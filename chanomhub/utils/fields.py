from typing import List, Optional, Dict
from ..models.article import ArticlePreset, ArticleField

FIELD_PRESETS: Dict[ArticlePreset, List[ArticleField]] = {
    "minimal": ["id", "title", "slug", "mainImage", "viewsCount"],
    "standard": [
        "id", "title", "slug", "description", "ver", "mainImage", "coverImage",
        "author", "tags", "platforms", "categories", "creators", "engine",
        "favoritesCount", "favorited", "createdAt", "updatedAt", "status",
        "sequentialCode", "images", "price", "isPaid", "isUnlocked", "viewsCount",
    ],
    "full": [
        "id", "title", "slug", "description", "body", "ver", "mainImage",
        "coverImage", "backgroundImage", "author", "tags", "platforms",
        "categories", "creators", "engine", "images", "favoritesCount",
        "favorited", "createdAt", "updatedAt", "status", "sequentialCode",
        "price", "isPaid", "isUnlocked", "viewsCount",
    ],
    "complete": [
        "id", "title", "slug", "description", "body", "ver", "mainImage",
        "coverImage", "backgroundImage", "author", "tags", "platforms",
        "categories", "creators", "engine", "images", "favoritesCount",
        "favorited", "createdAt", "updatedAt", "status", "sequentialCode",
        "downloads", "mods", "officialDownloadSources", "versions", "price",
        "isPaid", "isUnlocked", "viewsCount",
    ],
}

FIELD_MAPPINGS: Dict[ArticleField, str] = {
    "id": "id",
    "title": "title",
    "slug": "slug",
    "description": "description",
    "body": "body",
    "ver": "ver",
    "mainImage": "mainImage",
    "coverImage": "coverImage",
    "backgroundImage": "backgroundImage",
    "createdAt": "createdAt",
    "updatedAt": "updatedAt",
    "status": "status",
    "sequentialCode": "sequentialCode",
    "favoritesCount": "favoritesCount",
    "favorited": "favorited",
    "engine": """engine {
    id
    name
  }""",
    "author": """author {
    id
    name
    image
  }""",
    "creators": """creators {
    id
    name
  }""",
    "tags": """tags {
    id
    name
  }""",
    "platforms": """platforms {
    id
    name
  }""",
    "categories": """categories {
    id
    name
  }""",
    "images": """images {
    id
    url
  }""",
    "mods": """mods {
    id
    name
    version
    downloadLink
    description
    creditTo
    status
    categories {
      id
      name
    }
    images {
      id
      url
    }
  }""",
    "versions": "versions",
    "downloads": """downloads {
    id
    name
    url
    isActive
    vipOnly
    forVersion
    createdAt
    updatedAt
  }""",
    "downloadLinks": """downloads {
    id
    url
    vipOnly
  }""",
    "officialDownloadSources": """officialDownloadSources {
    id
    name
    url
    status
  }""",
    "version": "version",
    "price": "price",
    "isPaid": "isPaid",
    "isUnlocked": "isUnlocked",
    "viewsCount": "viewsCount",
}

def build_fields_query(preset: Optional[ArticlePreset] = "standard", fields: Optional[List[ArticleField]] = None) -> str:
    selected_fields = fields if fields is not None else FIELD_PRESETS.get(preset or "standard", FIELD_PRESETS["standard"])
    return "\n  ".join([FIELD_MAPPINGS.get(f, f) for f in selected_fields])

FIELD_MAPPINGS_MOD = {
    "id": "id",
    "name": "name",
    "description": "description",
    "creditTo": "creditTo",
    "downloadLink": "downloadLink",
    "version": "version",
    "status": "status",
    "categories": """categories {
    id
    name
  }""",
    "images": """images {
    id
    url
  }""",
    "creator": """creator {
    name
    image
  }""",
}

def build_mod_fields_query(fields: Optional[List[str]] = None) -> str:
    default_fields = ["id", "name", "version", "downloadLink"]
    selected_fields = fields if fields is not None else default_fields
    return "\n  ".join([FIELD_MAPPINGS_MOD.get(f, f) for f in selected_fields])
