import pytest
from pydantic import ValidationError

from schemas import MockInterviewRequestSchema


def test_mock_interview_schema_accepts_current_frontend_payload():
    payload = {
        "category": "Computer",
        "level": "beginner",
        "message": "yes",
        "history": [
            {
                "role": "ai",
                "content": "Hi! Are you ready to begin?",
            }
        ],
    }

    schema = MockInterviewRequestSchema(**payload)

    assert schema.message == "yes"
    assert schema.question_count is None


def test_mock_interview_schema_tolerates_deprecated_question_count():
    payload = {
        "category": "Computer",
        "level": "beginner",
        "message": "yes",
        "history": [],
        "question_count": 0,
    }

    schema = MockInterviewRequestSchema(**payload)

    assert schema.question_count == 0


def test_mock_interview_schema_still_rejects_unknown_fields():
    payload = {
        "category": "Computer",
        "level": "beginner",
        "message": "yes",
        "history": [],
        "unexpected": True,
    }

    with pytest.raises(ValidationError):
        MockInterviewRequestSchema(**payload)


@pytest.fixture()
def mock_interview_client(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'test-secret')
    monkeypatch.setenv('MONGODB_URL', '')
    monkeypatch.setenv('MONGODB_URI', '')

    from main import create_app
    import routes.interview
    import services.interview_ai

    app = create_app()
    app.testing = True
    app.config['RATELIMIT_ENABLED'] = False

    monkeypatch.setattr(routes.interview, "mongo_db", None)
    monkeypatch.setattr(
        services.interview_ai,
        "conduct_mock_interview",
        lambda category, level, message, history: "Great, let's begin. What is your strongest technical skill?",
    )

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_csrf_token'] = 'mock_tok'
            sess['user_id'] = 'test_user'
            sess['username'] = 'srajan'
        yield client


@pytest.mark.parametrize("extra_payload", [{}, {"question_count": 0}])
def test_mock_interview_yes_turn_continues_flow(mock_interview_client, extra_payload):
    payload = {
        "category": "Computer",
        "level": "beginner",
        "message": "yes",
        "history": [
            {
                "role": "ai",
                "content": "Hi! Are you ready to begin?",
            }
        ],
        **extra_payload,
    }

    response = mock_interview_client.post(
        '/api/mock-interview',
        json=payload,
        headers={'X-CSRF-Token': 'mock_tok'},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["isQuestion"] is True
