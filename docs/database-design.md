# Database schema

- `users`: unique email, Argon2 password hash, role flag.
- `accounts`: user foreign key, currency, nonnegative cached balance, status, system flag.
- `transfers`: source/destination foreign keys, amount, actor, idempotency key, request hash, timestamp.
- `ledger_entries`: two postings per completed transfer, with account and transfer foreign keys.
- `audit_logs`: simple action audit events.

## Example SQL

```sql
SELECT a.id, a.balance, COUNT(t.id) AS outgoing_transfers
FROM accounts a LEFT JOIN transfers t ON t.source_id=a.id
GROUP BY a.id, a.balance;

SELECT transfer_id, SUM(CASE WHEN direction='credit' THEN amount ELSE -amount END) AS net
FROM ledger_entries GROUP BY transfer_id HAVING SUM(CASE WHEN direction='credit' THEN amount ELSE -amount END) <> 0;
```

The second query should return zero rows for correctly balanced committed transfers. Full immutable-ledger enforcement and cross-table balance reconciliation constraints are future work.
