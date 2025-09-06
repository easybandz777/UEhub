# UE Hub - Upper Echelon Hub

A modular, extensible monorepo for inventory management and OSHA training with pluggable architecture.

## Architecture Principles

- **Domain-Driven Modules**: Each domain (inventory, training, auth, etc.) is a self-contained module
- **Ports & Adapters**: Business logic depends on interfaces, not concrete implementations
- **Dependency Injection**: Adapters are injected via FastAPI dependencies
- **Event-Driven**: Cross-module communication via domain events (in-process + Redis)
- **Versioned API**: `/v1/*` with OpenAPI spec and generated clients
- **Config-Driven**: All integrations configurable via environment variables

## Tech Stack

### Frontend
- **Next.js 14** (TypeScript, App Router)
- **Tailwind CSS** + **shadcn/ui**
- **React Hook Form** + **Zod**
- **Zustand** (state management)
- **ECharts** (data visualization)

### Backend
- **FastAPI** (Python 3.11)
- **SQLAlchemy 2.x** + **Alembic**
- **Pydantic v2**
- **Redis** (events/caching)
- **RQ** (background jobs)

### Database
- **Neon Postgres** with JSONB support
- **pg_trgm** for full-text search

### Infrastructure
- **Frontend**: Vercel deployment
- **Backend**: Fly.io/Cloud Run
- **Observability**: Sentry integration
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- pnpm 8+
- PostgreSQL (or use Neon)
- Redis

### Installation

```bash
# Install dependencies
pnpm install

# Set up backend environment
cd backend
cp .env.example .env
# Edit .env with your database and Redis URLs

# Run migrations
make migrate

# Seed initial data
make seed

# Start development servers
pnpm dev
```

### Development Commands

```bash
# Backend API server
make api

# Database migrations
make migrate

# Seed data
make seed

# Background worker
make worker

# Generate TypeScript SDK
make sdk

# Run all services
pnpm dev
```

## Module Structure

### Backend Modules

Each module follows the same structure:
```
modules/<module_name>/
├── router.py      # FastAPI routes
├── service.py     # Business logic
├── repository.py  # Data access
├── schemas.py     # Pydantic models
├── events.py      # Domain events (optional)
└── __init__.py
```

### Frontend Features

Feature-sliced architecture:
```
features/
├── core/          # Auth, layout, navigation
├── inventory/     # Inventory management
├── training/      # Training modules
├── reporting/     # Analytics and reports
└── webhooks/      # Webhook management
```

## Adding a New Module

### Backend Module Checklist

1. **Create module structure**:
   ```bash
   mkdir -p backend/app/modules/<module_name>
   touch backend/app/modules/<module_name>/{__init__.py,router.py,service.py,repository.py,schemas.py}
   ```

2. **Define database models** in `repository.py`

3. **Create Alembic migration**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "<module_name>_init"
   ```

4. **Register router** in `backend/app/api.py`:
   ```python
   from app.modules.<module_name>.router import router as <module_name>_router
   app.include_router(<module_name>_router, prefix="/v1/<module_name>", tags=["<module_name>"])
   ```

5. **Add event handlers** (if needed) in `app/core/events.py`

6. **Create frontend feature**:
   ```bash
   mkdir -p frontend/src/features/<module_name>
   ```

7. **Add feature flag** (if gated):
   ```sql
   INSERT INTO feature_flag (key, enabled, payload) VALUES ('<module_name>', true, '{}');
   ```

### Frontend Feature Checklist

1. **Create feature directory** with components
2. **Add routes** in `frontend/src/app`
3. **Use generated SDK** from `packages/sdk-js`
4. **Follow import boundaries** (only import from `features/core` and shared packages)

## Module Boundaries

### Import Rules

- **Backend**: Modules cannot import each other's internals
- **Frontend**: Features can only import from `features/core` and shared packages
- **Communication**: Use domain events or API calls between modules

### Dependency Flow

```
Business Logic (Services)
       ↓
   Interfaces (Ports)
       ↓
Concrete Adapters (Infrastructure)
```

## Event System

### Publishing Events

```python
# In a service
await self.events.publish("training.attempt.passed", {
    "attempt_id": attempt.id,
    "user_id": attempt.user_id,
    "score": attempt.score
})
```

### Subscribing to Events

```python
# In another module's service
@self.events.subscribe("training.attempt.passed")
async def handle_training_passed(payload: dict):
    # Generate certificate
    pass
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key
- `SENTRY_DSN`: Error tracking (optional)
- `STORAGE_BACKEND`: `local` or `s3`
- `MAIL_BACKEND`: `console` or `resend`

### Feature Flags

Control feature availability via the `feature_flag` table:

```sql
-- Enable/disable modules
UPDATE feature_flag SET enabled = false WHERE key = 'reporting';

-- Configure feature behavior
UPDATE feature_flag SET payload = '{"max_items": 1000}' WHERE key = 'inventory';
```

## API Documentation

- **OpenAPI Spec**: `http://localhost:8000/docs`
- **Generated Types**: Available in `packages/types`
- **SDK Client**: Available in `packages/sdk-js`

## Testing

```bash
# Run all tests
pnpm test

# Backend tests only
cd backend && python -m pytest

# Frontend tests only
cd frontend && pnpm test
```

## Deployment

### Backend (Fly.io)

```bash
cd backend
fly deploy
```

### Frontend (Vercel)

Automatic deployment via GitHub integration.

### Environment Setup

1. **Database**: Set up Neon Postgres instance
2. **Redis**: Configure Redis instance
3. **Storage**: Set up S3 bucket (optional)
4. **Email**: Configure Resend API key (optional)

## Troubleshooting

### Common Issues

1. **Module import errors**: Check import boundaries and dependencies
2. **Database connection**: Verify `DATABASE_URL` and network access
3. **Event delivery**: Check Redis connection and worker status
4. **SDK generation**: Ensure backend is running when generating types

### Debug Commands

```bash
# Check module dependencies
pnpm dlx depcruise --validate .dependency-cruiser.js src

# Verify database connection
cd backend && python -c "from app.core.db import engine; print(engine.url)"

# Test Redis connection
redis-cli ping
```

## Contributing

1. Follow module boundaries strictly
2. Add tests for new features
3. Update OpenAPI documentation
4. Regenerate SDK after API changes
5. Update feature flags as needed

## License

MIT License - see LICENSE file for details.
