# Feature Specification: OpenRouter Authentication Fix

**Feature Branch**: `003-openrouter-auth-fix`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "CRITICAL ISSUE: OpenRouter Authentication 401 Error Fix for Todo AI Chatbot"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Fix OpenRouter Authentication (Priority: P1)

As a user of the Todo AI Chatbot, I need the system to properly authenticate with OpenRouter API so that I can receive AI-generated responses to my requests without errors. Currently, the system shows 401 Unauthorized errors with "No cookie auth credentials found".

**Why this priority**: This is the most critical issue as the entire AI functionality is broken without proper authentication, making the core feature unusable.

**Independent Test**: Can be fully tested by sending a chat request to the API and verifying that the AI responds without 401 errors, delivering proper responses to user commands like "Add task to buy milk".

**Acceptance Scenarios**:

1. **Given** backend is configured with valid OpenRouter API key, **When** user sends a chat request, **Then** AI responds with a proper response without authentication errors
2. **Given** backend is running, **When** user sends "Add task to buy milk", **Then** AI confirms the task creation and the task appears in the database

---

### User Story 2 - Configure OpenRouter Client Properly (Priority: P2)

As a developer maintaining the Todo AI Chatbot, I need the OpenAI client to be properly configured for OpenRouter so that API calls use the correct endpoints and headers required by OpenRouter infrastructure.

**Why this priority**: This ensures proper integration with OpenRouter's API requirements, preventing future authentication and configuration issues.

**Independent Test**: Can be tested by verifying the OpenAI client configuration in code uses OpenRouter-specific settings like base_url, proper headers, and correct model names.

**Acceptance Scenarios**:

1. **Given** application starts up, **When** OpenAI client is initialized, **Then** it connects to OpenRouter API with correct configuration

---

### User Story 3 - Implement Error Handling for OpenRouter Issues (Priority: P3)

As a user of the Todo AI Chatbot, I need the system to handle OpenRouter-specific errors gracefully so that I get appropriate fallback responses when API issues occur.

**Why this priority**: This improves user experience during transient failures and provides resilience against API outages or rate limiting.

**Independent Test**: Can be tested by simulating various API error conditions and verifying appropriate user feedback.

**Acceptance Scenarios**:

1. **Given** OpenRouter API returns a 429 rate limit error, **When** user makes a request, **Then** system provides graceful fallback response to the user

---

### Edge Cases

- What happens when OpenRouter API key is invalid or expired?
- How does system handle network timeouts or connection failures to OpenRouter?
- What occurs when OpenRouter model is temporarily unavailable?
- How does the system behave with malformed API responses from OpenRouter?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST configure OpenAI client with OpenRouter-specific base URL (https://openrouter.ai/api/v1)
- **FR-002**: System MUST use OPENROUTER_API_KEY from environment variables for authentication
- **FR-003**: System MUST set proper headers including HTTP-Referer and X-Title for OpenRouter API
- **FR-004**: System MUST use OpenRouter-compatible model names (e.g., openrouter/auto instead of gpt models)
- **FR-005**: System MUST handle 401 Unauthorized errors by checking API key configuration
- **FR-006**: System MUST implement retry logic for 429 rate limit errors with exponential backoff
- **FR-007**: System MUST continue to process user requests after authentication fix is applied

### Key Entities *(include if feature involves data)*

- **OpenRouterClient**: Configuration and authentication settings for connecting to OpenRouter API
- **AuthenticationConfig**: Environment variables and settings required for OpenRouter API access

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Backend logs show 200 OK responses from OpenRouter API instead of 401 errors
- **SC-002**: Users receive AI responses within 2-5 seconds of sending requests
- **SC-003**: AI correctly processes user commands like "Add task to buy milk" and confirms actions
- **SC-004**: Created tasks appear in the database with correct user associations
- **SC-005**: Frontend consistently displays AI response messages without authentication errors
