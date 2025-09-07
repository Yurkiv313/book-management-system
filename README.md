# 📚 Book Management System  

A REST API built with **FastAPI** and **PostgreSQL** to manage users, authors, and books.  
Includes authentication (JWT), pagination, sorting, rate-limiting, and test coverage.  

---

## 🚀 Features
- User registration, login, JWT authentication (access + refresh tokens)  
- CRUD operations for users, authors, and books  
- Pagination and sorting support  
- Rate limiting (throttling) with **slowapi**  
- Database migrations with **Alembic**  
- Unit tests with **pytest**, **pytest-asyncio**, and coverage reports  
- Preloaded sample data (`/data`) available for testing  

---

## 🛠️ Requirements
- Python **3.11+**  
- Docker + Docker Compose  
- PostgreSQL (runs via Docker)  

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone git@github.com:Yurkiv313/book-management-system.git
   cd book-management-system
   
2. **Create environment file**
   ```bash
   cp .env.sample .env

3. **Start PostgreSQL with Docker**
   ```bash
   docker compose up -d

4. **Create virtual environment and install dependencies**
   ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows PowerShell

    pip install -r requirements.txt

5. **Apply database migrations**
   ```bash
   python -m alembic upgrade head

6. **Run the application**
   ```bash
   python -m uvicorn src.main:app --reload
   
## 📂 Data Import
In the data/ folder you will find sample .json and .csv files.
They can be uploaded through the provided API endpoints to quickly populate the database.

## 📑 API Docs
Once the server is running, open in your browser:

Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

## 🧪 Running Tests
Run all tests with coverage:
   ```bash
   pytest --cov=src tests/
