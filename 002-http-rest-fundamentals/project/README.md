# Project: Task Management API Specification

## Overview

Design a complete REST API specification for a task management application (like Todoist, Things, or Asana). This is a conceptual design exercise - you'll define the endpoints, not implement them.

Your mobile app would consume this API to display tasks, create new tasks, organize them into categories, and assign them to users.

## Requirements

Design endpoints for:

1. **Tasks** (CRUD operations)
   - List all tasks (with pagination)
   - Get single task
   - Create new task
   - Update task (partial update)
   - Delete task
   - Mark task as complete/incomplete

2. **Categories** (organizing tasks)
   - List categories
   - Create category
   - Get tasks in a category

3. **Task Assignments** (multi-user support)
   - Assign task to user
   - Unassign task from user
   - Get user's assigned tasks

4. **Additional considerations**:
   - Include proper HTTP methods
   - Include expected status codes
   - Include example request/response bodies
   - Follow REST naming conventions

## Starter Template

```python
# task_api_spec.py
"""
Task Management API Specification

Define your API endpoints as a list of dictionaries.
"""

API_SPEC = {
    "base_url": "https://api.taskapp.com/v1",
    "endpoints": [
        # TODO: Add your endpoint definitions here
        # Example structure:
        # {
        #     "method": "GET",
        #     "path": "/tasks",
        #     "description": "List all tasks",
        #     "query_params": ["page", "limit", "status"],
        #     "success_status": 200,
        #     "response_example": {
        #         "tasks": [...],
        #         "pagination": {...}
        #     }
        # }
    ]
}

# Task model (for reference)
TASK_MODEL = {
    "id": "integer",
    "title": "string",
    "description": "string",
    "status": "string (pending|in_progress|completed)",
    "category_id": "integer|null",
    "assigned_to": "integer|null (user_id)",
    "due_date": "string (ISO 8601)",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
}

# Category model
CATEGORY_MODEL = {
    "id": "integer",
    "name": "string",
    "color": "string",
    "created_at": "string (ISO 8601)"
}

# TODO: Define at least 10 endpoints covering:
# - Task CRUD
# - Task status updates
# - Category CRUD
# - Task-Category relationships
# - Task assignments

if __name__ == "__main__":
    # Print your API spec
    print(f"API Base: {API_SPEC['base_url']}")
    print(f"\nTotal Endpoints: {len(API_SPEC['endpoints'])}")
    print("\nEndpoints:")
    for ep in API_SPEC['endpoints']:
        print(f"  {ep['method']:6} {ep['path']:40} - {ep['description']}")
```

## Success Criteria

- [ ] At least 10 endpoints defined
- [ ] All CRUD operations for tasks covered
- [ ] Category management endpoints included
- [ ] Task assignment endpoints included
- [ ] All endpoints use correct HTTP methods
- [ ] All endpoints follow REST naming (plural nouns, no verbs)
- [ ] Each endpoint has example request/response
- [ ] Proper status codes specified
- [ ] Pagination considered for list endpoints
- [ ] Filtering options included (e.g., filter by status, category)

## Stretch Goals

1. **Advanced Filtering**: Add search and advanced filter endpoints
   - Search tasks by title/description
   - Filter by date range
   - Filter by multiple criteria

2. **Pagination Design**: Define both offset-based and cursor-based pagination
   - Offset: `?page=1&limit=20`
   - Cursor: `?cursor=abc123&limit=20`

3. **Error Response Format**: Define consistent error response structure
   - Include error codes
   - Include field-level validation errors
   - Include error messages

4. **Bulk Operations**: Design endpoints for bulk actions
   - Bulk create tasks
   - Bulk update task status
   - Bulk delete tasks

5. **Sub-tasks**: Add support for hierarchical tasks
   - Create sub-task under parent task
   - List all sub-tasks
   - Move task to be sub-task of another

## Example Endpoint Definition

```python
{
    "method": "GET",
    "path": "/tasks",
    "description": "List all tasks with optional filtering",
    "query_params": {
        "page": "integer (default: 1)",
        "limit": "integer (default: 20, max: 100)",
        "status": "string (pending|in_progress|completed)",
        "category_id": "integer",
        "assigned_to": "integer (user_id)"
    },
    "success_status": 200,
    "response_example": {
        "tasks": [
            {
                "id": 1,
                "title": "Write API documentation",
                "status": "in_progress",
                "category_id": 2,
                "assigned_to": 5,
                "due_date": "2024-03-20T00:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 150,
            "pages": 8
        }
    }
}
```

## Tips

- Think about how your mobile app would use this API
- What screens need which endpoints?
- What data does each screen need to fetch?
- How would you handle loading states and pagination?
- What error scenarios need specific status codes?

Remember: This is design practice. Focus on clean, consistent, predictable patterns that would make the mobile developer's job easy.
