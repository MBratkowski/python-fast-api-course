"""
Exercise 2: Celery Task Definitions

Learn to define and test Celery tasks using task.apply() for synchronous execution.
No running Redis server or Celery worker is needed -- apply() executes tasks in-process.

Run: pytest 013-background-tasks/exercises/02_celery_tasks.py -v

Note: These exercises use task.apply() which runs tasks synchronously for testing.
In production, you would use task.delay() or task.apply_async() with a running worker.
"""

from celery import Celery
import pytest

# ============= CELERY APP SETUP (PROVIDED) =============

# Create Celery app with eager mode for testing (no broker needed)
celery_app = Celery("test_worker")
celery_app.conf.update(
    task_always_eager=True,          # Execute tasks synchronously
    task_eager_propagates=True,      # Propagate exceptions
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)


# ============= TODO: Exercise 2.1 =============
# Define a basic Celery task that processes data.
# - Task name: process_data
# - Parameters: items (list of dicts)
# - Return a dict with:
#   - "count": number of items processed
#   - "ids": list of "id" values from each item
#
# Example: process_data([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}])
#          -> {"count": 2, "ids": [1, 2]}

@celery_app.task
def process_data(items: list) -> dict:
    """Process a list of data items and extract IDs."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.2 =============
# Define a task that computes a value and returns it via the result backend.
# - Task name: calculate_statistics
# - Parameters: numbers (list of int/float)
# - Return a dict with:
#   - "sum": sum of all numbers
#   - "average": average of all numbers (0 if empty list)
#   - "min": minimum value (None if empty list)
#   - "max": maximum value (None if empty list)
#   - "count": number of values

@celery_app.task
def calculate_statistics(numbers: list) -> dict:
    """Calculate statistics for a list of numbers."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.3 =============
# Define a task that transforms data and passes it to another task.
# This simulates a simple task chain pattern.
#
# Task 1: normalize_text
# - Parameters: text (str)
# - Return the text stripped and lowered: text.strip().lower()
#
# Task 2: count_words
# - Parameters: text (str)
# - Return a dict with:
#   - "text": the input text
#   - "word_count": number of words (split by whitespace)
#   - "char_count": number of characters (including spaces)
#
# Task 3: process_text_pipeline
# - Parameters: text (str)
# - Call normalize_text synchronously using .apply()
# - Pass the result to count_words synchronously using .apply()
# - Return the final result from count_words

@celery_app.task
def normalize_text(text: str) -> str:
    """Normalize text by stripping and lowering."""
    # TODO: Implement
    pass


@celery_app.task
def count_words(text: str) -> dict:
    """Count words and characters in text."""
    # TODO: Implement
    pass


@celery_app.task
def process_text_pipeline(text: str) -> dict:
    """Pipeline: normalize text, then count words."""
    # TODO: Implement
    # Hint: Use normalize_text.apply(args=[text]).result
    # Then pass that result to count_words.apply(args=[...]).result
    pass


# ============= TODO: Exercise 2.4 =============
# Define a task that handles different data types gracefully.
# - Task name: safe_divide
# - Parameters: a (number), b (number)
# - Return a dict with:
#   - "result": a / b (as float)
#   - "status": "success"
# - If b is 0, return:
#   - "result": None
#   - "status": "error"
#   - "message": "Division by zero"

@celery_app.task
def safe_divide(a, b) -> dict:
    """Safely divide two numbers."""
    # TODO: Implement
    pass


# ============= TODO: Exercise 2.5 =============
# Define a task that aggregates results from multiple sub-tasks.
# - Task name: aggregate_reports
# - Parameters: report_configs (list of dicts with "name" and "value" keys)
# - For each config, compute: {"name": config["name"], "doubled": config["value"] * 2}
# - Return a dict with:
#   - "reports": list of computed report dicts
#   - "total_value": sum of all original values
#   - "report_count": number of reports

@celery_app.task
def aggregate_reports(report_configs: list) -> dict:
    """Aggregate multiple report configurations."""
    # TODO: Implement
    pass


# ============= TESTS =============
# Run with: pytest 013-background-tasks/exercises/02_celery_tasks.py -v


def test_process_data_basic():
    """Test basic data processing task."""
    items = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = process_data.apply(args=[items])

    assert result.successful(), "Task should succeed"
    data = result.result
    assert data["count"] == 2
    assert data["ids"] == [1, 2]


def test_process_data_empty():
    """Test processing empty data."""
    result = process_data.apply(args=[[]])

    assert result.successful()
    data = result.result
    assert data["count"] == 0
    assert data["ids"] == []


def test_calculate_statistics():
    """Test statistics calculation."""
    numbers = [10, 20, 30, 40, 50]
    result = calculate_statistics.apply(args=[numbers])

    assert result.successful()
    data = result.result
    assert data["sum"] == 150
    assert data["average"] == 30.0
    assert data["min"] == 10
    assert data["max"] == 50
    assert data["count"] == 5


def test_calculate_statistics_empty():
    """Test statistics with empty list."""
    result = calculate_statistics.apply(args=[[]])

    assert result.successful()
    data = result.result
    assert data["sum"] == 0
    assert data["average"] == 0
    assert data["min"] is None
    assert data["max"] is None
    assert data["count"] == 0


def test_calculate_statistics_single():
    """Test statistics with single value."""
    result = calculate_statistics.apply(args=[[42]])

    assert result.successful()
    data = result.result
    assert data["sum"] == 42
    assert data["average"] == 42.0
    assert data["min"] == 42
    assert data["max"] == 42


def test_normalize_text():
    """Test text normalization."""
    result = normalize_text.apply(args=["  Hello World  "])

    assert result.successful()
    assert result.result == "hello world"


def test_count_words():
    """Test word counting."""
    result = count_words.apply(args=["hello world"])

    assert result.successful()
    data = result.result
    assert data["text"] == "hello world"
    assert data["word_count"] == 2
    assert data["char_count"] == 11


def test_process_text_pipeline():
    """Test the full text processing pipeline."""
    result = process_text_pipeline.apply(args=["  Hello Beautiful World  "])

    assert result.successful()
    data = result.result
    assert data["text"] == "hello beautiful world"
    assert data["word_count"] == 3
    assert data["char_count"] == 21


def test_safe_divide_success():
    """Test successful division."""
    result = safe_divide.apply(args=[10, 3])

    assert result.successful()
    data = result.result
    assert abs(data["result"] - 3.3333) < 0.01
    assert data["status"] == "success"


def test_safe_divide_by_zero():
    """Test division by zero handling."""
    result = safe_divide.apply(args=[10, 0])

    assert result.successful()
    data = result.result
    assert data["result"] is None
    assert data["status"] == "error"
    assert data["message"] == "Division by zero"


def test_aggregate_reports():
    """Test report aggregation."""
    configs = [
        {"name": "sales", "value": 100},
        {"name": "traffic", "value": 200},
        {"name": "signups", "value": 50},
    ]
    result = aggregate_reports.apply(args=[configs])

    assert result.successful()
    data = result.result
    assert data["report_count"] == 3
    assert data["total_value"] == 350
    assert len(data["reports"]) == 3
    assert data["reports"][0] == {"name": "sales", "doubled": 200}
    assert data["reports"][1] == {"name": "traffic", "doubled": 400}
    assert data["reports"][2] == {"name": "signups", "doubled": 100}


def test_aggregate_reports_empty():
    """Test aggregation with empty configs."""
    result = aggregate_reports.apply(args=[[]])

    assert result.successful()
    data = result.result
    assert data["report_count"] == 0
    assert data["total_value"] == 0
    assert data["reports"] == []
