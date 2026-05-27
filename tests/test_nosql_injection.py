import os
import importlib
import importlib.util
import sys
import pytest

# Ensure we don't accidentally connect to a real MongoDB during tests
os.environ.pop('MONGODB_URL', None)
os.environ.pop('MONGODB_URI', None)

# Import the application factory by file path to avoid PYTHONPATH issues
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
main_path = os.path.join(project_root, 'main.py')
spec = importlib.util.spec_from_file_location('main', main_path)
main = importlib.util.module_from_spec(spec)
sys.modules['main'] = main
sys.path.insert(0, project_root)
spec.loader.exec_module(main)
app = main.create_app()
app.testing = True

from werkzeug.security import generate_password_hash


class FakeResult:
    def __init__(self, inserted_id=None, deleted_count=0):
        self.inserted_id = inserted_id
        self.deleted_count = deleted_count


class FakeCursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, *args, **kwargs):
        return self

    def skip(self, n):
        return self

    def limit(self, n):
        return self

    def __iter__(self):
        return iter(self.docs)

    def __len__(self):
        return len(self.docs)


class FakeCollection:
    def __init__(self):
        self.docs = []
        self.last_insert = None
        self.last_update = None
        self.last_delete = None

    def find_one(self, query=None, projection=None):
        # Return a known user when username == 'existing_user'
        if query and isinstance(query, dict):
            username = query.get('username')
            if username == 'existing_user':
                return {
                    '_id': 'fakeid',
                    'username': 'existing_user',
                    'email': 'e@e.com',
                    'password_hash': generate_password_hash('password')
                }
        return None

    def insert_one(self, doc):
        self.docs.append(doc.copy())
        self.last_insert = doc.copy()
        return FakeResult(inserted_id='fakeid')

    def update_one(self, filter, update, upsert=False):
        self.last_update = (filter, update, upsert)
        return FakeResult()

    def delete_one(self, filter):
        self.last_delete = filter
        class R:
            deleted_count = 1

        return R()

    def find(self, *args, **kwargs):
        return FakeCursor(self.docs.copy())

    def insert_many(self, docs):
        for d in docs:
            self.insert_one(d)
        return FakeResult(inserted_id='many')

    def delete_many(self, q):
        self.docs = []
        return FakeResult()


class FakeMongo:
    def __init__(self):
        self.users = FakeCollection()
        self.user_profiles = FakeCollection()
        self.login_attempts = FakeCollection()
        self.projects = FakeCollection()
        self.roadmaps = FakeCollection()
        self.careers = FakeCollection()
        self.courses = FakeCollection()
        self.interview_questions = FakeCollection()


fake_mongo = FakeMongo()


def patch_routes_mongo(fake):
    import database
    database.mongo_db = fake
    for name, module in list(sys.modules.items()):
        if name.startswith('routes') and hasattr(module, 'mongo_db'):
            setattr(module, 'mongo_db', fake)


@pytest.fixture(autouse=True)
def client():
    # Patch route modules before each test to ensure DB calls go to our fake
    patch_routes_mongo(fake_mongo)
    with app.test_client() as client:
        yield client


def test_login_nosql_injection(client):
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'login_tok'
    resp = client.post('/api/auth/login', json={"username": {"$ne": ""}, "password": "x"}, headers={'X-CSRF-Token': 'login_tok'})
    assert resp.status_code in (400, 401)
    data = resp.get_json()
    assert data is not None and data.get('success') is False


def test_register_nosql_injection(client):
    payload = {
        "username": {"$ne": ""},
        "email": "attacker@example.com",
        "password": "Password1!",
        "confirm_password": "Password1!",
        "full_name": "Attacker"
    }
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'reg_tok'
    resp = client.post('/api/auth/register', json=payload, headers={'X-CSRF-Token': 'reg_tok'})
    # Validation should fail (400) or DB duplicate (409), but never succeed
    assert resp.status_code in (400, 409)
    data = resp.get_json()
    assert data is not None and data.get('success') is False


def test_update_profile_operator_key_not_applied(client):
    # Prepare session with CSRF token
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'tok'
        sess['user_id'] = 'fakeid'
        sess['username'] = 'testuser'
        sess['email'] = 't@test.com'

    # Payload with top-level operator key should be rejected by schema
    resp = client.put('/api/auth/update-profile', json={"$set": {"is_admin": True}}, headers={'X-CSRF-Token': 'tok'})
    assert resp.status_code == 400
    # Ensure no DB update occurred
    import routes.auth
    assert routes.auth.mongo_db.user_profiles.last_update is None


def test_create_project_malicious_title_serialized_to_string(client):
    # Prepare session and CSRF
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'tok2'
        sess['user_id'] = 'fakeid'
        sess['username'] = 'project_user'
        sess['email'] = 'p@example.com'
    payload = {
        "title": {"$ne": ""},
        "link": "http://example.com",
        "description": "A sample project"
    }
    resp = client.post('/api/projects', json=payload, headers={'X-CSRF-Token': 'tok2'})
    # With strict schemas, the dict title should be rejected
    assert resp.status_code == 400
    import routes.projects
    assert getattr(routes.projects.mongo_db.projects, 'last_insert', None) is None


def test_register_rejects_extra_field(client):
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'reg_extra_tok'
    payload = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "Password1!",
        "confirm_password": "Password1!",
        "full_name": "New User",
        "unexpected": "value"
    }
    resp = client.post('/api/auth/register', json=payload, headers={'X-CSRF-Token': 'reg_extra_tok'})
    assert resp.status_code == 400


def test_update_profile_rejects_extra_field(client):
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'tok3'
        sess['user_id'] = 'fakeid'
        sess['username'] = 'testuser'
        sess['email'] = 't@test.com'

    resp = client.put('/api/auth/update-profile', json={"bio": "hey", "unexpected": "x"}, headers={'X-CSRF-Token': 'tok3'})
    assert resp.status_code == 400


def test_create_project_rejects_extra_field(client):
    with client.session_transaction() as sess:
        sess['_csrf_token'] = 'tok4'
        sess['user_id'] = 'fakeid'
        sess['username'] = 'project_user'
        sess['email'] = 'p@example.com'
    payload = {
        "title": "My Project",
        "link": "http://example.com",
        "description": "A sample project",
        "unexpected": "nope"
    }
    resp = client.post('/api/projects', json=payload, headers={'X-CSRF-Token': 'tok4'})
    assert resp.status_code == 400
