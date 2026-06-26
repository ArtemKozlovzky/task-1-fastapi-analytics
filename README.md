Task1

FastAPI application that provides car offers from a PostgreSQL database through a REST API with interactive Swagger UI documentation.

Prerequisites
Docker
Docker Compose
Quick Start

Clone the repository:

git clone https://github.com/ArtemKozlovzky/task-1-fastapi-analytics
cd Task1

Copy the environment file and fill in the required values:

cp .env.example .env

Build and start the application:

docker compose up --build

This command will:

start the PostgreSQL database;
run database migrations;
start the FastAPI application.

Open the Swagger UI:

http://localhost:8000/docs
or
http://127.0.0.1:8000/docs

Running Tests

Run the test suite inside the application container:

docker compose exec app pytest

Project Structure
.
├── app/                 # FastAPI application source code
│   ├── cars_hub/        # API endpoints that communicate with CarsHub API
│   ├── routes/          # API endpoints
│   └── utils/           # Utility modules
├── db/
│   └── queries/         # Database initialization scripts and SQL queries
├── tests/               # Automated tests
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
└── requirements.txt     # Python dependencies