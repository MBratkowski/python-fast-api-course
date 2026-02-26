# Custom Commands for Backend Learning

## Learning Commands

### /learn <module>
Start learning a module. Displays theory content and guides through exercises.
Example: `/learn 003-fastapi-basics`

### /exercise <module> <number>
Work on a specific exercise with hints available.
Example: `/exercise 003-fastapi-basics 01`

### /test
Run tests for current module or specific file.
Example: `/test` or `/test 003-fastapi-basics`

### /hint
Get a contextual hint for the current exercise without revealing the solution.

### /solution
Show the reference solution for comparison (use after attempting).

### /progress
Display completion status across all modules.

### /next
Suggest the next module based on current progress.

## Development Commands

### /api
Start the FastAPI development server with hot reload.
```bash
uvicorn main:app --reload
```

### /db
Run database migrations or reset database.

### /docker
Build and run the Docker container for testing.

## Review Commands

### /review
Get code review feedback on current implementation.

### /check-types
Run mypy type checking on the codebase.

### /lint
Run ruff linting and auto-fix issues.
