# AI Mock Interview System Refactor - User Answer Tracking

## Overview
The mock interview system has been refactored to track **user answers** instead of AI-generated question numbers. This ensures interviews end only after the user submits 10 complete answers, preventing premature termination when AI models attempt to wrap up early.

## Key Changes

### 1. Backend: Answer Counting Function
**File:** `services/interview_ai.py`

Added `count_user_answers(history)` function:
```python
def count_user_answers(history):
    """
    Count the number of user answers in the interview history.
    
    Only counts items where:
    - role == "user"
    - content is non-empty after stripping whitespace
    
    Returns: int (count of user answers, capped at 10)
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

### 2. Backend: API Endpoint Update
**File:** `routes/interview.py` → `/api/mock-interview` endpoint

**Key changes:**
- Removed reliance on `question_count` parameter
- Uses `count_user_answers(history)` to determine progress
- Checks if `user_answer_count >= 10` to trigger completion
- When interview completes:
  - Calls `generate_mock_interview_report()` immediately
  - Returns report object directly with `isComplete: true`
- Returns new response fields:
  ```json
  {
    "success": true,
    "reply": "...", 
    "isQuestion": true,
    "isComplete": false,
    "answersCompleted": 3,
    "maxAnswers": 10
  }
  ```

**Response when interview completes (after 10th answer):**
```json
{
  "success": true,
  "reply": { "overall_score": 85, "detailed_evaluation": "...", ... },
  "isComplete": true,
  "answersCompleted": 10,
  "maxAnswers": 10
}
```

### 3. Frontend: UI Updates
**File:** `frontend/js/interview.js`

**Variable changes:**
- `mockQuestionCount` → `mockAnswerCount` (now tracks user submissions)
- Added `mockInterviewReport` to cache report from backend

**Function updates:**

#### `updateChatACount()`
Changed from: `Question X/10` 
To: `Answer X/10`

#### `sendMockMessage()`
- Removed `question_count` from API request
- Extracts `answersCompleted` from backend response
- Updates progress: `mockAnswerCount = response.answersCompleted`
- Checks `response.isComplete` flag instead of counting questions
- When interview complete:
  - Receives report in `response.reply`
  - Calls `displayMockInterviewReport()` to cache it
  - Calls `completeMockInterview()` to transition UI

#### `completeMockInterview()`
- Now displays cached report instead of fetching it
- No longer makes secondary API call to `/api/mock-interview/report`
- Uses `renderPerformanceReport()` to display the report

#### `displayMockInterviewReport(report)`
New function that caches the report object from backend.

#### Initialization
- `startMockInterview()`: Resets `mockAnswerCount = 0` and `mockInterviewReport = null`
- `clearMockInterviewState()`: Clears interview state including report

## Interview Flow Diagram

```
User Answer 1
    ↓
[Send to /api/mock-interview]
    ↓
Backend counts: 1 user answer < 10
    ↓
Returns next AI question + answersCompleted: 1
    ↓
Frontend shows "Answer 1/10" + AI question
    ↓
User Answer 2
    ...
    ↓
User Answer 10 (final)
    ↓
[Send to /api/mock-interview]
    ↓
Backend counts: 10 user answers >= 10
    ↓
Backend calls generate_mock_interview_report()
    ↓
Returns report + isComplete: true + answersCompleted: 10
    ↓
Frontend displays report directly
    ↓
Interview complete!
```

## Benefits

1. **Interview Integrity**: Cannot end before 10 answers are submitted
2. **AI-Independent**: Never relies on AI to decide interview termination
3. **Single Report Fetch**: Report generated server-side, no extra API call
4. **Clear Progress**: User always knows "Answer X/10"
5. **Cleaner UX**: Immediate report display without loading spinner

## API Response Changes

### Before (Old System)
- Tracked `question_count` and `questionsAsked`
- Called `/api/mock-interview/report` separately for report
- Report fetch could fail independently

### After (New System)
- Tracks `answersCompleted` and `maxAnswers`
- Report included directly in final response
- Single source of truth for interview completion

## Testing Checklist

- [ ] User can start mock interview
- [ ] Progress displays "Answer 1/10" → "Answer 10/10"
- [ ] Interview continues through all 10 answers
- [ ] Report displays after 10th answer submission
- [ ] Report shows correct performance data
- [ ] Reset button clears state properly
- [ ] Integrity guards still function (no copy/paste, tab switching)
- [ ] Mobile experience works correctly

## Backward Compatibility

This change removes the `question_count` parameter requirement from the frontend, making API calls simpler. Old clients using `question_count` will continue to work as the backend gracefully ignores unknown parameters.
