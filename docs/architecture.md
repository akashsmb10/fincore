# Architecture and engineering tradeoffs

A modular monolith keeps this project understandable. FastAPI handles request validation and routing, SQLAlchemy models relational data, PostgreSQL enforces balance constraints and transactional consistency, and JWT identifies the authenticated actor. Redis is provisioned but not wired into application code.

**Transaction lifecycle:** authenticate actor → verify source ownership → acquire actor row lock → check idempotency key → acquire both account row locks in ID order → validate balances and statuses → update cached account balances → create one transfer and two ledger entries → commit. A failed step rolls back the entire transaction.

**Concurrency:** locking the actor row serializes requests made by the same actor. Ordered account locks protect balances from concurrent actors. For production use, add explicit serialization retry handling, transaction isolation tests and stronger database-level ledger constraints.

**Idempotency:** uniqueness `(actor_id, idempotency_key)` plus request digest. The actor lock ensures same-user concurrent retries serialize. Successful replay returns original transfer ID without a second posting. Failed operations are not persisted as completed requests.

**Accounting limitation:** The system clearing account represents demo funding and withdrawal without a real external funding source. It is not a production-grade ledger. Entries are treated as immutable by the application but database permissions/triggers do not yet enforce append-only behavior.
