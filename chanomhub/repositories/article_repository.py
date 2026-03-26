from typing import List, Optional, Dict, Any, Union
from ..client import ChanomhubClient
from ..models.article import (
    Article,
    ArticleListItem,
    ArticleListOptions,
    ArticleQueryOptions,
    ArticleStatus,
    ArticleCreate,
)
from ..models.common import PaginatedResponse, NamedEntity, Mod, OfficialDownloadSource, Download
from ..utils.fields import build_fields_query, build_mod_fields_query
from ..utils.urls import transform_image_urls_deep, resolve_download_url

class ArticleRepository:
    def __init__(self, client: ChanomhubClient):
        self.client = client

    def get_all(self, options: Optional[ArticleListOptions] = None) -> List[ArticleListItem]:
        options = options or ArticleListOptions()
        
        filter_parts = []
        if options.filter:
            f = options.filter
            if f.tag: filter_parts.append(f'tag: "{f.tag}"')
            if f.platform: filter_parts.append(f'platform: "{f.platform}"')
            if f.category: filter_parts.append(f'category: "{f.category}"')
            if f.author: filter_parts.append(f'author: "{f.author}"')
            if f.favorited is not None: filter_parts.append(f'favorited: {"true" if f.favorited else "false"}')
            if f.engine: filter_parts.append(f'engine: "{f.engine}"')
            if f.sequential_code: filter_parts.append(f'sequentialCode: "{f.sequential_code}"')
            if f.q: filter_parts.append(f'q: "{f.q.replace('"', '\\"')}"')

        filter_arg = f'filter: {{ {", ".join(filter_parts)} }}, ' if filter_parts else ""
        fields_query = build_fields_query(options.preset, options.fields)

        status_val = options.status.value if hasattr(options.status, "value") else options.status
        query = f"""query GetArticles {{
      public {{
        articles({filter_arg}limit: {options.limit}, offset: {options.offset}, status: {status_val}) {{
          {fields_query}
        }}
      }}
    }}"""

        print(f"DEBUG QUERY: {query}")
        data = self.client.graphql_fetch(query, operation_name="GetArticles")
        articles_data = data.get("public", {}).get("articles", [])
        
        transformed = transform_image_urls_deep(articles_data, self.client.config.cdn_url)
        return [ArticleListItem.model_validate(item) for item in transformed]

    def get_all_paginated(self, options: Optional[ArticleListOptions] = None) -> PaginatedResponse[ArticleListItem]:
        options = options or ArticleListOptions()
        
        filter_parts = []
        if options.filter:
            f = options.filter
            if f.tag: filter_parts.append(f'tag: "{f.tag}"')
            if f.platform: filter_parts.append(f'platform: "{f.platform}"')
            if f.category: filter_parts.append(f'category: "{f.category}"')
            if f.author: filter_parts.append(f'author: "{f.author}"')
            if f.favorited is not None: filter_parts.append(f'favorited: {"true" if f.favorited else "false"}')
            if f.engine: filter_parts.append(f'engine: "{f.engine}"')
            if f.sequential_code: filter_parts.append(f'sequentialCode: "{f.sequential_code}"')
            if f.q: filter_parts.append(f'q: "{f.q.replace('"', '\\"')}"')

        filter_arg = f'filter: {{ {", ".join(filter_parts)} }}, ' if filter_parts else ""
        count_filter_arg = f'(filter: {{ {", ".join(filter_parts)} }})' if filter_parts else ""
        fields_query = build_fields_query(options.preset, options.fields)

        status_val = options.status.value if hasattr(options.status, "value") else options.status
        query = f"""query GetArticlesPaginated {{
      public {{
        articles({filter_arg}limit: {options.limit}, offset: {options.offset}, status: {status_val}) {{
          {fields_query}
        }}
        articlesCount{count_filter_arg}
      }}
    }}"""

        data = self.client.graphql_fetch(query, operation_name="GetArticlesPaginated")
        public_data = data.get("public", {})
        articles_data = public_data.get("articles", [])
        total = public_data.get("articlesCount", 0)
        
        transformed = transform_image_urls_deep(articles_data, self.client.config.cdn_url)
        items = [ArticleListItem.model_validate(item) for item in transformed]
        
        page = (options.offset // options.limit) + 1
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            pageSize=options.limit
        )

    def get_by_slug(self, slug: str, options: Optional[ArticleQueryOptions] = None) -> Optional[Article]:
        options = options or ArticleQueryOptions()
        fields_query = build_fields_query(options.preset, options.fields)
        
        query = f"""query GetArticleBySlug($slug: String!, $language: String, $version: String) {{
      public {{
        article(slug: $slug, language: $language, version: $version) {{
          {fields_query}
        }}
      }}
    }}"""

        variables = {
            "slug": slug,
            "language": options.language,
            "version": options.version,
        }

        print(f"DEBUG SLUG QUERY: {query}")
        print(f"DEBUG SLUG VARS: {variables}")
        data = self.client.graphql_fetch(query, variables=variables, operation_name="GetArticleBySlug")
        print(f"DEBUG SLUG DATA: {data}")
        article_data = data.get("public", {}).get("article")
        
        if not article_data:
            return None
            
        transformed = transform_image_urls_deep(article_data, self.client.config.cdn_url)
        
        # Transform downloads if present
        if "downloads" in transformed and transformed["downloads"]:
            storage_url = self.client.config.storage_download_url
            for d in transformed["downloads"]:
                d["url"] = resolve_download_url(d["url"], storage_url)
                # Add helper flags similar to TS transformDownload
                url_lower = d["url"].lower()
                d["isPurchaseRedirect"] = "purchase=true" in url_lower or "/articles/" in url_lower
                d["isDirectFile"] = not d["isPurchaseRedirect"] and any(ext in url_lower for ext in [".zip", ".rar", ".7z", ".apk", "/public/"])

        return Article.model_validate(transformed)

    def get_tags(self) -> List[str]:
        query = """query GetTags {
      system {
        tags
      }
    }"""
        data = self.client.graphql_fetch(query)
        return data.get("system", {}).get("tags", [])

    def get_categories(self) -> List[str]:
        query = """query GetCategories {
      system {
        categories
      }
    }"""
        data = self.client.graphql_fetch(query)
        return data.get("system", {}).get("categories", [])

    def get_platforms(self) -> List[str]:
        query = """query GetPlatforms {
      system {
        platforms
      }
    }"""
        data = self.client.graphql_fetch(query)
        return data.get("system", {}).get("platforms", [])

    def get_engines(self) -> List[NamedEntity]:
        data = self.client.rest_fetch("/api/engines")
        return [NamedEntity.model_validate(item) for item in data]

    def get_mods(self, article_id: int, fields: Optional[List[str]] = None) -> List[Mod]:
        fields_query = build_mod_fields_query(fields)
        query = f"""query GetArticleMods($articleId: Int!) {{
      public {{
        article(id: $articleId) {{
          mods {{
            {fields_query}
          }}
        }}
      }}
    }}"""
        data = self.client.graphql_fetch(query, variables={"articleId": article_id}, operation_name="GetArticleMods")
        mods_data = data.get("public", {}).get("article", {}).get("mods", [])
        return [Mod.model_validate(item) for item in mods_data]

    def get_official_download_sources(self, article_id: int) -> List[OfficialDownloadSource]:
        query = """query GetOfficialDownloadSources($articleId: Int!) {
      public {
        article(id: $articleId) {
          officialDownloadSources {
            id
            name
            url
            status
          }
        }
      }
    }"""
        data = self.client.graphql_fetch(query, variables={"articleId": article_id}, operation_name="GetOfficialDownloadSources")
        sources_data = data.get("public", {}).get("article", {}).get("officialDownloadSources", [])
        return [OfficialDownloadSource.model_validate(item) for item in sources_data]

    def increment_view(self, slug: str) -> None:
        self.client.rest_fetch(f"/api/articles/{slug}/view", method="POST")

    def create(self, article: ArticleCreate) -> Article:
        data = self.client.rest_fetch(
            "/api/articles",
            method="POST",
            json=article.model_dump(by_alias=True, exclude_none=True)
        )
        # The backend returns { article: ArticleDTO }
        article_data = data.get("article") if isinstance(data, dict) else data
        return Article.model_validate(article_data)
