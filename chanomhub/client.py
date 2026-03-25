from typing import Any, Dict, List, Optional, TypeVar, Type, Union
import httpx
from .config import ChanomhubConfig

T = TypeVar("T")

class ChanomhubClient:
    def __init__(self, config: ChanomhubConfig):
        self.config = config
        self._http_client = httpx.Client(base_url=config.api_url)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        return headers

    def graphql_fetch(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        is_retry: bool = False,
    ) -> Dict[str, Any]:
        payload = {
            "query": query,
            "variables": variables or {},
        }
        if operation_name:
            payload["operationName"] = operation_name

        response = self._http_client.post(
            "/api/v2/graphql",
            json=payload,
            headers=self._get_headers(),
        )

        if response.status_code == 401 and self.config.refresh_token and not is_retry:
            if self._handle_unauthorized():
                return self.graphql_fetch(query, variables, operation_name, True)

        response.raise_for_status()
        data = response.json()
        
        if "errors" in data and data["errors"]:
            # Check for auth errors in graphql errors
            is_auth_error = any(
                "Unauthorized" in e.get("message", "") or
                e.get("extensions", {}).get("code") in ["UNAUTHENTICATED", "401"]
                for e in data["errors"]
            )
            if is_auth_error and self.config.refresh_token and not is_retry:
                 if self._handle_unauthorized():
                    return self.graphql_fetch(query, variables, operation_name, True)
            
            # For now just return data with errors
            return data

        return data.get("data", {})

    def rest_fetch(
        self,
        endpoint: str,
        method: str = "GET",
        json: Optional[Dict[str, Any]] = None,
        is_retry: bool = False,
    ) -> Any:
        response = self._http_client.request(
            method,
            endpoint,
            json=json,
            headers=self._get_headers(),
        )

        if response.status_code == 401 and self.config.refresh_token and not is_retry and "/auth/refresh" not in endpoint:
            if self._handle_unauthorized():
                return self.rest_fetch(endpoint, method, json, True)

        response.raise_for_status()
        
        if response.status_code == 204:
            return None

        data = response.json()
        # Some endpoints wrap data in a 'data' key
        if isinstance(data, dict) and "data" in data and "statusCode" in data:
            return data["data"]
        return data

    def _handle_unauthorized(self) -> bool:
        # Simple token refresh logic
        refresh_token = self.config.refresh_token
        if not refresh_token:
            return False

        try:
            response = self._http_client.post(
                "/api/auth/refresh",
                json={"refreshToken": refresh_token},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle potential wrapping
            res_data = data.get("data", data)
            new_token = res_data.get("accessToken") or res_data.get("token")
            new_refresh_token = res_data.get("refreshToken")

            if new_token and new_refresh_token:
                self.config.token = new_token
                self.config.refresh_token = new_refresh_token
                if self.config.on_token_refreshed:
                    self.config.on_token_refreshed(new_token, new_refresh_token)
                return True
            return False
        except Exception:
            return False
