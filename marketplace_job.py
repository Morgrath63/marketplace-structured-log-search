from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient


@dataclass(frozen=True)
class SellerAsset:
    asset_id: str
    title: str


@dataclass(frozen=True)
class BuyerUpdate:
    buyer_id: str
    note: str


def ship_order(client: InfraiClient, order_id: str, asset: SellerAsset, update: BuyerUpdate) -> list[dict[str, Any]]:
    events = [
        {"message": "seller asset attached", "level": "info", "service": "marketplace-job", "context": {"event_id": f"{order_id}:asset", "order_id": order_id, "asset_id": asset.asset_id, "title": asset.title}},
        {"message": "buyer update received", "level": "info", "service": "marketplace-job", "context": {"event_id": f"{order_id}:buyer", "order_id": order_id, "buyer_id": update.buyer_id, "note": update.note}},
        {"message": "order handed off", "level": "info", "service": "marketplace-job", "context": {"event_id": f"{order_id}:handoff", "order_id": order_id, "state": "handed_off"}},
    ]
    for event in events:
        client.ingest_log(event)
    return events


def find_order(client: InfraiClient, order_id: str) -> dict:
    return client.search_logs(order_id, "marketplace-job")


if __name__ == "__main__":
    api = InfraiClient()
    ship_order(api, "order-1042", SellerAsset("asset-77", "logo pack"), BuyerUpdate("buyer-9", "Please include SVG"))
    result = find_order(api, "order-1042")
    print(f"Found marketplace events: {result}")
