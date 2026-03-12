# Research: Todo AI Chatbot Enhancement Features

## Overview
This document investigates the implementation approaches for adding priority levels, tagging system, search functionality, filtering capabilities, and sorting options to the Todo AI Chatbot.

## Feature Analysis

### 1. Priority Levels Implementation

**Decision**: Implement priority as an ENUM field with three values: 'high', 'medium', 'low'
**Rationale**:
- Simple to implement and understand
- Matches user requirements from spec
- Efficient for database queries and indexing
- Extensible if more levels are needed in the future

**Alternatives considered**:
- Integer scale (1-5): More granular but potentially confusing
- String-based flexible values: More flexible but harder to query consistently
- Boolean urgent/normal: Too limited for user needs

**Implementation approach**:
- Add `priority` column to Task model as ENUM('high', 'medium', 'low') with default 'medium'
- Update database migration to add this field
- Modify MCP tools to accept and return priority information

### 2. Tagging System Implementation

**Decision**: Implement tags as a JSON array field in the Task model
**Rationale**:
- Flexible storage that allows multiple tags per task
- JSON arrays are well-supported in PostgreSQL
- Efficient querying capabilities with PostgreSQL's JSON operators
- Maintains data integrity while allowing variable tag counts

**Alternatives considered**:
- Separate tags table with many-to-many relationship: More normalized but complex queries
- Comma-separated string: Simple but difficult to query efficiently
- Array field (PostgreSQL native): Good option but JSON offers more flexibility

**Implementation approach**:
- Add `tags` column to Task model as JSON field containing an array of strings
- Add database migration for the new field
- Update MCP tools to handle tag operations
- Create helper functions for tag management

### 3. Search Functionality Implementation

**Decision**: Implement full-text search using PostgreSQL's built-in capabilities combined with LIKE queries
**Rationale**:
- PostgreSQL has robust full-text search capabilities
- Can search across title, description, and tags efficiently
- Good performance characteristics for the expected scale
- Integrates well with existing database infrastructure

**Implementation approach**:
- Use PostgreSQL's `to_tsvector` and `to_tsquery` functions for full-text search
- Create database index on searchable fields for performance
- Implement search in the extended `list_tasks` MCP tool
- Support both exact and fuzzy matching

**Query approach**:
- Primary: Full-text search on title and description
- Secondary: JSON containment queries for tag searching
- Combined: UNION or combined WHERE clauses depending on search parameters

### 4. Filtering Capabilities Implementation

**Decision**: Extend the existing `list_tasks` MCP tool with additional filter parameters
**Rationale**:
- Maintains backward compatibility with existing API
- Leverages existing tool structure and patterns
- Easy for the AI agent to use consistent parameter format
- Can combine multiple filters for complex queries

**Filter types to implement**:
- Priority filter: Filter tasks by priority level(s)
- Tag filter: Filter tasks by tag(s)
- Status filter: Already exists (completed/pending), but can be enhanced
- Date range filter: Filter by creation or update dates

**Implementation approach**:
- Add optional parameters to `list_tasks` function: `priority`, `tags`, `date_from`, `date_to`
- Build dynamic SQL queries based on provided filter parameters
- Use AND logic for multiple filters, OR logic within multi-value parameters

### 5. Sorting Options Implementation

**Decision**: Extend the `list_tasks` MCP tool with sorting parameters
**Rationale**:
- Consistent with filtering approach using same tool
- Maintains backward compatibility (default sort unchanged)
- Flexible enough to support multiple sort criteria
- Can be combined with filters effectively

**Sort options to implement**:
- Priority: High to low (custom ordering)
- Alphabetical: By title (A-Z or Z-A)
- Chronological: By creation date (oldest/newest first)
- Custom: Combination of criteria

**Implementation approach**:
- Add `sort_by` and `sort_order` parameters to `list_tasks` function
- Use CASE statements for custom priority ordering (high, medium, low)
- Apply ORDER BY clauses dynamically based on parameters
- Maintain existing default sort (newest first by creation date) when no sort specified

## Technical Integration Points

### Database Schema Changes
1. Add `priority` column to tasks table (ENUM with default)
2. Add `tags` column to tasks table (JSON)
3. Create indexes for performance:
   - Index on priority for filtering
   - GIN index on tags for JSON queries
   - Composite indexes for combined searches

### MCP Tools Extension
1. **add_task**: Add `priority` and `tags` optional parameters
2. **list_tasks**: Add `priority`, `tags`, `search`, `date_from`, `date_to`, `sort_by`, `sort_order` parameters
3. **update_task**: Add `priority` and `tags` optional parameters
4. **complete_task** and **delete_task**: No changes needed

### Query Performance Considerations
- Use EXPLAIN ANALYZE to optimize queries during implementation
- Consider partial indexes for frequently used filter combinations
- Monitor query performance with increasing data volume
- Implement pagination for large result sets in future iterations

## Risk Assessment

### Potential Issues
1. **Performance degradation**: Additional fields and queries may slow response times
   - Mitigation: Proper indexing and query optimization
2. **Migration complexity**: Updating existing data without downtime
   - Mitigation: Careful migration planning with backward compatibility
3. **Complexity in AI parsing**: More parameters may confuse the AI agent
   - Mitigation: Clear parameter documentation and examples

### Dependencies
- PostgreSQL full-text search capabilities
- SQLModel's JSON field support
- Existing MCP tool framework compatibility

## Conclusion
The planned implementation approach extends the existing architecture in a compatible way while adding the required functionality. The database-centric approach leverages PostgreSQL's strengths for efficient search and filtering operations. The MCP tool extensions maintain API consistency while providing rich new capabilities for task management.