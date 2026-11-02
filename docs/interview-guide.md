# FinCore interview questions and answers

### 1. What is ACID?

Atomicity, consistency, isolation, durability: PostgreSQL commits balance and postings together.

### 2. Why PostgreSQL?

Foreign keys, constraints, row locks and robust transactional semantics.

### 3. Why Decimal?

Binary floating-point is unsuitable for exact two-decimal financial values.

### 4. What is double-entry?

Each transfer posts equal debit and credit amounts.

### 5. How do you prevent overdrafts?

Lock the source row and verify funds before decrementing within the transaction.

### 6. What is idempotency?

Retrying a successful request with the same key and payload returns the original result.

### 7. How do you handle deadlocks?

Acquire account locks in a consistent ID order; production should add bounded retries.

### 8. What is a JWT?

A signed token carrying an authenticated subject and expiration.

### 9. Why hash passwords?

Store nonreversible password verifiers rather than plaintext.

### 10. Why FastAPI?

Typed validation, dependency injection and generated OpenAPI docs.

### 11. What is an index?

A structure that accelerates selected lookups with write/storage tradeoffs.

### 12. What is a foreign key?

A database-enforced relationship to a referenced row.

### 13. What is a race condition?

Outcome depends on interleaving concurrent operations.

### 14. What is row-level locking?

PostgreSQL FOR UPDATE blocks conflicting writes to selected rows.

### 15. What is rollback?

Discard uncommitted changes when an operation fails.

### 16. What is a database migration?

A versioned change to database structure.

### 17. Why Docker?

Reproducible application and service environments.

### 18. What is an API?

An interface exposing defined operations and data contracts.

### 19. What is HTTP 409?

A conflict with current resource state, such as insufficient funds.

### 20. What is a service layer?

Business logic separated from HTTP routing.

### 21. What is normalization?

Organizing relational tables to reduce redundancy and anomalies.

### 22. What is pagination?

Retrieving bounded subsets of a larger result set.

### 23. Why unit tests?

Fast verification of isolated behavior.

### 24. Why integration tests?

Verify interactions with real dependencies like PostgreSQL.

### 25. Why not SQLite for concurrency tests?

SQLite locking differs from PostgreSQL FOR UPDATE semantics.

### 26. What is caching?

Storing derived results for faster retrieval; balances must remain database-authoritative.

### 27. What is rate limiting?

Restricting request frequency to reduce abuse.

### 28. What is a connection pool?

Reusable database connections managed by the application.

### 29. What is SQL injection?

Untrusted input changing SQL meaning; use bound ORM parameters.

### 30. What is CORS?

Browser policy controlling cross-origin resource access.

### 31. What is authorization?

Determining whether a user may perform a specific action.

### 32. What is authentication?

Verifying who a user is.

### 33. What is a composite unique constraint?

Uniqueness across multiple columns such as actor and idempotency key.

### 34. What is p95 latency?

Latency below which 95 percent of requests fall.

### 35. What is CI?

Automated build and test checks triggered by code changes.

### 36. What is optimistic concurrency?

Conflict detection through version checks rather than early locks.

### 37. What is pessimistic concurrency?

Preventing conflicts by locking records before changes.

### 38. What is an audit log?

Record of security or business-relevant actions.

### 39. What is a compensating transaction?

New inverse postings instead of deleting original ledger history.

### 40. What is a modular monolith?

One deployable app divided into coherent modules.
