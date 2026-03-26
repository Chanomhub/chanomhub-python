from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
from .common import Author, Download, OfficialDownloadSource, Mod, NamedEntity, ImageObject, PaginatedResponse

class ArticleStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    NOT_APPROVED = "NOT_APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"

class GameEngine(str, Enum):
    RENPY = "RENPY"
    RPGM = "RPGM"
    UNITY = "UNITY"
    UNREAL = "UNREAL"
    GODOT = "GODOT"
    TYRANOBUILDER = "TyranoBuilder"
    WOLFRPG = "WOLFRPG"
    KIRIKIRI = "KIRIKIRI"
    FLASH = "FLASH"
    BAKINPLAYER = "BakinPlayer"

ArticlePreset = Literal["minimal", "standard", "full", "complete"]

ArticleField = Literal[
    "id", "title", "slug", "description", "body", "ver", "mainImage", "coverImage",
    "backgroundImage", "author", "tags", "platforms", "categories", "creators",
    "engine", "images", "mods", "favoritesCount", "favorited", "createdAt",
    "updatedAt", "status", "sequentialCode", "versions", "downloads",
    "downloadLinks", "officialDownloadSources", "version", "price", "isPaid",
    "isUnlocked", "viewsCount"
]

class ArticleEngine(BaseModel):
    id: str
    name: str

class Article(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    body: Optional[str] = None
    ver: Optional[str] = None
    creators: List[NamedEntity] = []
    tags: List[NamedEntity] = []
    platforms: List[NamedEntity] = []
    categories: List[NamedEntity] = []
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    status: ArticleStatus
    engine: Optional[ArticleEngine] = None
    main_image: Optional[str] = Field(None, alias="mainImage")
    background_image: Optional[str] = Field(None, alias="backgroundImage")
    cover_image: Optional[str] = Field(None, alias="coverImage")
    images: List[ImageObject] = []
    author: Author
    favorited: bool = False
    favorites_count: int = Field(0, alias="favoritesCount")
    sequential_code: Optional[str] = Field(None, alias="sequentialCode")
    downloads: Optional[List[Download]] = None
    mods: List[Mod] = []
    versions: Optional[List[str]] = None
    download_links: Optional[List[Download]] = Field(None, alias="downloadLinks")
    official_download_sources: Optional[List[OfficialDownloadSource]] = Field(None, alias="officialDownloadSources")
    version: Optional[str] = None
    price: float = 0
    is_paid: bool = Field(False, alias="isPaid")
    is_unlocked: bool = Field(False, alias="isUnlocked")
    views_count: int = Field(0, alias="viewsCount")

    class Config:
        populate_by_name = True

class ArticleListItem(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    ver: Optional[str] = None
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    main_image: Optional[str] = Field(None, alias="mainImage")
    cover_image: Optional[str] = Field(None, alias="coverImage")
    favorites_count: int = Field(0, alias="favoritesCount")
    favorited: bool = False
    status: Optional[ArticleStatus] = None
    engine: Optional[ArticleEngine] = None
    sequential_code: Optional[str] = Field(None, alias="sequentialCode")
    author: dict # { name: str, image: Optional[str] }
    tags: Optional[List[NamedEntity]] = None
    platforms: Optional[List[NamedEntity]] = None
    categories: Optional[List[NamedEntity]] = None
    creators: Optional[List[NamedEntity]] = None
    images: Optional[List[ImageObject]] = None
    price: float = 0
    is_paid: bool = Field(False, alias="isPaid")
    is_unlocked: bool = Field(False, alias="isUnlocked")
    views_count: int = Field(0, alias="viewsCount")

    class Config:
        populate_by_name = True

class ArticleFilter(BaseModel):
    tag: Optional[str] = None
    platform: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    favorited: Optional[bool] = None
    engine: Optional[str] = None
    sequential_code: Optional[str] = Field(None, alias="sequentialCode")
    q: Optional[str] = None

    class Config:
        populate_by_name = True

class ArticleListOptions(BaseModel):
    limit: int = 12
    offset: int = 0
    status: ArticleStatus = ArticleStatus.PUBLISHED
    filter: Optional[ArticleFilter] = None
    preset: Optional[ArticlePreset] = "standard"
    fields: Optional[List[ArticleField]] = None

class ArticleQueryOptions(BaseModel):
    language: Optional[str] = None
    version: Optional[str] = None
    preset: Optional[ArticlePreset] = "full"
    fields: Optional[List[ArticleField]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class ArticleCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    description: str
    body: str
    price: Optional[float] = 0
    is_premium: Optional[bool] = Field(False, alias="isPremium")
    language: Optional[str] = None
    ver: Optional[str] = None
    status: Optional[ArticleStatus] = ArticleStatus.DRAFT
    engine: Optional[str] = None
    main_image: Optional[str] = Field(None, alias="mainImage")
    background_image: Optional[str] = Field(None, alias="backgroundImage")
    cover_image: Optional[str] = Field(None, alias="coverImage")
    other_images: List[str] = Field([], alias="otherImages")
    tags: List[str] = []
    categories: List[str] = []
    platforms: List[str] = []
    creator: Optional[str] = None

    class Config:
        populate_by_name = True
