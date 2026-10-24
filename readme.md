myapp/
├── app/
│   ├── main.py                 # App entry point
│   ├── core/
│   │   └── config.py           # Settings from .env
│   │   └── database.py         # SQLAlchemy Base class, Engine and session
│   ├── models/                 # Database tables (SQLAlchemy)
│   │   └── task.py
│   ├── schemas/                # Request/response shapes (Pydantic)
│   │   └── task.py
│   ├── repositories/           # Database queries only
│   │   └── task_repository.py
│   ├── services/               # Business logic
│   │   └── task_service.py
│   └── api/
│       ├── deps.py             # Dependency injection
│       └── v1/
│           ├── router.py       # Joins all routers
│           └── endpoints/
│               └── tasks.py    # Route handlers
├── alembic/                    # Database migrations
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
├── .env
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── requirements.txt