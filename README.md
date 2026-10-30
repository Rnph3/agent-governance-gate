# Durable Agent Gate — Local Proof of Concept

This code is **not a production agent platform**. It is a small, runnable demonstration of durable local state, rejection of forbidden actions, human-gated *simulation*, and replayable audit logs using Python/SQLite.

Run: `python3 -m unittest discover -s tests -v` then `python3 examples/demo.py`.

It has **no external side effects** and **does not contain a path for trading, payments, outbound contact, or shared-system commitment writes**. It does not validate reviewer identity, implement MCP, LLM, cloud deployment or CI. The manual string in `approve` is only a demo assertion, not an auth mechanism. The policy table is an illustrative implementation of safe defaults.

Concept mapping: durable queue state -> SQLite persistence; review gate -> explicit `APPROVED_FOR_SIMULATION` status; audit -> an `audit` table that the code only ever inserts into (not tamper-proof: SQLite does not prevent updates or deletes); forbidden actions -> structural rejection.

## Not implemented

Production usage, a durable worker queue, verified human identity, a policy engine, signed audit logs, concurrency control, observability, CI, MCP/LLM integration and cloud deployment.

## Test results (2026-10-30, local)

- `python3 -m unittest discover -s tests -v`: 4 tests, OK (tested on Python 3.14.0a3, macOS).
- `python3 examples/demo.py`: unreviewed `PUBLISH_PREVIEW` blocked; after demo approval returns a local JSON preview with `external_effects: False`; `TRADE` is `BLOCKED`; 5 audit events recorded.

## License

See `LICENSE`.
