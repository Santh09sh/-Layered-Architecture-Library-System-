# 📚 LibraryOS — Intelligent Library Management System

> Modern university library management platform with **Layered Architecture**, **Entity Graph**, and **AI Agent**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                  │
│     React + TypeScript + Tailwind + ReactFlow    │
├─────────────────────────────────────────────────┤
│              Application Layer                   │
│    FastAPI Routes + Schemas + Auth Middleware     │
├─────────────────────────────────────────────────┤
│              Business Layer                      │
│   Services (Auth, Book, Borrowing, Fines, etc.)  │
├─────────────────────────────────────────────────┤
│               Domain Layer                       │
│      Entities + Enums + Relationships            │
├─────────────────────────────────────────────────┤
│             Data Access Layer                    │
│     SQLAlchemy Repositories + Graph Service      │
├─────────────────────────────────────────────────┤
│                AI Agent Layer                    │
│   LLM Provider + Tool Registry + Reasoning      │
└─────────────────────────────────────────────────┘
```

### Strict Layered Separation
- **Presentation** → talks to Application only
- **Application** → validates input, delegates to Business
- **Business** → contains ALL business rules (borrowing limits, fines, eligibility)
- **Domain** → entity models, enums, no logic
- **Data Access** → generic repository pattern, SQL queries
- **AI Agent** → orchestrates tools backed by real database queries

---

## ✨ Features

### 📖 Library Management
- **Book Catalogue** — Search, filter by category, availability toggle
- **Book Details** — Cover images, reviews, copy locations, borrow actions
- **Circulation** — Borrow, return, renew with eligibility checks
- **Reservations** — Queue-based reservation system
- **Fines** — Auto-calculated late fees, payment tracking
- **Reviews** — Star ratings and text reviews per book

### 🕸️ Entity Graph
- **Interactive Visualization** — ReactFlow-powered graph with color-coded nodes
- **Entity Types** — Users, Books, Authors, Publishers, Categories, Book Copies
- **Relationship Edges** — WROTE, PUBLISHED, CATEGORIZED, BORROWED
- **Search & Filter** — Query entities and filter by type
- **Recommendations** — Graph-based book recommendations

### 🤖 AI Agent (LibraryAI)
- **Natural Language Chat** — Ask questions about books, availability, fines
- **12 Tools** — search_books, recommend_books, check_availability, get_statistics, etc.
- **Reasoning Pipeline** — Intent → Tool Selection → Execution → Response
- **Tool Transparency** — See which tools were called and their results
- **Dual Provider** — Google Gemini (production) or Mock (demo)

### 🔐 Authentication & Authorization
- **JWT Authentication** — Secure token-based auth
- **Role-Based Access** — Admin, Librarian, Student roles
- **Protected Routes** — Role-specific API endpoints

### 📊 Analytics Dashboard
- **Overview Stats** — Total books, active borrows, overdue count, fines
- **Borrowing Trends** — Monthly borrowing chart
- **Popular Categories** — Category distribution pie chart
- **Role-Aware** — Admins/Librarians see analytics, Students see personal dashboard

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Tailwind CSS v4, ReactFlow, Recharts |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | SQLite (dev), PostgreSQL-ready |
| AI | Google Gemini API (optional), Mock provider for demo |
| Auth | JWT (python-jose), bcrypt password hashing |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Seed the database with demo data
python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from app.seed_data import seed; seed()"
# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@library.edu | admin123 |
| Librarian | sarah@library.edu | librarian123 |
| Student | vishnu@university.edu | student123 |

> All 20 students use password: `student123`

---

## 📁 Project Structure

```
SE Project/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Pydantic settings
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   ├── seed_data.py               # Demo data seeder
│   │   ├── domain/                    # Domain Layer
│   │   │   ├── enums.py               # UserRole, BorrowStatus, etc.
│   │   │   └── entities/              # SQLAlchemy models (12 entities)
│   │   ├── data_access/               # Data Access Layer
│   │   │   ├── base_repository.py     # Generic CRUD repository
│   │   │   └── *_repository.py        # Entity-specific queries
│   │   ├── business/                  # Business Layer
│   │   │   ├── auth_service.py        # JWT + password hashing
│   │   │   ├── book_service.py        # Book CRUD + search
│   │   │   ├── borrowing_service.py   # Borrow rules + eligibility
│   │   │   ├── fine_service.py        # Fine calculation + payment
│   │   │   └── ...                    # 9 services total
│   │   ├── graph/                     # Entity Graph
│   │   │   ├── models.py              # GraphNode, GraphEdge, GraphData
│   │   │   └── graph_service.py       # Graph construction + search
│   │   ├── ai/                        # AI Agent
│   │   │   ├── llm_provider.py        # Abstract LLM interface
│   │   │   ├── gemini_provider.py     # Gemini + Mock implementations
│   │   │   ├── tool_registry.py       # 12 tools backed by real data
│   │   │   └── agent.py               # Reasoning pipeline
│   │   └── application/               # Application Layer
│   │       ├── dependencies.py        # Auth dependencies + RBAC
│   │       ├── schemas/               # Pydantic request/response DTOs
│   │       ├── routes/                # FastAPI routers (6 modules)
│   │       └── middleware/            # Error handler
│   ├── .env                           # Configuration
│   └── requirements.txt               # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── main.tsx                   # React entry
    │   ├── App.tsx                    # Router + auth protection
    │   ├── api.ts                     # Axios HTTP client
    │   ├── AuthContext.tsx            # JWT auth state
    │   ├── index.css                  # Global styles + glassmorphism
    │   ├── components/
    │   │   └── Layout.tsx             # Sidebar + top bar shell
    │   └── pages/
    │       ├── LoginPage.tsx          # Login + register
    │       ├── DashboardPage.tsx      # Stats + charts
    │       ├── BooksPage.tsx          # Book catalogue
    │       ├── BookDetailPage.tsx     # Book detail + borrow
    │       ├── BorrowedPage.tsx       # Circulation management
    │       ├── FinesPage.tsx          # Fine management
    │       ├── GraphPage.tsx          # Entity graph (ReactFlow)
    │       └── AgentPage.tsx          # AI chat interface
    └── vite.config.ts                 # Vite + Tailwind + proxy
```

---

## 🔑 Entity Relationship Diagram

```
User ──1:N──> BorrowRecord ──N:1──> BookCopy ──N:1──> Book
User ──1:N──> Reservation ──N:1──> Book
User ──1:N──> Review ──N:1──> Book
User ──1:N──> Fine ──N:1──> BorrowRecord
User ──1:N──> Notification
Book ──M:N──> Author (via book_authors)
Book ──N:1──> Publisher
Book ──N:1──> Category
Book ──1:N──> BookCopy
```

---

## 🧪 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | — | Login |
| POST | `/api/auth/register` | — | Register |
| GET | `/api/auth/me` | ✅ | Get profile |
| GET | `/api/books` | — | List/search books |
| GET | `/api/books/{id}` | — | Book details |
| POST | `/api/books` | 🔒 Librarian | Create book |
| POST | `/api/borrow` | ✅ | Borrow a copy |
| POST | `/api/borrow/{id}/return` | ✅ | Return book |
| POST | `/api/borrow/{id}/renew` | ✅ | Renew book |
| POST | `/api/reservations` | ✅ | Reserve book |
| GET | `/api/fines/my` | ✅ | My fines |
| POST | `/api/fines/{id}/pay` | ✅ | Pay fine |
| POST | `/api/reviews` | ✅ | Write review |
| GET | `/api/graph/me` | ✅ | My entity graph |
| GET | `/api/graph/search?q=` | ✅ | Search graph |
| POST | `/api/agent/chat` | ✅ | Chat with AI |
| GET | `/api/analytics/overview` | 🔒 Librarian | Dashboard stats |

---

## 📐 Design Patterns Used

1. **Repository Pattern** — Generic `BaseRepository<T>` with entity-specific extensions
2. **Service Layer Pattern** — Business rules encapsulated in service classes
3. **DTO Pattern** — Pydantic schemas separate API contracts from domain models
4. **Strategy Pattern** — LLM provider abstraction (Gemini/Mock)
5. **Tool Pattern** — AI agent tool registry for controlled data access
6. **Observer-like** — Notification service triggered by business events
7. **Factory** — LLM provider selection based on configuration
8. **Dependency Injection** — FastAPI `Depends()` for DB sessions and auth
