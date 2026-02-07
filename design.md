# Design Document: Goal Detector

## Overview

Goal Detector is a session-based web application that guides users through a reflective questionnaire and generates personalized learning/career roadmaps using AI analysis. The system follows a linear flow: questionnaire → analysis → roadmap presentation. All data exists only in memory during the session, ensuring privacy. The application emphasizes encouragement and beginner-friendly language throughout the user experience.

**Key Design Principles:**
- Privacy-first: No data persistence beyond the session
- Simplicity: Linear flow with clear progression
- Encouragement: Positive reinforcement at every stage
- Accessibility: Beginner-friendly language and interface

## Architecture

The application follows a client-server architecture with three main layers:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (UI Components, State Management)      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (Questionnaire Logic, Session Mgmt)    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         AI Analysis Layer               │
│  (Response Processing, Roadmap Gen)     │
└─────────────────────────────────────────┘
```

**Layer Responsibilities:**

1. **Presentation Layer**: Renders UI, handles user input, displays progress and results
2. **Application Layer**: Manages questionnaire flow, validates responses, maintains session state
3. **AI Analysis Layer**: Processes responses, identifies themes, generates personalized roadmaps

**Data Flow:**
1. User starts session → Initialize empty session state
2. User answers questions → Responses stored in session state
3. Questionnaire complete → Responses sent to AI analyzer
4. AI generates roadmap → Roadmap displayed to user
5. Session ends → All data discarded

## Components and Interfaces

### 1. Session Manager

**Responsibility:** Manages the lifecycle of a user session and maintains state.

**Interface:**
```
SessionManager {
  startSession() → SessionId
  getSessionState(sessionId: SessionId) → SessionState
  updateSessionState(sessionId: SessionId, state: SessionState) → void
  endSession(sessionId: SessionId) → void
}
```

**Behavior:**
- Creates new session with unique identifier
- Stores session state in memory (no persistence)
- Provides access to current session state
- Cleans up session data on end

### 2. Questionnaire Controller

**Responsibility:** Manages questionnaire flow and response collection.

**Interface:**
```
QuestionnaireController {
  getCurrentQuestion(sessionId: SessionId) → Question
  submitResponse(sessionId: SessionId, response: Response) → ValidationResult
  getProgress(sessionId: SessionId) → Progress
  isComplete(sessionId: SessionId) → boolean
  getAllResponses(sessionId: SessionId) → Response[]
}
```

**Behavior:**
- Tracks current question index
- Validates responses before acceptance
- Advances to next question on valid submission
- Provides progress information
- Determines when questionnaire is complete

### 3. Response Validator

**Responsibility:** Validates user responses according to defined rules.

**Interface:**
```
ResponseValidator {
  validate(response: Response) → ValidationResult
  isEmpty(response: Response) → boolean
  isValidLength(response: Response) → boolean
}
```

**Validation Rules:**
- Response must not be empty (after trimming whitespace)
- Response must be within reasonable length (e.g., 1-1000 characters)
- Response must contain valid characters

### 4. AI Analyzer

**Responsibility:** Processes user responses and generates personalized recommendations.

**Interface:**
```
AIAnalyzer {
  analyzeResponses(responses: Response[]) → AnalysisResult
  identifyThemes(responses: Response[]) → Theme[]
  assessMotivation(responses: Response[]) → MotivationLevel
  extractConstraints(responses: Response[]) → Constraints
}
```

**Analysis Process:**
1. Parse all responses to extract key information
2. Identify recurring themes and interests
3. Assess time constraints and commitment level
4. Evaluate current skill level and experience
5. Determine motivation and desired outcomes

### 5. Roadmap Generator

**Responsibility:** Creates structured, personalized roadmaps from analysis results.

**Interface:**
```
RoadmapGenerator {
  generateRoadmap(analysis: AnalysisResult) → Roadmap
  createSteps(themes: Theme[], constraints: Constraints) → Step[]
  addEncouragement(roadmap: Roadmap) → Roadmap
  formatForDisplay(roadmap: Roadmap) → FormattedRoadmap
}
```

**Generation Process:**
1. Create logical sequence of steps based on themes
2. Adjust complexity based on skill level
3. Consider time constraints in step sizing
4. Add encouraging messages and positive framing
5. Format for readability

### 6. UI Renderer

**Responsibility:** Renders user interface components and handles user interactions.

**Interface:**
```
UIRenderer {
  renderQuestion(question: Question, progress: Progress) → void
  renderError(error: Error) → void
  renderLoadingState() → void
  renderRoadmap(roadmap: FormattedRoadmap) → void
  captureUserInput() → string
}
```

**UI States:**
- Question display with progress indicator
- Loading state during AI analysis
- Roadmap display with formatted content
- Error display with recovery options

## Data Models

### Question
```
Question {
  id: string
  text: string
  category: QuestionCategory
  order: number
}

QuestionCategory = "interests" | "goals" | "constraints" | "skills" | "motivation"
```

### Response
```
Response {
  questionId: string
  text: string
  timestamp: Date
}
```

### SessionState
```
SessionState {
  sessionId: string
  currentQuestionIndex: number
  responses: Response[]
  status: SessionStatus
  createdAt: Date
}

SessionStatus = "active" | "analyzing" | "complete" | "error"
```

### AnalysisResult
```
AnalysisResult {
  themes: Theme[]
  motivationLevel: MotivationLevel
  constraints: Constraints
  skillLevel: SkillLevel
  recommendations: string[]
}

Theme {
  name: string
  confidence: number
  relatedResponses: string[]
}

MotivationLevel = "high" | "moderate" | "exploratory"

Constraints {
  timeAvailable: string
  commitmentLevel: string
  startDate: string
}

SkillLevel = "beginner" | "intermediate" | "advanced"
```

### Roadmap
```
Roadmap {
  title: string
  introduction: string
  steps: Step[]
  encouragement: string[]
  disclaimer: string
}

Step {
  order: number
  title: string
  description: string
  estimatedTime: string
  resources: string[]
}
```

### ValidationResult
```
ValidationResult {
  isValid: boolean
  errors: string[]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Response Validation Consistency
*For any* string input, the validation result should correctly identify whether it is non-empty (after trimming whitespace) and within acceptable length bounds.

**Validates: Requirements 1.2, 2.1**

### Property 2: Question Progression
*For any* valid response submitted at any question position (except the last), the system should advance to the next sequential question.

**Validates: Requirements 1.3**

### Property 3: Progress Calculation Accuracy
*For any* question position in the questionnaire, the progress indicator should accurately reflect the percentage of completion (current position / total questions).

**Validates: Requirements 1.5**

### Property 4: Response Storage Round-Trip
*For any* valid response submitted to the system, retrieving the responses from the session should include that exact response with matching content and question ID.

**Validates: Requirements 2.3, 2.4**

### Property 5: Complete Response Processing
*For any* complete set of questionnaire responses, the AI analyzer should receive and process all responses without omission.

**Validates: Requirements 3.1**

### Property 6: Recommendation Generation
*For any* valid analysis result, the roadmap generator should produce a non-empty set of recommendations.

**Validates: Requirements 3.5**

### Property 7: Roadmap Structure Integrity
*For any* generated roadmap, the steps should have sequential order numbers starting from 1 with no gaps, and the roadmap should contain all required fields (title, introduction, steps, encouragement, disclaimer).

**Validates: Requirements 4.1, 4.2**

### Property 8: Encouragement Presence
*For any* generated roadmap, the encouragement field should be non-empty and contain at least one positive reinforcement message.

**Validates: Requirements 5.1**

### Property 9: Session Isolation
*For any* two sessions created sequentially, ending the first session and starting a second session should result in the second session having no access to the first session's data, and the second session should start with clean/empty state.

**Validates: Requirements 6.1, 6.2, 6.5**

### Property 10: Error State Preservation
*For any* session state and any error that occurs during processing, if the error is recoverable, the session state should remain unchanged from its pre-error state.

**Validates: Requirements 9.3**

### Property 11: Error Message Safety
*For any* error that occurs in the system, the user-facing error message should not contain technical implementation details such as stack traces, file paths, or internal variable names.

**Validates: Requirements 9.4**

## Error Handling

The system implements a layered error handling strategy:

### Error Categories

1. **Validation Errors**: User input that doesn't meet requirements
   - Empty responses
   - Responses exceeding length limits
   - Invalid characters
   - **Handling**: Display friendly prompt, allow retry, maintain session state

2. **AI Analysis Errors**: Failures in the AI processing layer
   - API timeouts
   - Service unavailability
   - Invalid responses from AI service
   - **Handling**: Display user-friendly error, offer retry option, log technical details

3. **Network Errors**: Connectivity issues
   - Connection timeout
   - DNS resolution failure
   - Service unreachable
   - **Handling**: Inform user of connectivity issue, suggest retry, maintain session state

4. **System Errors**: Unexpected application errors
   - Null reference errors
   - Unexpected state transitions
   - Memory issues
   - **Handling**: Log error details, display generic error message, provide restart instructions

### Error Recovery Strategy

**Recoverable Errors** (validation, network, AI service):
- Preserve current session state
- Display specific, actionable error message
- Provide retry mechanism
- Log error for debugging

**Unrecoverable Errors** (system crashes, memory exhaustion):
- Log complete error details
- Display generic error message without technical details
- Provide clear restart instructions
- Clean up session resources

### Error Message Guidelines

- Use plain language, avoid technical jargon
- Be specific about what went wrong
- Provide actionable next steps
- Maintain encouraging tone even in errors
- Never expose stack traces, file paths, or internal details to users

## Testing Strategy

The Goal Detector application will employ a dual testing approach combining unit tests for specific scenarios and property-based tests for universal correctness properties.

### Testing Framework Selection

**Property-Based Testing Library**: 
- For JavaScript/TypeScript: **fast-check**
- For Python: **Hypothesis**

Each property test will run a minimum of 100 iterations to ensure comprehensive input coverage through randomization.

### Unit Testing Focus

Unit tests will verify:
- **Specific examples**: Concrete scenarios like application startup showing first question
- **Edge cases**: Empty input handling, boundary conditions
- **Integration points**: Component interactions and data flow
- **Error conditions**: Specific error scenarios and recovery

**Example Unit Tests**:
- Application initialization displays first question (Req 1.1)
- Empty response triggers helpful prompt (Req 2.2)
- Questionnaire completion triggers analysis (Req 1.4)
- UI displays one question at a time (Req 7.1)
- Loading indicator shown during analysis (Req 7.5)
- Disclaimer present in roadmap (Req 8.1)
- Questionnaire includes all required categories (Req 10.1-10.5)
- Specific error types produce appropriate messages (Req 9.1, 9.2, 9.5)

### Property-Based Testing Focus

Property tests will verify universal properties across all inputs:

**Property Test 1: Response Validation Consistency**
- **Tag**: Feature: goal-detector, Property 1: Response Validation Consistency
- **Test**: Generate random strings (empty, whitespace, valid, too long) and verify validation correctly identifies each category
- **Iterations**: 100+

**Property Test 2: Question Progression**
- **Tag**: Feature: goal-detector, Property 2: Question Progression
- **Test**: Generate random valid responses at various question positions, verify next question is displayed
- **Iterations**: 100+

**Property Test 3: Progress Calculation Accuracy**
- **Tag**: Feature: goal-detector, Property 3: Progress Calculation Accuracy
- **Test**: Generate random question positions, verify progress percentage is correct
- **Iterations**: 100+

**Property Test 4: Response Storage Round-Trip**
- **Tag**: Feature: goal-detector, Property 4: Response Storage Round-Trip
- **Test**: Generate random responses, submit them, verify all can be retrieved with exact content
- **Iterations**: 100+

**Property Test 5: Complete Response Processing**
- **Tag**: Feature: goal-detector, Property 5: Complete Response Processing
- **Test**: Generate random complete response sets, verify analyzer receives all responses
- **Iterations**: 100+

**Property Test 6: Recommendation Generation**
- **Tag**: Feature: goal-detector, Property 6: Recommendation Generation
- **Test**: Generate random analysis results, verify recommendations are non-empty
- **Iterations**: 100+

**Property Test 7: Roadmap Structure Integrity**
- **Tag**: Feature: goal-detector, Property 7: Roadmap Structure Integrity
- **Test**: Generate random roadmaps, verify sequential ordering and required fields
- **Iterations**: 100+

**Property Test 8: Encouragement Presence**
- **Tag**: Feature: goal-detector, Property 8: Encouragement Presence
- **Test**: Generate random roadmaps, verify encouragement field is non-empty
- **Iterations**: 100+

**Property Test 9: Session Isolation**
- **Tag**: Feature: goal-detector, Property 9: Session Isolation
- **Test**: Create random sessions with random data, verify no data leakage between sessions
- **Iterations**: 100+

**Property Test 10: Error State Preservation**
- **Tag**: Feature: goal-detector, Property 10: Error State Preservation
- **Test**: Generate random session states and recoverable errors, verify state unchanged
- **Iterations**: 100+

**Property Test 11: Error Message Safety**
- **Tag**: Feature: goal-detector, Property 11: Error Message Safety
- **Test**: Generate random errors, verify user messages contain no technical details
- **Iterations**: 100+

### Test Coverage Goals

- **Unit Test Coverage**: 80%+ of code paths
- **Property Test Coverage**: All correctness properties from design
- **Integration Tests**: Critical user flows (questionnaire → analysis → roadmap)
- **Error Scenarios**: All error categories with recovery paths

### Testing Best Practices

- Keep unit tests focused on single concerns
- Use property tests for comprehensive input coverage
- Mock AI service calls for deterministic testing
- Test error paths as thoroughly as happy paths
- Maintain fast test execution (< 5 seconds for full suite)
- Use descriptive test names that explain what is being verified
