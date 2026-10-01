from marketplace_job import BuyerUpdate, SellerAsset, ship_order
from infrai_client import InfraiClient


class FakeClient:
    def __init__(self):
        self.events = []

    def ingest_log(self, event):
        self.events.append(event)


def test_handoff_emits_ordered_business_events():
    client = FakeClient()
    events = ship_order(client, "order-1", SellerAsset("asset-1", "banner"), BuyerUpdate("buyer-1", "ship it"))
    assert [event["context"]["event_id"] for event in events] == ["order-1:asset", "order-1:buyer", "order-1:handoff"]
    assert events[-1]["context"]["state"] == "handed_off"
    assert client.events == events


def test_ingest_uses_entries_request_field(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    client = InfraiClient()
    calls = []
    monkeypatch.setattr(client, "call", lambda *args: calls.append(args))
    event = {"message": "order handed off", "level": "info", "service": "marketplace-job"}

    client.ingest_log(event)

    assert calls == [("POST", "/v1/logs/ingest", {"entries": [event]})]
