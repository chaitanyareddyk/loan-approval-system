# Loan Approval System

## System Design and Architecture

The system follows a microservice-oriented architecture with the following components:

- **RESTful API**: FastAPI application to handle HTTP requests.
- **Celery Worker**: Asynchronous task queue to process loan applications and approve/reject them.
- **Database**: PostgreSQL for persistent data storage.
- **Message Broker**: Redis to mediate between the web server and Celery workers.

## Set Up and Installation

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL
- Redis

### Environment Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/chaitanyareddyk/loan-approval-system.git
   cd loan-approval-system
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the environment variables by copying the `.env.example` to `.env` and filling in the details for the database and Redis configurations.

5. Initialize the database by running the initial migration scripts to create the necessary tables.

### Running the System

1. Start the FastAPI application:
   ```sh
   uvicorn app.main:app --reload
   ```

2. In a new terminal, start the Celery worker:
   ```sh
   celery -A app.celery_worker worker --loglevel=info
   ```

3. The FastAPI server will be available at `http://127.0.0.1:8000`.

## Testing the System

To run the tests and generate coverage reports, execute the following command:

```sh
pytest
```

Ensure you are in the project's root directory when running tests.

## Documentation

Further documentation on API endpoints and usage can be found at `http://127.0.0.1:8000/docs` once the FastAPI server is running.