# Failure modes and limits

- Unknown action types fail closed.
- `TRADE`, `PAYMENT`, `WRITE_SHARED_COMMITMENT`, `EXTERNAL_MESSAGE` cannot be approved or executed.
- `PUBLISH_PREVIEW` cannot execute even as a local simulation before approval.
- SQLite holds an insert-only (by convention, not enforced) audit record of request, approval, denied, and simulated events.
- Tests cover durable restart, forbidden behavior, approval, unknown types.
- No user identity proof, signed audit log, process isolation, retries, idempotency, concurrent workers, secret management or real remote API is implemented.
