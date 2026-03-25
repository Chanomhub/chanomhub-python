from typing import Optional, Callable
from pydantic import BaseModel, Field

class ChanomhubConfig(BaseModel):
    api_url: str = Field("https://api.chanomhub.com", alias="apiUrl")
    token: Optional[str] = None
    refresh_token: Optional[str] = Field(None, alias="refreshToken")
    storage_download_url: str = Field("https://storage.chanomhub.com", alias="storageDownloadUrl")
    cdn_url: str = Field("https://imgproxy.chanomhub.com", alias="cdnUrl")
    default_cache_seconds: int = Field(3600, alias="defaultCacheSeconds")
    on_token_refreshed: Optional[Callable[[str, str], None]] = Field(None, alias="onTokenRefreshed")

    class Config:
        populate_by_name = True
