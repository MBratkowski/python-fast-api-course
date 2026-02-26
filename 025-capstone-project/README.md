# Module 025: Capstone Project

## The Challenge

Build a complete, production-ready REST API from scratch. This project combines everything you've learned.

## Project Options

Choose one (or propose your own):

### Option A: Social Media API
Build a Twitter/Instagram-like backend:
- User registration & authentication
- Posts with images
- Following/followers
- Feed generation
- Likes and comments
- Real-time notifications

### Option B: E-Commerce API
Build a shopping backend:
- User accounts
- Product catalog
- Shopping cart
- Order processing
- Payment integration (Stripe)
- Order history

### Option C: Task Management API
Build a Trello/Asana-like backend:
- Workspaces and projects
- Tasks with assignments
- Due dates and priorities
- Comments and attachments
- Team collaboration
- Activity feed

## Requirements

Your project must include:

### Core Features
- [ ] User authentication (JWT)
- [ ] Role-based authorization
- [ ] Full CRUD for main resources
- [ ] Input validation with Pydantic
- [ ] Proper error handling

### Data Layer
- [ ] PostgreSQL database
- [ ] SQLAlchemy models with relationships
- [ ] Alembic migrations
- [ ] Redis caching

### Production Ready
- [ ] Comprehensive tests (80%+ coverage)
- [ ] Docker & docker-compose
- [ ] CI/CD pipeline
- [ ] API documentation
- [ ] Rate limiting
- [ ] Logging

### Bonus
- [ ] WebSocket feature
- [ ] File uploads
- [ ] Background tasks
- [ ] API versioning

## Project Structure

```
capstone/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── [resources].py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── .github/workflows/
└── README.md
```

## Evaluation Criteria

1. **Functionality** - Does it work?
2. **Code Quality** - Is it clean and well-organized?
3. **Testing** - Is it well-tested?
4. **Documentation** - Can someone else understand it?
5. **Production Readiness** - Could this be deployed?

## Timeline Suggestion

1. **Planning** - Design API, database schema
2. **Core Setup** - Project structure, auth, database
3. **Main Features** - CRUD operations
4. **Advanced Features** - Caching, background tasks
5. **Testing & Polish** - Tests, documentation
6. **Deployment** - Docker, CI/CD

## Getting Help

Stuck? Try:
1. Review the relevant module
2. Check FastAPI documentation
3. Search Stack Overflow
4. Ask for a code review

Good luck! 🚀
