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


def test_mock_interview_schema_accepts_question_count():
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
        lambda category, level, message, history, answers_completed=0, max_answers=10, **kwargs: "Great, let's begin. What is your strongest technical skill?",
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
    assert data["isComplete"] is False
    assert data["answersCompleted"] == 1
    assert data["maxAnswers"] == 10


def test_mock_interview_category_normalization(mock_interview_client):
    # Test that &amp; and lowercase values are correctly normalized and accepted by /api/mock-interview
    payload = {
        "category": "aerospace &amp; aviation",  # Lowercase and containing entity
        "level": "beginner",
        "message": "yes",
        "history": [
            {
                "role": "ai",
                "content": "Hi! Are you ready to begin?",
            }
        ]
    }

    response = mock_interview_client.post(
        '/api/mock-interview',
        json=payload,
        headers={'X-CSRF-Token': 'mock_tok'},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True


def test_mock_interview_final_answer_completes_without_new_question(mock_interview_client, monkeypatch):
    import services.interview_ai

    monkeypatch.setattr(
        services.interview_ai,
        "conduct_mock_interview",
        lambda *args, **kwargs: pytest.fail("conduct_mock_interview should not run after 10 answers"),
    )
    monkeypatch.setattr(
        services.interview_ai,
        "generate_mock_interview_report",
        lambda category, level, history: {
            "overall_score": 82,
            "detailed_evaluation": "Strong completion.",
            "good_parts": ["Clear answers"],
            "bad_parts": [],
            "improvement_tips": ["Keep practicing"],
        },
    )

    history = []
    for i in range(1, 10):
        history.append({"role": "ai", "content": f"Question {i}?"})
        history.append({"role": "user", "content": f"Answer {i}."})

    payload = {
        "category": "Computer",
        "level": "beginner",
        "message": "Answer 10.",
        "history": history,
    }

    response = mock_interview_client.post(
        '/api/mock-interview',
        json=payload,
        headers={'X-CSRF-Token': 'mock_tok'},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["isComplete"] is True
    assert data["answersCompleted"] == 10
    assert data["maxAnswers"] == 10
    assert data["reply"]["overall_score"] == 82


def test_count_user_answers_with_message():
    from services.interview_ai import count_user_answers, count_user_answers_with_message

    history = [
        {"role": "ai", "content": "Ready?"},
        {"role": "user", "content": "Yes"},
    ]
    assert count_user_answers(history) == 1
    assert count_user_answers_with_message(history, "Second answer") == 2
    assert count_user_answers_with_message(history + [{"role": "user", "content": "Second answer"}], "Second answer") == 2


def test_count_user_answers_caps_at_ten():
    from services.interview_ai import count_user_answers_with_message

    history = []
    for i in range(12):
        history.append({"role": "user", "content": f"Answer {i}"})
    assert count_user_answers_with_message(history, "") == 10


def test_mock_interview_replaces_early_ai_summary(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "That's the end of our mock interview. Here's a brief summary of your "
            "performance: you did well and should keep practicing."
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "code reusability",
        [],
        answers_completed=7,
        max_answers=10,
    )

    assert reply.endswith("?")
    assert "summary" not in reply.lower()
    assert "performance" not in reply.lower()
    assert "mock interview" not in reply.lower()


def test_mock_interview_keeps_acknowledgement_and_strips_numbering(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "Good answer — you explained that clearly. What is an API and why is it useful?"
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "code reusability",
        [],
        answers_completed=7,
        max_answers=10,
    )

    assert reply.startswith("Good answer")
    assert reply.endswith("?")
    assert "What is an API and why is it useful?" in reply


def test_mock_interview_keeps_brief_feedback_before_question(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "That's correct, you've listed some of the basic data types. "
            "What is the purpose of functions in programming?"
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "int, float, string",
        [],
        answers_completed=3,
        max_answers=10,
    )

    assert "That's correct" in reply
    assert reply.endswith("What is the purpose of functions in programming?")


def test_mock_interview_strips_parenthetical_meta_and_blocks_summary(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "That's correct. What is a variable? "
            "(This is the 10th question, after this I will provide a summary of your performance)"
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "a named storage location",
        [],
        answers_completed=4,
        max_answers=10,
    )

    assert "That's correct." in reply
    assert reply.endswith("What is a variable?")
    assert "10th question" not in reply.lower()
    assert "summary" not in reply.lower()
    from schemas import MockInterviewReportRequestSchema
    payload = {
        "category": "Computer",
        "level": "beginner",
        "history": [
            {"role": "ai", "content": "Hi! Are you ready to begin?"},
            {"role": "user", "content": "Yes, I am."}
        ]
    }
    schema = MockInterviewReportRequestSchema(**payload)
    assert schema.category == "Computer"
    assert schema.level == "beginner"
    assert len(schema.history) == 2


def test_mock_interview_keeps_two_sentence_feedback(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "That's a solid start. You identified the main idea correctly. "
            "What is the purpose of functions in programming?"
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "int, float, string",
        [],
        answers_completed=3,
        max_answers=10,
    )

    feedback, question = reply.split("\n\n", 1)
    assert "That's a solid start." in feedback
    assert "You identified the main idea correctly." in feedback
    assert question.endswith("?")


def test_mock_interview_enforces_feedback_and_reply_word_limits(monkeypatch):
    import services.interview_ai as interview_ai

    monkeypatch.setattr(
        interview_ai.gemini_client,
        "chat",
        lambda *args, **kwargs: (
            "That's correct, you've listed some of the basic data types and explained them "
            "in great detail with multiple examples from your personal experience. "
            "What is the purpose of functions in programming?"
        ),
    )
    monkeypatch.setattr(interview_ai.groq_client, "chat", lambda *args, **kwargs: None)

    reply = interview_ai.conduct_mock_interview(
        "Computer",
        "beginner",
        "int, float, string",
        [],
        answers_completed=3,
        max_answers=10,
    )

    feedback, question = reply.split("\n\n", 1)
    assert len(feedback.split()) <= interview_ai.MOCK_FEEDBACK_MAX_WORDS
    assert len(reply.split()) <= interview_ai.MOCK_REPLY_MAX_WORDS
    assert question.endswith("?")


def test_mock_interview_report_endpoint(mock_interview_client, monkeypatch):
    import services.interview_ai

    # Mock the report generator
    monkeypatch.setattr(
        services.interview_ai,
        "generate_mock_interview_report",
        lambda category, level, history: {
            "overall_score": 85,
            "detailed_evaluation": "Good job.",
            "good_parts": ["Part A"],
            "bad_parts": ["Part B"],
            "improvement_tips": ["Tip C"]
        }
    )

    payload = {
        "category": "Computer",
        "level": "beginner",
        "history": [
            {"role": "ai", "content": "Hi! Are you ready to begin?"},
            {"role": "user", "content": "Yes, I am."}
        ]
    }

    response = mock_interview_client.post(
        '/api/mock-interview/report',
        json=payload,
        headers={'X-CSRF-Token': 'mock_tok'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["report"]["overall_score"] == 85
    assert data["report"]["detailed_evaluation"] == "Good job."
