# Profiling with cProfile

## Why This Matters

On iOS, you attach Instruments' Time Profiler to your app and immediately see a call tree showing which methods consume the most CPU time. On Android, the CPU Profiler in Android Studio gives you flame charts and method traces. You never guess where the bottleneck is -- you measure it.

Python has the same capability built into the standard library. `cProfile` is Python's Time Profiler: it records every function call, how many times it was called, and how long it took. The workflow is identical to what you already know -- attach a profiler, reproduce the slow behavior, read the results, fix the hotspot.

## Python Profiling Tools

| Tool | What It Does | Install | Mobile Equivalent |
|------|-------------|---------|-------------------|
| `cProfile` | Function-level CPU profiling | stdlib | Instruments Time Profiler / CPU Profiler |
| `line_profiler` | Line-by-line timing | `pip install line-profiler` | Instruments with source-level detail |
| `memory_profiler` | Line-by-line memory usage | `pip install memory-profiler` | Instruments Allocations / Memory Profiler |
| `tracemalloc` | Memory allocation tracking | stdlib | Instruments Leaks |
| `snakeviz` | Interactive profile visualization | `pip install snakeviz` | Instruments call tree UI |

## Using cProfile

### Command-line profiling

The simplest way to profile a script:

```bash
python -m cProfile -s cumulative my_script.py
```

The `-s cumulative` flag sorts results by cumulative time (the total time spent in a function including all functions it calls).

### Programmatic profiling

For more control, use `cProfile.Profile()` directly:

```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(10000):
        total += sum(range(i))
    return total

# Profile the function
profiler = cProfile.Profile()
profiler.enable()
result = slow_function()
profiler.disable()

# Print sorted results
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)  # Top 10 functions
```

### Saving and loading profiles

```python
import cProfile

# Save profile to a file
cProfile.run("slow_function()", "output.prof")

# Load and analyze later
import pstats
stats = pstats.Stats("output.prof")
stats.sort_stats("cumulative")
stats.print_stats(20)
```

## Reading Profiler Output

cProfile output looks like this:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    10000    0.015    0.000   12.345    0.001 script.py:5(slow_function)
    10000    12.330    0.001   12.330    0.001 {built-in method builtins.sum}
        1    0.000    0.000   12.345   12.345 script.py:1(main)
```

| Column | Meaning |
|--------|---------|
| `ncalls` | Number of times the function was called |
| `tottime` | Total time spent in this function only (excluding sub-calls) |
| `percall` | `tottime / ncalls` -- average time per call (excluding sub-calls) |
| `cumtime` | Cumulative time in this function AND everything it calls |
| `percall` | `cumtime / ncalls` -- average cumulative time per call |

**How to read it:**
- High `tottime` = the function itself is slow (optimize its code)
- High `cumtime` but low `tottime` = the function calls something slow (look at what it calls)
- High `ncalls` = the function is called too many times (reduce call count)

**Mobile analogy:** This is the same as reading the Instruments call tree. `tottime` is "Self Time" and `cumtime` is "Total Time" in Instruments terminology.

## Visualizing with snakeviz

Reading raw profiler output is like reading Instruments data in text form -- possible but painful. snakeviz gives you an interactive visualization:

```bash
pip install snakeviz

# Profile and save
python -m cProfile -o profile.prof my_script.py

# Open interactive visualization in browser
snakeviz profile.prof
```

snakeviz shows an icicle diagram where:
- Each rectangle is a function
- Width represents time spent
- Depth shows the call stack
- Click to zoom into a specific function

## FastAPI Middleware for Request Timing

In production, you want to know how long each request takes:

```python
import time
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    logger.info(
        "Request %s %s completed in %.3fs",
        request.method,
        request.url.path,
        duration,
    )

    response.headers["X-Process-Time"] = f"{duration:.3f}"
    return response
```

This is the backend equivalent of measuring your ViewController's `viewDidLoad()` time or your Fragment's `onCreateView()` duration.

## Profiling FastAPI Endpoints

To profile a specific endpoint during development:

```python
import cProfile
import pstats
import io
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def get_users():
    profiler = cProfile.Profile()
    profiler.enable()

    # Your actual logic here
    users = await fetch_all_users()

    profiler.disable()

    # Log the top bottlenecks
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(5)
    logger.debug("Profile:\n%s", stream.getvalue())

    return users
```

**Important:** Remove profiling code before deploying to production. Profiling adds overhead.

## Comparison: Mobile vs Python Profiling

| Workflow Step | iOS (Instruments) | Android (Studio Profiler) | Python (cProfile) |
|---------------|-------------------|---------------------------|-------------------|
| Start profiling | Product > Profile | Run > Profile | `python -m cProfile` or `profiler.enable()` |
| See call tree | Built-in UI | Built-in flame chart | `pstats.Stats.print_stats()` |
| Visualize | Instruments UI | Studio UI | `snakeviz profile.prof` |
| Filter by function | Click in call tree | Click flame chart | `stats.print_callers()` |
| Save results | Instruments trace file | `.trace` file | `.prof` file |

## Key Takeaways

1. **Always measure, never guess.** Use cProfile to identify the actual bottleneck before optimizing anything.
2. **`tottime` is self time, `cumtime` is total time.** High tottime means the function itself is slow. High cumtime with low tottime means it calls something slow.
3. **Sort by cumulative time** to find the functions that contribute most to total execution time.
4. **Use snakeviz for visualization.** Reading raw cProfile output is tedious; snakeviz makes patterns obvious.
5. **Profile in development, time in production.** Use cProfile during development; use timing middleware (not full profiling) in production.
6. **The 80/20 rule applies.** Usually one or two functions cause most of the slowdown. Fix those first.
