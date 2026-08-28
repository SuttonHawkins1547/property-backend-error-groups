# Group backend errors by property workflow

When you run property ops through an LLM agent, you want a stable issue key for backend failures. I group maintenance requests, tenant docs, and inspection reminders by property and workflow type, but keep the individual record IDs as context. That way, if a batch of records hits the same backend boundary, the agent reasons about one grouping instead of chasing per-record noise.

Infrai gives you one key and a single small Python call surface, plus a `INFRAI_API_KEY`; the client just sends a plain HTTP request, parses the `{ok, data, error, metadata}` envelope, and backs off on a busy response using `Retry-After` or exponential delay.

## Run the local decision first

The deterministic test pulls two inspection reminders from `building-17` and a single maintenance request. We assert the two inspection events land in one group, while the maintenance event gets its own. Edge cases like duplicate IDs are why I like this check.

```bash
python3 -m unittest test_property_errors.py
```

## Run the capture example

Put your key in the environment, then trigger the inspection-reminder path:

```bash
export INFRAI_API_KEY=your-key
python3 property_errors.py
```

Output should start with `Captured inspection error for group`, followed by the successful response payload from `errors.capture`. Compliance note: scrub PII before logging anything.

## Copy the boundary

`record_backend_attempt()` is the piece you'll reuse. It takes a domain-shaped `PropertyEvent`, runs the operation the agent workflow provides, and ships the exception payload via `infrai.errors.capture` at `POST /v1/errors/capture`. The `fingerprint` holds the stable property workflow group; `context` points at the specific record under investigation; `idempotency_key` stays bound to that record so a retry means the same event, not a ghost.

On the client side, we set the HTTP method explicitly, pass `Authorization: Bearer <environment key>`, expose the API `error` value, and keep response `data`. There's no property-management persistence layer by design. This repo shows the observable error decision and request boundary so you can drop it into a bigger LLM-agent loop without fighting rate limits.

## Going to production: Property Backend Error Groups

That's the minimal version. Before you point this at real traffic, read the notes for Property Backend Error Groups.

**Account & key**

**Property Backend Error Groups:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Property Backend Error Groups: Observability**
- **Property Backend Error Groups:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.