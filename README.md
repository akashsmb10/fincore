# FinCore — Secure Banking Transaction Simulation

Educational Python/FastAPI backend demonstrating relational database design, double-entry postings, transactional transfer logic, row locking, idempotent requests, authentication, Docker and automated tests. **Not a real banking system.** No real funds or payment integrations.

## Quick start

1. Copy `.env.example` to `.env` and replace `JWT_SECRET` with a secure random value.
2. Run `docker compose up --build` (Docker with Compose required).
3. Visit `http://localhost:8000/docs` for Swagger UI.
4. Register using `POST /auth/register`, log in using `POST /auth/login` and click **Authorize** in Swagger using the bearer token.
5. Create two accounts using `POST /accounts`.
6. In the demo environment, use `POST /funding` with `Idempotency-Key: demo-fund-0001` and `{ "account_id": "<your-account-id>", "amount": "1000.00" }`.
7. Transfer using `POST /transfers` with a new idempotency key and `{ "source_id": "...", "destination_id": "...", "amount": "50.00" }`.

## Architecture

FastAPI routes → authentication and service layer → PostgreSQL accounts, transfers and immutable ledger entries. PostgreSQL is authoritative; Redis container is provided but **not yet integrated into rate limiting or caching**. The current implementation uses a user-row lock to serialize each user's transfer requests and ordered account row locks to avoid common deadlocks. Financial values use `Decimal` and `NUMERIC(18,2)`.

## Current scope and limitations

- Supported: registration/login, JWT, account creation/listing, balance retrieval, freezing, simulated funding/withdrawal, transfers, history, basic audit log, ledger entries, idempotent request replay and PostgreSQL row locking.
- **Not yet implemented:** Redis-backed rate limiting, reversal endpoint, admin workflows, token refresh/revocation, full concurrency stress suite, load benchmarking, observability, advanced security hardening. Do not claim these are complete.
- Funding is gated by `ENABLE_SIMULATED_FUNDING`; disable it outside a local demo. A system clearing account is modeled with an unlimited simulated source/sink and a zero cached balance. This is a demo simplification, not a real-world general ledger.
- For correctness, use PostgreSQL; SQLite does not provide the same row-lock semantics.
- Only INR with two decimal places is supported. Database schema is initialized via Alembic. Migrations are intended for a fresh demo database.

## Tests

`pip install -e '.[dev]' && pytest -q`

PostgreSQL integration test: set `TEST_DATABASE_URL` to a **dedicated disposable** PostgreSQL database before running `pytest -q`. The integration fixture creates and drops tables, so **never point it at an important database**.

## Interview discussion

See `docs/interview-guide.md` and `docs/architecture.md` for architecture decisions, transaction consistency and technical interview questions.
