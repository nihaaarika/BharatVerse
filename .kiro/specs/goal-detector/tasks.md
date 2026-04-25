# Implementation Plan: Goal Detector

## Overview

This implementation plan breaks down the Goal Detector application into discrete, incremental coding tasks. The application will be built using TypeScript for type safety and maintainability. Each task builds on previous work, with property-based tests integrated throughout to validate correctness early. The implementation follows a bottom-up approach: core data models → business logic → UI components → integration.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Initialize TypeScript project with appropriate configuration
  - Install fast-check for property-based testing
  - Install testing framework (Jest or Vitest)
  - Set up basic project structure (src/, tests/, types/)
  - _Requirements: Foundation for all requirements_

- [ ] 2. Implement core data models and types
  - [ ] 2.1 Create TypeScript interfaces for all data models
    - Define Question, Response, SessionState, AnalysisResult, Roadmap types
    - Define enums for QuestionCategory, SessionStatus, MotivationLevel, SkillLevel
    - _Requirements: 1.1, 2.3, 3.1, 4.1_
  
  - [ ]* 2.2 Write unit tests for type definitions
    - Test that types enforce correct structure
    - _Requirements: 1.1, 2.3, 3.1, 4.1_

- [ ] 3. Implement Response Validator
  - [ ] 3.1 Create ResponseValidator class with validation methods
    - Implement isEmpty() to check for empty/whitespace-only strings
    - Implement isValidLength() to check length bounds (1-1000 characters)
    - Implement validate() to return ValidationResult
    - _Requirements: 1.2, 2.1, 2.2_
  
  - [ ]* 3.2 Write property test for response validation
    - **Property 1: Response Validation Consistency**
    - **Validates: Requirements 1.2, 2.1**
    - Generate random strings (empty, whitespace, valid, too long)
    - Verify validation correctly identifies each category
  
  - [ ]* 3.3 Write unit tests for edge cases
    - Test empty string, whitespace-only strings
    - Test boundary lengths (0, 1, 1000, 1001 characters)
    - _Requirements: 1.2, 2.1, 2.2_

- [ ] 4. Implement Session Manager
  - [ ] 4.1 Create SessionManager class with session lifecycle methods
    - Implement startSession() to create new session with unique ID
    - Implement getSessionState() to retrieve current state
    - Implement updateSessionState() to modify state
    - Implement endSession() to clean up session data
    - Use in-memory Map for session storage
    - _Requirements: 6.1, 6.2, 6.5_
  
  - [ ]* 4.2 Write property test for session isolation
    - **Property 9: Session Isolation**
    - **Validates: Requirements 6.1, 6.2, 6.5**
    - Generate random sessions with random data
    - Verify no data leakage between sessions
    - Verify new sessions start with clean state
  
  - [ ]* 4.3 Write unit tests for session lifecycle
    - Test session creation, retrieval, update, deletion
    - Test that ended sessions cannot be retrieved
    - _Requirements: 6.1, 6.2, 6.5_

- [ ] 5. Implement Questionnaire Controller
  - [ ] 5.1 Create predefined question set
    - Define questions covering all required categories (interests, goals, constraints, skills, motivation)
    - Assign sequential order numbers to questions
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 5.2 Create QuestionnaireController class
    - Implement getCurrentQuestion() to get question by index
    - Implement submitResponse() to validate and store responses
    - Implement getProgress() to calculate completion percentage
    - Implement isComplete() to check if all questions answered
    - Implement getAllResponses() to retrieve all responses
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.3, 2.4_
  
  - [ ]* 5.3 Write property test for question progression
    - **Property 2: Question Progression**
    - **Validates: Requirements 1.3**
    - Generate random valid responses at various positions
    - Verify next question is displayed after submission
  
  - [ ]* 5.4 Write property test for progress calculation
    - **Property 3: Progress Calculation Accuracy**
    - **Validates: Requirements 1.5**
    - Generate random question positions
    - Verify progress percentage is correct (position / total)
  
  - [ ]* 5.5 Write property test for response storage
    - **Property 4: Response Storage Round-Trip**
    - **Validates: Requirements 2.3, 2.4**
    - Generate random responses and submit them
    - Verify all can be retrieved with exact content
  
  - [ ]* 5.6 Write unit tests for questionnaire flow
    - Test initial state shows first question
    - Test completion detection when all questions answered
    - Test that question set includes all required categories
    - _Requirements: 1.1, 1.4, 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 6. Checkpoint - Core logic validation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement AI Analyzer (mock for MVP)
  - [ ] 7.1 Create AIAnalyzer class with analysis methods
    - Implement analyzeResponses() to process response set
    - Implement identifyThemes() to extract key themes (mock implementation)
    - Implement assessMotivation() to determine motivation level (mock implementation)
    - Implement extractConstraints() to parse time/commitment info (mock implementation)
    - For MVP: Use rule-based logic or simple keyword matching
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 7.2 Write property test for complete response processing
    - **Property 5: Complete Response Processing**
    - **Validates: Requirements 3.1**
    - Generate random complete response sets
    - Verify analyzer receives all responses (count matches)
  
  - [ ]* 7.3 Write property test for recommendation generation
    - **Property 6: Recommendation Generation**
    - **Validates: Requirements 3.5**
    - Generate random analysis results
    - Verify recommendations array is non-empty
  
  - [ ]* 7.4 Write unit tests for analysis logic
    - Test that analysis produces AnalysisResult with all fields
    - Test edge case of minimal responses
    - _Requirements: 3.1, 3.5_

- [ ] 8. Implement Roadmap Generator
  - [ ] 8.1 Create RoadmapGenerator class
    - Implement generateRoadmap() to create full roadmap from analysis
    - Implement createSteps() to generate sequential steps
    - Implement addEncouragement() to add positive messages
    - Implement formatForDisplay() to structure output
    - Include disclaimer text about advisory nature
    - _Requirements: 4.1, 4.2, 5.1, 8.1, 8.5_
  
  - [ ]* 8.2 Write property test for roadmap structure
    - **Property 7: Roadmap Structure Integrity**
    - **Validates: Requirements 4.1, 4.2**
    - Generate random roadmaps
    - Verify sequential ordering (1, 2, 3... with no gaps)
    - Verify all required fields present (title, introduction, steps, encouragement, disclaimer)
  
  - [ ]* 8.3 Write property test for encouragement presence
    - **Property 8: Encouragement Presence**
    - **Validates: Requirements 5.1**
    - Generate random roadmaps
    - Verify encouragement field is non-empty
  
  - [ ]* 8.4 Write unit tests for roadmap content
    - Test that disclaimer is present
    - Test that acknowledgment of individual circumstances is present
    - Test that steps are actionable and specific
    - _Requirements: 4.1, 5.1, 8.1, 8.5_

- [ ] 9. Implement error handling
  - [ ] 9.1 Create error handling utilities
    - Create custom error types (ValidationError, AIAnalysisError, NetworkError, SystemError)
    - Implement error message sanitizer to remove technical details
    - Implement error logger (console for MVP)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 9.2 Write property test for error state preservation
    - **Property 10: Error State Preservation**
    - **Validates: Requirements 9.3**
    - Generate random session states and recoverable errors
    - Verify state unchanged after error
  
  - [ ]* 9.3 Write property test for error message safety
    - **Property 11: Error Message Safety**
    - **Validates: Requirements 9.4**
    - Generate random errors with stack traces
    - Verify user messages contain no technical details (no stack traces, file paths, variable names)
  
  - [ ]* 9.4 Write unit tests for specific error scenarios
    - Test AI analysis failure produces user-friendly message
    - Test network error produces retry suggestion
    - Test unrecoverable error provides restart instructions
    - _Requirements: 9.1, 9.2, 9.5_

- [ ] 10. Checkpoint - Business logic complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement UI components (basic CLI or web interface)
  - [ ] 11.1 Create UI Renderer for displaying content
    - Implement renderQuestion() to display question with progress
    - Implement renderError() to display error messages
    - Implement renderLoadingState() to show loading indicator
    - Implement renderRoadmap() to display formatted roadmap
    - Implement captureUserInput() to get user responses
    - For MVP: Use simple CLI interface or basic HTML forms
    - _Requirements: 1.1, 1.5, 7.1, 7.2, 7.5_
  
  - [ ]* 11.2 Write unit tests for UI rendering
    - Test that one question displayed at a time
    - Test that navigation controls are present
    - Test that loading indicator shown during analysis
    - Test that progress indicator reflects current position
    - _Requirements: 7.1, 7.2, 7.5, 1.5_

- [ ] 12. Integrate all components into main application flow
  - [ ] 12.1 Create main application controller
    - Wire SessionManager, QuestionnaireController, AIAnalyzer, RoadmapGenerator, UIRenderer together
    - Implement main flow: start session → display questions → collect responses → analyze → generate roadmap → display results
    - Add error handling at each stage
    - _Requirements: All requirements_
  
  - [ ]* 12.2 Write integration tests for end-to-end flow
    - Test complete flow from start to roadmap display
    - Test error recovery at each stage
    - Test session cleanup on completion
    - _Requirements: All requirements_

- [ ] 13. Final checkpoint - Complete system validation
  - Run all tests (unit, property, integration)
  - Verify all 11 correctness properties pass with 100+ iterations
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples and edge cases
- For MVP, AI analysis can use simple rule-based logic rather than actual AI service
- TypeScript provides type safety and better maintainability
- fast-check library provides property-based testing capabilities
- Integration tests ensure all components work together correctly
