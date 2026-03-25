from typing import List, Optional, Union, TypeVar, Generic
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar("T")

class ListOptions(BaseModel):
    limit: Optional[int] = None
    offset: Optional[int] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")

    class Config:
        populate_by_name = True

class NamedEntity(BaseModel):
    id: str
    name: str

class ImageObject(BaseModel):
    id: Optional[str] = None
    url: str

class Author(BaseModel):
    id: Optional[int] = None
    name: str
    username: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[str] = None
    background_image: Optional[str] = Field(None, alias="backgroundImage")
    following: Optional[bool] = None
    social_media_links: Optional[List[dict]] = Field(None, alias="socialMediaLinks")

    class Config:
        populate_by_name = True

class Download(BaseModel):
    id: Union[int, str]
    name: str
    url: str
    is_active: bool = Field(..., alias="isActive")
    vip_only: bool = Field(..., alias="vipOnly")
    created_at: Optional[str] = Field(None, alias="createdAt")
    type: str # 'DIRECT_FILE' | 'EXTERNAL_MIRROR' | 'PURCHASE_REDIRECT'
    is_purchase_redirect: Optional[bool] = Field(None, alias="isPurchaseRedirect")
    is_direct_file: Optional[bool] = Field(None, alias="isDirectFile")

    class Config:
        populate_by_name = True

class OfficialDownloadSource(BaseModel):
    id: str
    name: str
    url: str
    status: str

class Mod(BaseModel):
    id: int
    name: str
    description: str
    credit_to: str = Field(..., alias="creditTo")
    download_link: str = Field(..., alias="downloadLink")
    version: str
    status: str
    categories: List[NamedEntity]
    images: List[ImageObject]
    creator: dict # { name: str, image: Optional[str] }

    class Config:
        populate_by_name = True

class ItemType(str, Enum):
    ARTICLE = "ARTICLE"
    MOD = "MOD"
