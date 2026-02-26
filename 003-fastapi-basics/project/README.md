# Project: Quotes API

## Overview

Build a simple API for managing a collection of quotes. This project practices FastAPI basics: routing, request handling, in-memory storage, and CRUD operations.

## Requirements

Create a FastAPI application with the following endpoints:

### 1. List All Quotes
- **GET /quotes**
- Returns all quotes
- Response: `{"quotes": [...]}`

### 2. Get Single Quote
- **GET /quotes/{quote_id}**
- Returns a specific quote by ID
- 404 if quote not found

### 3. Get Random Quote
- **GET /quotes/random**
- Returns a random quote from the collection
- Use `import random` and `random.choice()`

### 4. Add New Quote
- **POST /quotes**
- Request body: `{"text": "...", "author": "..."}`
- Creates new quote with auto-generated ID
- Returns created quote with 201 status

### 5. Delete Quote
- **DELETE /quotes/{quote_id}**
- Removes quote from collection
- Returns 204 No Content
- 404 if quote not found

## Starter Template

```python
# quotes_api.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import random

app = FastAPI(
    title="Quotes API",
    description="A simple API for managing inspirational quotes",
    version="1.0.0"
)

# Pydantic models
class QuoteCreate(BaseModel):
    """Schema for creating a new quote."""
    text: str
    author: str

class Quote(BaseModel):
    """Schema for quote response."""
    id: int
    text: str
    author: str

# In-memory storage
QUOTES = [
    {"id": 1, "text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"id": 2, "text": "Innovation distinguishes between a leader and a follower.", "author": "Steve Jobs"},
    {"id": 3, "text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"id": 4, "text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"id": 5, "text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
]

next_id = 6  # For auto-incrementing IDs


# TODO: Implement GET /quotes
@app.get("/quotes", tags=["quotes"])
async def list_quotes():
    """List all quotes."""
    pass  # TODO: Return {"quotes": QUOTES}


# TODO: Implement GET /quotes/{quote_id}
@app.get("/quotes/{quote_id}", tags=["quotes"], response_model=Quote)
async def get_quote(quote_id: int):
    """Get a quote by ID."""
    pass  # TODO: Search QUOTES for quote_id, raise 404 if not found


# TODO: Implement GET /quotes/random
@app.get("/quotes/random", tags=["quotes"], response_model=Quote)
async def get_random_quote():
    """Get a random quote."""
    pass  # TODO: Use random.choice(QUOTES)


# TODO: Implement POST /quotes
@app.post("/quotes", tags=["quotes"], response_model=Quote, status_code=status.HTTP_201_CREATED)
async def create_quote(quote: QuoteCreate):
    """Create a new quote."""
    global next_id
    pass  # TODO: Create new quote dict, add to QUOTES, increment next_id, return new quote


# TODO: Implement DELETE /quotes/{quote_id}
@app.delete("/quotes/{quote_id}", tags=["quotes"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(quote_id: int):
    """Delete a quote."""
    pass  # TODO: Find and remove quote from QUOTES, raise 404 if not found, return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the API

```bash
# Run with uvicorn
uvicorn quotes_api:app --reload

# Or run the file directly
python quotes_api.py
```

Visit:
- API: http://localhost:8000/quotes
- Docs: http://localhost:8000/docs

## Testing with curl

```bash
# List all quotes
curl http://localhost:8000/quotes

# Get quote by ID
curl http://localhost:8000/quotes/1

# Get random quote
curl http://localhost:8000/quotes/random

# Create new quote
curl -X POST http://localhost:8000/quotes \
  -H "Content-Type: application/json" \
  -d '{"text": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde"}'

# Delete quote
curl -X DELETE http://localhost:8000/quotes/1
```

## Success Criteria

- [ ] All 5 endpoints implemented and working
- [ ] List endpoint returns all quotes
- [ ] Get by ID returns correct quote or 404
- [ ] Random endpoint returns different quotes
- [ ] Create endpoint adds new quote with auto-generated ID
- [ ] Create endpoint returns 201 status code
- [ ] Delete endpoint removes quote and returns 204
- [ ] Delete endpoint returns 404 for non-existent quote
- [ ] All endpoints have proper tags for documentation
- [ ] API documentation accessible at /docs
- [ ] No errors when running pytest (if you add tests)

## Stretch Goals

1. **Search Quotes**
   - Add `GET /quotes/search?query=innovation`
   - Search in both text and author fields
   - Case-insensitive search

2. **Filter by Author**
   - Add `GET /quotes?author=Steve Jobs`
   - Return only quotes from specified author

3. **Pagination**
   - Add `GET /quotes?skip=0&limit=10`
   - Return paginated results with total count

4. **Update Quote**
   - Add `PATCH /quotes/{quote_id}`
   - Allow updating text and/or author
   - Return updated quote

5. **Quote Categories**
   - Add category field to quotes (motivational, funny, wisdom, etc.)
   - Filter by category: `GET /quotes?category=motivational`

6. **Favorite Quotes**
   - Add favorite flag to quotes
   - Endpoint to toggle favorite: `POST /quotes/{quote_id}/favorite`
   - List favorites: `GET /quotes/favorites`

## Example Manual Testing

Using the interactive docs at http://localhost:8000/docs:

1. **List quotes** - Click GET /quotes → Try it out → Execute
2. **Get quote** - Click GET /quotes/{quote_id} → Try it out → Enter ID: 1 → Execute
3. **Random quote** - Click GET /quotes/random → Try it out → Execute (multiple times)
4. **Create quote** - Click POST /quotes → Try it out → Fill in text and author → Execute
5. **Delete quote** - Click DELETE /quotes/{quote_id} → Try it out → Enter ID → Execute

## Tips

- Use the interactive docs (/docs) for testing - easier than curl
- Start with list_quotes - it's the simplest
- get_quote and delete_quote need to search QUOTES and handle 404
- For random quote, import random at the top: `import random`
- Remember to use `global next_id` in create_quote to modify the global variable
- Use list comprehension to remove quotes: `QUOTES[:] = [q for q in QUOTES if q["id"] != quote_id]`
- Test each endpoint before moving to the next

## Common Mistakes

- Forgetting to raise HTTPException for 404 cases
- Not incrementing next_id after creating a quote
- Returning the quote instead of None for DELETE endpoint (should return None for 204)
- Not using `global next_id` in create_quote function
- Trying to modify QUOTES with `QUOTES = [...]` instead of `QUOTES[:] = [...]`
