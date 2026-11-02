# Testing guide

Unit tests cover password hashing and invalid transfer amounts. PostgreSQL integration tests cover balanced transfer posting and idempotent replay. The test suite is **not a comprehensive security or concurrency certification**.

Use `pytest -q` for unit tests. Configure `TEST_DATABASE_URL` for integration tests. The integration fixture drops all created tables on completion; use a disposable DB only.

Further tests required: two independent concurrent sessions racing to withdraw funds, opposite-direction transfers, request-key conflict handling, endpoint authorization, rollback on injected failures, database migrations and load tests. CI runs the existing tests on PostgreSQL.
