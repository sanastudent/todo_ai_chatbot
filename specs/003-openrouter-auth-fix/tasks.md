---
description: "Task list for OpenRouter Authentication Fix"
---

# Tasks: OpenRouter Authentication Fix

**Input**: Design documents from `/specs/003-openrouter-auth-fix/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Analyze current codebase to identify recent changes causing OpenRouter 401 error
- [X] T002 Locate OpenAI client initialization in agent service files
- [X] T003 [P] Examine recent commit history for authentication-related changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Locate and verify current OpenRouter API key configuration in .env
- [X] T005 [P] Identify all files containing OpenAI client initialization
- [X] T006 [P] Document current OpenAI client configuration parameters
- [X] T007 Find current OpenRouter client configuration in services
- [X] T008 [P] Locate API routes that handle chat requests

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Fix OpenRouter Authentication (Priority: P1) 🎯 MVP

**Goal**: Fix OpenRouter authentication 401 errors by correcting client configuration

**Independent Test**: Send a chat request and verify that AI responds without authentication errors

### Implementation for User Story 1

- [X] T009 [P] [US1] Update OpenAI client base URL to OpenRouter endpoint in src/services/openrouter_client.py
- [X] T010 [P] [US1] Add required OpenRouter headers (HTTP-Referer, X-Title) to client configuration
- [X] T011 [US1] Verify API key is loaded correctly from environment variables
- [X] T012 [US1] Update model specification to use OpenRouter-compatible model names
- [X] T013 [US1] Test authentication with minimal verification using sample request
- [X] T014 [US1] Add proper error handling for 401 Unauthorized responses

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Configure OpenRouter Client Properly (Priority: P2)

**Goal**: Ensure OpenAI client is properly configured for OpenRouter with all required settings

**Independent Test**: Verify the OpenAI client configuration uses OpenRouter-specific settings like base_url, proper headers, and correct model names

### Implementation for User Story 2

- [X] T015 [P] [US2] Implement proper OpenRouter client initialization in src/services/agent.py
- [X] T016 [P] [US2] Add configuration validation on application startup
- [X] T017 [US2] Update environment variable loading mechanism
- [X] T018 [US2] Add health checks that verify AI service accessibility
- [X] T019 [US2] Create documentation for required OpenRouter-specific settings

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Implement Error Handling for OpenRouter Issues (Priority: P3)

**Goal**: Handle OpenRouter-specific errors gracefully to improve user experience

**Independent Test**: Simulate various API error conditions and verify appropriate user feedback

### Implementation for User Story 3

- [X] T020 [P] [US3] Implement retry logic for 429 rate limit errors with exponential backoff
- [X] T021 [US3] Add graceful fallback responses for API errors
- [X] T022 [US3] Create error logging for troubleshooting OpenRouter issues
- [X] T023 [US3] Add comprehensive error handling for various OpenRouter API responses

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T024 [P] Update README.md with OpenRouter configuration requirements
- [X] T025 Create tests for OpenRouter connectivity
- [X] T026 [P] Add configuration validation checks
- [X] T027 Verify logs show successful OpenRouter API calls (200 status)
- [X] T028 Test that "Add task to buy milk" returns AI response correctly
- [X] T029 Confirm frontend displays responses properly
- [X] T030 Ensure no "401 Unauthorized" errors appear in logs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence