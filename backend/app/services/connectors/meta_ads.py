import httpx

from app.core.config import settings
from app.services.connectors.base import PlatformConnector


class MetaAdsConnector(PlatformConnector):
    name = "meta"

    def __init__(self) -> None:
        self.base_url = f"https://graph.facebook.com/{settings.meta_api_version}"
        self.token = settings.meta_access_token

    def sync_record(self, *, external_id: str, taxonomy_value: str, dry_run: bool = True) -> dict:
        payload = {"name": taxonomy_value}
        if dry_run:
            return {
                "status": "dry_run",
                "external_id": external_id,
                "request": payload,
                "response": {"message": "Dry-run: no changes pushed."},
            }

        url = f"{self.base_url}/{external_id}"
        params = {"access_token": self.token}
        with httpx.Client(timeout=30) as client:
            response = client.post(url, params=params, data=payload)
        return {
            "status": "success" if response.status_code < 300 else "failed",
            "external_id": external_id,
            "request": payload,
            "response": response.json() if response.content else {},
            "status_code": response.status_code,
        }
