# Service Boundaries

## Why This Matters

On iOS, you decide which functionality goes into which Swift Package module. On Android, you define Gradle module boundaries. Get it wrong, and you end up with circular dependencies, modules that import everything from each other, and refactoring nightmares.

Service boundaries in microservices are the same concept at a higher level -- but the cost of getting it wrong is much higher. Changing a module boundary is a code refactor. Changing a service boundary means migrating databases, updating API contracts, and coordinating multiple team deployments.

## Domain-Driven Design Basics

Domain-Driven Design (DDD) provides a framework for finding natural service boundaries. The key concept is the **bounded context** -- a boundary within which a specific model and vocabulary apply.

### Bounded Contexts

```
E-Commerce System

┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  User Context   │  │  Order Context    │  │ Product Context │
│                 │  │                   │  │                 │
│  User           │  │  Order            │  │  Product        │
│  - id           │  │  - id             │  │  - id           │
│  - name         │  │  - user_id        │  │  - name         │
│  - email        │  │  - items[]        │  │  - price        │
│  - password     │  │  - total          │  │  - description  │
│  - address      │  │  - status         │  │  - inventory    │
│                 │  │                   │  │                 │
│  Profile        │  │  "User" here =    │  │  "User" here =  │
│  - avatar       │  │  just user_id     │  │  not relevant   │
│  - bio          │  │  (not full User)  │  │                 │
└─────────────────┘  └──────────────────┘  └─────────────────┘
```

**Key insight:** The word "User" means different things in different contexts:
- In User Context: full profile with authentication details
- In Order Context: just an ID to associate with orders
- In Product Context: not relevant at all

Each bounded context has its own model of the world.

## One Database Per Service

The most important rule of microservices: **each service owns its own data**.

```
WRONG: Shared Database

Service A ──┐
             ├──→ Shared PostgreSQL ← Tight coupling!
Service B ──┘                         Schema change breaks both

RIGHT: Database Per Service

Service A ──→ Database A    Independent schemas
Service B ──→ Database B    Independent migrations
```

**Why this matters:**
- Shared databases create hidden coupling
- Schema changes in one service can break another
- You cannot independently deploy or scale services
- Database becomes a single point of failure

```python
# WRONG: Order service directly queries user table
async def get_order_with_user(order_id: int, db: Session):
    result = db.execute(
        text("""
            SELECT o.*, u.name as user_name
            FROM orders o
            JOIN users u ON o.user_id = u.id  -- Accessing another service's table!
            WHERE o.id = :id
        """),
        {"id": order_id},
    )
    return result.fetchone()

# RIGHT: Order service calls user service via HTTP
async def get_order_with_user(order_id: int, db: Session):
    order = await get_order(order_id, db)

    # Call user service API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://user-service:8001/users/{order.user_id}",
            timeout=5.0,
        )
        user = response.json()

    return {**order, "user_name": user["name"]}
```

## Shared-Nothing Architecture

Services should share nothing -- no database, no file system, no in-memory state:

```
┌──────────────┐     ┌──────────────┐
│ User Service │     │ Order Service│
│              │     │              │
│ Own code     │     │ Own code     │
│ Own database │     │ Own database │
│ Own cache    │     │ Own cache    │
│ Own config   │     │ Own config   │
│ Own logs     │     │ Own logs     │
└──────┬───────┘     └──────┬───────┘
       │                     │
       └────── API ──────────┘
       (HTTP or messages only)
```

## Identifying Service Boundaries

### Step 1: List Business Capabilities

For an e-commerce system:
- User management (registration, login, profiles)
- Product catalog (listing, search, details)
- Order processing (cart, checkout, payment)
- Notifications (email, push, SMS)
- Shipping (tracking, delivery estimates)

### Step 2: Group by Data Ownership

Each capability owns specific data:

| Capability | Owns | Does NOT Own |
|-----------|------|-------------|
| User Service | users, profiles, addresses | -- |
| Product Service | products, categories, inventory | -- |
| Order Service | orders, order_items, payments | users (reference by ID) |
| Notification Service | notification_preferences, templates | users (reference by ID) |

### Step 3: Check for Independence

Ask these questions:
- Can this capability be deployed independently? If no, the boundary is wrong.
- Does this capability have a single team owner? If shared, reconsider the split.
- Does this capability have different scaling needs? If yes, good boundary.

### Example: Splitting a Monolith

```python
# BEFORE: Monolith with everything in one app
# main.py
app = FastAPI()

# User routes
@app.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # ... user creation logic
    pass

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # ... user retrieval logic
    pass

# Order routes (in same app, same database)
@app.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Directly queries user table
    user = db.query(UserModel).filter(UserModel.id == order.user_id).first()
    # ... order creation logic
    pass
```

```python
# AFTER: Two separate services

# user_service/main.py
user_app = FastAPI()

@user_app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email}

# order_service/main.py
order_app = FastAPI()

@order_app.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Call user service instead of direct DB query
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://user-service:8001/users/{order.user_id}",
            timeout=5.0,
        )
        if response.status_code == 404:
            raise HTTPException(status_code=400, detail="User not found")

    # Create order in order service's own database
    new_order = OrderModel(**order.model_dump())
    db.add(new_order)
    db.commit()
    return new_order
```

## Anti-Pattern: The Distributed Monolith

The worst outcome: services that are deployed separately but tightly coupled.

**Symptoms:**
- Changing one service requires changing multiple others
- Services share a database
- You must deploy services in a specific order
- One service going down cascades failures everywhere

```
Distributed Monolith (AVOID):

Service A ──→ Service B ──→ Service C ──→ Service D
  Every request passes through all services
  = slower than a monolith with more complexity
```

## Mobile Analogy

Think of service boundaries like module boundaries in your mobile projects:

**Swift Package modules:**
```
MyApp/
├── UserModule/         → User Service
│   ├── Models/
│   ├── Services/
│   └── Package.swift   → Service API definition
├── OrderModule/        → Order Service
│   ├── Models/
│   ├── Services/
│   └── Package.swift
└── App/                → API Gateway
    └── AppDelegate.swift
```

**Multi-module Gradle project:**
```
app/
├── :user-feature/      → User Service
├── :order-feature/     → Order Service
├── :core-network/      → Shared communication layer
└── :app/               → API Gateway
```

The same principles apply: modules should have clear interfaces, own their data, and avoid circular dependencies.

## Key Takeaways

1. **Bounded contexts** define natural service boundaries -- where the vocabulary and models change
2. **One database per service** is the most important rule -- shared databases are hidden coupling
3. **Services communicate via APIs** (HTTP or messages), never by accessing each other's data directly
4. **Check independence**: if you cannot deploy a service without deploying another, the boundary is wrong
5. **A distributed monolith** is worse than a real monolith -- all the complexity, none of the benefits
6. **Start with clear module boundaries** in your monolith -- it makes future extraction straightforward
