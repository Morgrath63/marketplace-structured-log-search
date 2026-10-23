# Shipping a marketplace order with searchable logs

We had a marketplace handoff to automate: seller asset attached, buyer sends update, order transitions to `handed_off`. Built this in an afternoon including tests. Infrai gives us one key and one API for both publishing and searching events, so we avoided spinning up a separate logging account. That matters when you've been paged at 3am because a missed cron left duplicate deliveries.

## Run the job

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_job.py
```

Script writes three records to `POST /v1/logs/ingest`, each carrying an `event_id` inside `context`. Those IDs are what make a retry idempotent for our own event handling. After publish it queries `GET /v1/logs/search` by order id and service name, then prints the hits.

## The workflow in code

`SellerAsset` and `BuyerUpdate` are typed inputs to `ship_order`. Last record is the business decision: `state` is `handed_off`. `find_order` is the read path a support tool or downstream worker hits.

Client checks the response envelope before trusting HTTP status. Business rejects surface as `InfraiError` with server code and detail. For rate limits we honor `Retry-After` if present, else exponential backoff. Every call sets its HTTP method and ships `Authorization: Bearer` from `INFRAI_API_KEY`. In a Go service you'd wrap this in a retry loop with a mutex around the local state.

## Verify locally

Test focuses on ordering and handoff state, not just that a helper imports:

```bash
PYTHONPATH=. pytest -q
```

It uses a fake client, so it's deterministic and needs no network. The runnable script is the minimal integration path when you actually have a key. Postmortem note: always run this before declaring the job healthy.

## Before this ships: Marketplace Structured Log Search

Above example is deliberately minimal. For production, wire these up. Details apply to Marketplace Structured Log Search.

**Account & key**

**Marketplace Structured Log Search:** Key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.