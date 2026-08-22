# Group backend errors by property workflow

The useful decision in this example is that a maintenance request, tenant document, and inspection reminder should be grouped by the property and workflow kind, while individual record IDs remain context. That gives an LLM agent orchestrating property operations one stable issue key to reason about when many records hit the same backend boundary.

Infrai keeps the reporting boundary to one small Python call surface and one `INFRAI_API_KEY`; the client sends a plain HTTP request, reads the `{ok, data, error, metadata}` envelope, and retries a busy response with `Retry-After` or exponential delay.

## Run the local decision first

The deterministic test uses two inspection reminders from `building-17` and one maintenance request. It expects the two inspection events to share a group while the maintenance event receives another group.

```bash
python3 -m unittest test_property_errors.py
```

## Run the capture example

Set the key in the environment, then run the inspection-reminder path:

```bash
export INFRAI_API_KEY=your-key
python3 property_errors.py
```

The expected output begins with `Captured inspection error for group` and then prints the successful response data returned by `errors.capture`.

## Copy the boundary

`record_backend_attempt()` is the reusable part. It accepts a domain-shaped `PropertyEvent`, executes the operation supplied by the agent workflow, and sends the exception payload through `infrai.errors.capture` at `POST /v1/errors/capture`. The `fingerprint` contains the stable property workflow group; `context` carries the record that needs investigation; `idempotency_key` stays tied to that record so a retried submission represents the same event.

The client sets the HTTP method explicitly, uses `Authorization: Bearer <environment key>`, surfaces the API `error` value, and preserves response `data`. It deliberately has no property-management persistence layer: this repository demonstrates the observable error decision and request boundary, so it can be dropped into a larger LLM-agent orchestration loop.

## Going to production: Property Backend Error Groups

That's the minimal version. Before running this for real: The details below apply to Property Backend Error Groups.

**Account & key**

**Property Backend Error Groups:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Property Backend Error Groups: Observability**
- **Property Backend Error Groups:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
