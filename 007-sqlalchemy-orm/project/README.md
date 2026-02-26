# Project: Task Management Data Layer

## Overview

Build the data layer (models + CRUD operations) for a task management application. This project demonstrates SQLAlchemy model definitions, relationships, and database operations without the API layer - just the database code.

## Requirements

### 1. Define SQLAlchemy Models

Create four models with relationships:

**User:**
- `id`: int, primary key
- `username`: str (max 50), unique, not null
- `email`: str (max 255), unique, not null
- `created_at`: datetime, default to current time

**Project:**
- `id`: int, primary key
- `name`: str (max 100), not null
- `description`: text, nullable
- `owner_id`: int, foreign key to users.id
- `created_at`: datetime, default to current time
- Relationship: `owner` (many-to-one to User)
- Relationship: `tasks` (one-to-many to Task)

**Task:**
- `id`: int, primary key
- `title`: str (max 200), not null
- `description`: text, nullable
- `status`: str (max 20), default "todo", choices: ["todo", "in_progress", "done"]
- `priority`: int, default 3, range 1-5
- `project_id`: int, foreign key to projects.id
- `assignee_id`: int, foreign key to users.id, nullable
- `created_at`: datetime, default to current time
- `updated_at`: datetime, default to current time, update on change
- Relationship: `project` (many-to-one to Project)
- Relationship: `assignee` (many-to-one to User, nullable)
- Relationship: `comments` (one-to-many to Comment)

**Comment:**
- `id`: int, primary key
- `content`: text, not null
- `task_id`: int, foreign key to tasks.id
- `author_id`: int, foreign key to users.id
- `created_at`: datetime, default to current time
- Relationship: `task` (many-to-one to Task)
- Relationship: `author` (many-to-one to User)

### 2. Database Setup

- Use SQLite for this project (simpler than PostgreSQL)
- Create database file: `task_management.db`
- Use `Base.metadata.create_all()` to create tables (acceptable for this project)

### 3. Implement CRUD Functions

Create a `TaskRepository` class with methods:

**Project Operations:**
- `create_project(user_id, name, description) -> Project`
- `list_user_projects(user_id) -> list[Project]`
- `get_project(project_id) -> Project | None`

**Task Operations:**
- `create_task(project_id, title, description, priority, assignee_id?) -> Task`
- `update_task_status(task_id, status) -> Task | None`
- `assign_task(task_id, assignee_id) -> Task | None`
- `get_project_tasks(project_id, status?) -> list[Task]` (filter by status if provided)

**Comment Operations:**
- `add_comment(task_id, author_id, content) -> Comment`
- `get_task_comments(task_id) -> list[Comment]`

### 4. Implement Query Functions

**Statistics and Reports:**
- `get_tasks_by_status(project_id) -> dict[str, int]` - Count of tasks per status
- `get_user_assigned_tasks(user_id) -> list[Task]` - All tasks assigned to user across all projects
- `get_high_priority_tasks(project_id) -> list[Task]` - Tasks with priority 1 or 2

## Starter Template

```python
# task_manager.py
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime


class Base(DeclarativeBase):
    pass


# ============= Models =============

class User(Base):
    __tablename__ = "users"
    # TODO: Add fields and relationships


class Project(Base):
    __tablename__ = "projects"
    # TODO: Add fields and relationships


class Task(Base):
    __tablename__ = "tasks"
    # TODO: Add fields and relationships


class Comment(Base):
    __tablename__ = "comments"
    # TODO: Add fields and relationships


# ============= Database Setup =============

def init_db():
    """Initialize database and create tables."""
    engine = create_engine("sqlite:///task_management.db", echo=True)
    Base.metadata.create_all(engine)
    return engine


# ============= Repository =============

class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    # TODO: Implement all CRUD and query methods

    def create_project(self, user_id: int, name: str, description: str | None = None) -> Project:
        """Create a new project."""
        pass

    def list_user_projects(self, user_id: int) -> list[Project]:
        """List all projects owned by user."""
        pass

    # ... (add other methods)


# ============= Main Function (for testing) =============

def main():
    """Demonstrate the task management system."""
    engine = init_db()

    with Session(engine) as session:
        repo = TaskRepository(session)

        # Create user
        user = User(username="alice", email="alice@example.com")
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create project
        project = repo.create_project(user.id, "Website Redesign", "Redesign company website")

        # Create tasks
        task1 = repo.create_task(project.id, "Design mockups", "Create UI mockups", priority=1)
        task2 = repo.create_task(project.id, "Implement frontend", "Build React components", priority=2)

        # Update task status
        repo.update_task_status(task1.id, "in_progress")

        # Assign task
        repo.assign_task(task2.id, user.id)

        # Add comment
        repo.add_comment(task1.id, user.id, "Started working on this!")

        # Query tasks
        tasks = repo.get_project_tasks(project.id)
        print(f"Project has {len(tasks)} tasks")

        # Get status breakdown
        status_counts = repo.get_tasks_by_status(project.id)
        print(f"Status breakdown: {status_counts}")


if __name__ == "__main__":
    main()
```

## Success Criteria

- [ ] All four models defined with correct field types and constraints
- [ ] Relationships properly configured with `back_populates`
- [ ] Database creates without errors
- [ ] Can create users, projects, tasks, and comments
- [ ] Can update task status and assignee
- [ ] Can query tasks by project and filter by status
- [ ] Can get user's assigned tasks across all projects
- [ ] Status counts query returns correct data
- [ ] High priority task query works correctly
- [ ] All foreign key constraints are enforced

## Testing Your Implementation

```python
def test_basic_workflow():
    """Test a complete workflow."""
    engine = init_db()

    with Session(engine) as session:
        repo = TaskRepository(session)

        # Create user
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        session.add_all([user1, user2])
        session.commit()

        # Create project
        project = repo.create_project(user1.id, "Test Project", "Testing")

        # Create tasks
        task1 = repo.create_task(project.id, "Task 1", None, priority=1)
        task2 = repo.create_task(project.id, "Task 2", None, priority=5)

        # Assign and update
        repo.assign_task(task1.id, user2.id)
        repo.update_task_status(task1.id, "in_progress")

        # Verify
        tasks = repo.get_project_tasks(project.id)
        assert len(tasks) == 2

        user2_tasks = repo.get_user_assigned_tasks(user2.id)
        assert len(user2_tasks) == 1
        assert user2_tasks[0].title == "Task 1"

        high_priority = repo.get_high_priority_tasks(project.id)
        assert len(high_priority) == 1
        assert high_priority[0].priority == 1
```

## Stretch Goals

1. **Task Labels (many-to-many):**
   - Add `Label` model
   - Create `task_labels` association table
   - Add methods: `add_label_to_task()`, `get_tasks_by_label()`

2. **Task History Tracking:**
   - Add `TaskHistory` model to track status changes
   - Record who changed status and when
   - Query: `get_task_history(task_id)`

3. **Project Statistics:**
   - `get_project_stats(project_id)` → dict with:
     - Total tasks
     - Completed tasks
     - In-progress tasks
     - Average priority
     - Comment count

4. **Due Dates and Overdue Tasks:**
   - Add `due_date` field to Task
   - Query: `get_overdue_tasks(project_id)` - tasks past due date with status != "done"

5. **Cascade Delete Configuration:**
   - Configure cascades so:
     - Deleting project deletes its tasks
     - Deleting task deletes its comments
     - Deleting user does NOT delete their projects (set owner_id to NULL or prevent deletion)
