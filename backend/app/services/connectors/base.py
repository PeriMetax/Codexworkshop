from abc import ABC, abstractmethod


class PlatformConnector(ABC):
    name: str

    @abstractmethod
    def sync_record(self, *, external_id: str, taxonomy_value: str, dry_run: bool = True) -> dict:
        raise NotImplementedError
