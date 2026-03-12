# ADR-001: Data Model Extensions and MCP Tool Enhancement Approach

## Status
Accepted

## Date
2026-01-14

## Context
The Todo AI Chatbot needs to be enhanced with priority levels, tagging system, search functionality, filtering capabilities, and sorting options. The existing architecture uses MCP (Model Context Protocol) tools to interact with tasks. We need to decide how to extend the current system while maintaining backward compatibility and following the established architecture patterns.

The current system has:
- Task model with basic fields (id, user_id, title, description, completed, timestamps)
- MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
- PostgreSQL database with Neon
- FastMCP server implementation

## Decision
We will extend the existing architecture by:

1. **Data Model Extension**:
   - Add `priority` field as ENUM('high', 'medium', 'low') with default 'medium'
   - Add `tags` field as JSON array to store tag strings
   - Add appropriate database indexes for performance

2. **MCP Tool Enhancement**:
   - Extend `add_task` with optional `priority` and `tags` parameters
   - Extend `list_tasks` with filtering parameters (`priority`, `tags`, `search_term`, etc.) and sorting parameters (`sort_by`, `sort_order`)
   - Extend `update_task` with `priority` and `tags` update capabilities
   - Keep `complete_task` and `delete_task` unchanged

3. **Database Schema**:
   - Use PostgreSQL's native ENUM type for priority validation
   - Use JSONB for tags field to enable efficient querying
   - Add GIN index on tags for fast tag-based searches
   - Add composite indexes for common filter combinations

## Alternatives Considered

### Alternative 1: Separate Related Tables
- Create separate `priorities` and `tags` tables with many-to-many relationships
- Pros: More normalized, easier to enforce referential integrity
- Cons: More complex queries, potential performance impact, breaks existing patterns

### Alternative 2: Completely New Tool Set
- Create new MCP tools specifically for enhanced features
- Pros: Clean separation of concerns
- Cons: Breaks reuse-first approach, increases complexity, violates constitution requirements

### Alternative 3: Denormalized String Storage
- Store tags as comma-separated string
- Pros: Simple implementation
- Cons: Difficult to query efficiently, no validation, harder to maintain

### Alternative 4: External Search Service
- Integrate Elasticsearch or similar for advanced search
- Pros: Powerful search capabilities
- Cons: Additional infrastructure complexity, increased costs, deviates from simple architecture

## Consequences

### Positive
- Maintains backward compatibility with existing tools and clients
- Follows the reuse-first approach mandated by constitution
- Preserves existing architecture patterns and developer familiarity
- Enables rich new functionality without breaking changes
- Leverages PostgreSQL's advanced features for performance
- Maintains stateless architecture principles

### Negative
- Increases complexity of existing tools with more parameters
- Adds database storage overhead for new fields
- May require more sophisticated error handling
- Could impact performance if not properly indexed

## Implementation Notes
- Database migration will add columns with safe defaults
- All new parameters in MCP tools are optional to maintain compatibility
- Comprehensive validation will be implemented for new fields
- Performance will be monitored after implementation

## References
- specs/002-todo-enhancements/plan.md
- specs/002-todo-enhancements/research.md
- specs/002-todo-enhancements/data-model.md
- specs/002-todo-enhancements/contracts/api-contract.yaml