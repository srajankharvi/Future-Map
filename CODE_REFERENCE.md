# Implementation Code Reference

## Backend Implementation

### 1. count_user_answers() Function

**Location:** `services/interview_ai.py` (lines 15-37)

```python
def count_user_answers(history):
    """
    Count the number of user answers in the interview history.
    
    Only counts items where:
    - role == "user"
    - content is non-empty after stripping whitespace
    
    Args:
        history: List of message dicts with 'role' and 'content' keys
        
    Returns:
        int: Count of user answers, capped at 10
    """
    count = 0
    for item in history:
        if not isinstance(item, dict):
            continue
        if item.get("role") == "user":
            content = str(item.get("content", "")).strip()
            if content:
                count += 1
    return min(count, 10)
```

### 2. Updated /api/mock-interview Endpoint

**Location:** `routes/interview.py` (lines 270-381)

Key logic:
```python
# --- Count user answers instead of AI questions ---
from services.interview_ai import conduct_mock_interview, count_user_answers, generate_mock_interview_report

user_answer_count = count_user_answers(history)

# Determine if interview is complete (user has submitted 10 answers)
is_complete = user_answer_count >= MAX_MOCK_QUESTIONS

if is_complete:
    # Generate final report
    report = generate_mock_interview_report(category, level, history)
    if not report:
        report = {
            "overall_score": 75,
            "detailed_evaluation": "Thank you for completing the mock interview.",
            "good_parts": ["Participated in the interview."],
            "bad_parts": [],
            "improvement_tips": ["Continue practicing interviews."]
        }
    
    return jsonify({
        'success': True,
        'reply': report,
        'isComplete': True,
        'answersCompleted': user_answer_count,
        'maxAnswers': MAX_MOCK_QUESTIONS
    }), 200

# Interview in progress - get next AI response
reply = conduct_mock_interview(
    category,
    level,
    message,
    history,
    question_count=user_answer_count,
    max_questions=MAX_MOCK_QUESTIONS
)

# Check if reply contains a question
is_question = '?' in reply

return jsonify({
    'success': True,
    'reply': reply,
    'isQuestion': is_question,
    'isComplete': False,
    'answersCompleted': user_answer_count,
    'maxAnswers': MAX_MOCK_QUESTIONS
}), 200
```

## Frontend Implementation

### 1. Variable Declaration

**Location:** `frontend/js/interview.js` (lines 96-106)

```javascript
// ==================== MOCK INTERVIEW ====================

let mockMessages = [];
let mockAnswerCount = 0;  // Track user answers, not AI questions
let mockInterviewReport = null;  // Store report when received from backend
const MAX_MOCK_QUESTIONS = 10;
let isMockActive = false;
let mockSelectedLevel = 'beginner';
let mockPendingIntegrityNotice = '';
let lastMockIntegrityNotice = '';
let lastMockIntegrityNoticeAt = 0;
let lastMockTabViolationAt = 0;
```

### 2. Progress Display Function

**Location:** `frontend/js/interview.js` (around line 640)

```javascript
function updateChatACount() {
    const countEl = document.getElementById('chatQCount');
    if (countEl) {
        countEl.textContent = `Answer ${mockAnswerCount}/${MAX_MOCK_QUESTIONS}`;
    }
}
```

### 3. Send Message Handler

**Location:** `frontend/js/interview.js` (lines 443-524)

```javascript
async function sendMockMessage() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMessageBtn');
    const text = input.value.trim();

    if (!text || !isMockActive) return;

    // Capture current history BEFORE adding new message
    const currentHistory = [...mockMessages];

    // Add user message to UI and history
    addChatMessage('user', text);

    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;
    input.disabled = true;

    // Show loading
    showElement(document.getElementById('chatLoading'));

    try {
        const category = document.getElementById('mockCategory').value;
        const level = mockSelectedLevel;

        const response = await apiFetch(`${API_BASE}/mock-interview`, {
            method: 'POST',
            body: JSON.stringify({
                category,
                level,
                message: text,
                history: currentHistory
                // NOTE: question_count parameter removed
            })
        });

        if (!isMockActive) return;

        if (response.success) {
            // Update answer count from backend
            if (response.answersCompleted !== undefined) {
                mockAnswerCount = response.answersCompleted;
            }

            // Check if interview is complete (10 answers submitted)
            if (response.isComplete) {
                // Response contains the report object
                displayMockInterviewReport(response.reply);
                completeMockInterview(input, sendBtn);
                return;
            }

            // Interview in progress - add AI response (next question)
            if (typeof response.reply === 'string') {
                addChatMessage('ai', response.reply);
            }

            // Update progress display
            updateChatACount();
        } else {
            console.warn('Mock interview request failed:', {
                status: response.status,
                error: response.error
            });
            addChatMessage('ai', "I'm sorry, " + (response.error || "I encountered an error. Please try again."));
        }
    } catch (err) {
        if (isMockActive) {
            addChatMessage('ai', "Network error. Please check your connection.");
        }
        console.error('Mock interview error:', err);
    } finally {
        hideElement(document.getElementById('chatLoading'));

        // Re-enable inputs only if interview is still active
        if (isMockActive) {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }
}
```

### 4. Interview Completion Handler

**Location:** `frontend/js/interview.js` (lines 526-558)

```javascript
function completeMockInterview(input, sendBtn) {
    isMockActive = false;

    // Keep input disabled after interview ends
    input.disabled = true;
    sendBtn.disabled = true;

    // Show report after a brief pause
    setTimeout(() => {
        const chatbox = document.getElementById('mockChatbox');
        const loading = document.getElementById('mockReportLoading');
        const reportPanel = document.getElementById('mockReport');

        if (mockInterviewReport) {
            // Report was received from backend, display it
            renderPerformanceReport(mockInterviewReport, 
                document.getElementById('mockCategory').value, 
                mockSelectedLevel);
            hideElement(chatbox);
            hideElement(loading);
            showElement(reportPanel);

            // Scroll to report view
            setTimeout(() => {
                reportPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        } else {
            // Fallback: try to fetch report (shouldn't happen with new flow)
            generatePerformanceReport();
        }
    }, 1500);
}
```

### 5. Report Caching Function

**Location:** `frontend/js/interview.js` (lines 560-564)

```javascript
function displayMockInterviewReport(report) {
    // Report object is already received from backend
    // Store it for display
    mockInterviewReport = report;
}
```

### 6. Interview Initialization

**Location:** `frontend/js/interview.js` (lines 320-335)

```javascript
// UI transitions
document.getElementById('mockSetup').classList.add('hidden');
document.getElementById('mockChatbox').classList.remove('hidden');
hideElement(document.getElementById('mockReport'));
hideElement(document.getElementById('mockReportLoading'));
const oldRibbon = document.getElementById('chatReviewRibbon');
if (oldRibbon) oldRibbon.remove();
document.querySelector('.mock-interview-container').classList.add('chat-active');

document.getElementById('chatTitle').textContent = `Interview: ${category}`;
document.getElementById('chatQCount').textContent = `Answer 1/${MAX_MOCK_QUESTIONS}`;

isMockActive = true;
mockAnswerCount = 0;  // Track user answers, not questions
mockInterviewReport = null;  // Reset report
mockMessages = [];
mockPendingIntegrityNotice = '';
lastMockTabViolationAt = 0;
removeMockIntegrityWarnings();
```

## Example API Exchanges

### Exchange 1: First Answer (Answer 1/10)

**Request:**
```json
{
  "category": "Computer",
  "level": "intermediate",
  "message": "Yes, I'm ready to begin!",
  "history": [
    {
      "role": "ai",
      "content": "Hi! I'm your AI interviewer today..."
    },
    {
      "role": "user",
      "content": "Yes, I'm ready to begin!"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "reply": "Great! Let's start with a fundamental question. Can you explain what object-oriented programming is and give an example?",
  "isQuestion": true,
  "isComplete": false,
  "answersCompleted": 1,
  "maxAnswers": 10
}
```

**Frontend Update:**
```
Display: "Answer 1/10"
Show AI Question
```

### Exchange 10: Final Answer (Answer 10/10)

**Request:**
```json
{
  "category": "Computer",
  "level": "intermediate", 
  "message": "I've learned a lot about design patterns throughout my career...",
  "history": [
    ... (previous 19 messages)
    {
      "role": "user",
      "content": "I've learned a lot about design patterns throughout my career..."
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "reply": {
    "overall_score": 82,
    "detailed_evaluation": "You demonstrated strong knowledge of computer fundamentals...",
    "good_parts": [
      "Clear explanation of OOP concepts",
      "Good understanding of design patterns",
      "Practical examples with project work"
    ],
    "bad_parts": [
      "Could expand more on advanced concepts",
      "Some answers were shorter than expected"
    ],
    "improvement_tips": [
      "Practice explaining complex topics more thoroughly",
      "Study advanced design patterns in depth",
      "Review system design principles"
    ]
  },
  "isComplete": true,
  "answersCompleted": 10,
  "maxAnswers": 10
}
```

**Frontend Update:**
```
Display: "Answer 10/10"
Show Report Directly
Disable Input
```

## Key Differences from Old System

| Aspect | Old System | New System |
|--------|-----------|-----------|
| Progress Tracking | Tracks AI question numbers | Counts user answers |
| API Parameter | `question_count` sent/received | `answersCompleted` received |
| Interview Completion | After 10 AI questions | After 10 user answers |
| Report Delivery | Separate API call to `/api/mock-interview/report` | Included in final response |
| Report Fetch | Potential for separate failure | Always included with main response |
| UI Display | "Question X/10" | "Answer X/10" |
| Termination Risk | AI could wrap up early | Only when count reaches 10 |

