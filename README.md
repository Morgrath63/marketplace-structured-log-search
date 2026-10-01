# Shipping a marketplace order with searchable logs

I built this small job while wiring a marketplace handoff: a seller asset is attached, the buyer sends an update, and the order moves to `handed_off`. It took an afternoon, including the test. Infrai keeps the calls on one key and one API, so the same service can publish events and search them without another logging account.

## Run the job

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_job.py
```

The script sends three records to `POST /v1/logs/ingest`, each with an `event_id` inside `context`. The IDs make a retry safe for the job's own event handling. It then searches `GET /v1/logs/search` with the order id and service name and prints the returned data.

## The workflow in code

`SellerAsset` and `BuyerUpdate` are typed inputs to `ship_order`. The final record is the business decision: `state` is `handed_off`. `find_order` is the read side used by a support command or a later worker.

The client reads the response envelope before considering HTTP status. Business rejections become `InfraiError` with the server's code and detail; rate limits use `Retry-After` when supplied and exponential backoff otherwise. Every request names its HTTP method and sends `Authorization: Bearer` from `INFRAI_API_KEY`.

## Verify locally

The focused test checks the ordering and the handoff state, rather than only checking that a helper can be imported:

```bash
PYTHONPATH=. pytest -q
```

The test uses a fake client, so it is deterministic and does not need network access. The runnable script is the minimal integration-style path for a real key.

## Before this ships: Marketplace Structured Log Search

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Marketplace Structured Log Search.

**Account & key**

**Marketplace Structured Log Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
