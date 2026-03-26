from typing import List, Optional
from ..client import ChanomhubClient
from ..models.common import Mod, ModCreate

class ModRepository:
    def __init__(self, client: ChanomhubClient):
        self.client = client

    def create(self, article_slug: str, mod: ModCreate) -> Mod:
        data = self.client.rest_fetch(
            f"/api/mods/article/{article_slug}",
            method="POST",
            json=mod.model_dump(by_alias=True, exclude_none=True)
        )
        # The backend returns { mod: ModResponseDto }
        mod_data = data.get("mod") if isinstance(data, dict) else data
        return Mod.model_validate(mod_data)
