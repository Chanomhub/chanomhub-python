from typing import Any, Optional, Union, Dict
import urllib.parse

DEFAULT_STORAGE_URL = "https://cdn.chanomhub.com"
DEFAULT_CDN_URL = "https://imgproxy.chanomhub.com"
DEFAULT_STORAGE_DOWNLOAD_URL = "https://storage.chanomhub.com"

IMAGE_FIELDS = {"mainImage", "backgroundImage", "coverImage", "image"}

def build_imgproxy_path(options: Optional[Dict[str, Any]] = None) -> str:
    if not options:
        return ""
    
    parts = []
    
    # Resize: rs:%type:%width:%height:%enlarge
    if any(k in options for k in ["resizeType", "width", "height", "enlarge"]):
        rs = [
            "rs",
            options.get("resizeType", "fit"),
            str(options.get("width", 0)),
            str(options.get("height", 0)),
            "1" if options.get("enlarge") else "0",
        ]
        parts.append(":".join(rs))
    
    if options.get("quality", 0) > 0:
        parts.append(f"q:{options['quality']}")
    
    if options.get("gravity"):
        parts.append(f"g:{options['gravity']}")
    
    if options.get("dpr", 1) > 1:
        parts.append(f"dpr:{options['dpr']}")
    
    if options.get("blur", 0) > 0:
        parts.append(f"bl:{options['blur']}")
        
    if options.get("sharpen", 0) > 0:
        parts.append(f"sh:{options['sharpen']}")
        
    return "/".join(parts)

def resolve_image_url(
    image_url: Optional[str],
    cdn_url: str = DEFAULT_CDN_URL,
    storage_url: str = DEFAULT_STORAGE_URL,
    options: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    if not image_url:
        return None
    
    if image_url.startswith(("http://", "https://")):
        return image_url
    
    source_url = f"{storage_url}/{image_url}"
    options_path = build_imgproxy_path(options)
    format = options.get("format", "webp") if options else "webp"
    
    encoded_source_url = urllib.parse.quote(source_url, safe="")
    
    if options_path:
        return f"{cdn_url}/insecure/{options_path}/plain/{encoded_source_url}@{format}"
    
    return f"{cdn_url}/insecure/plain/{encoded_source_url}@{format}"

def resolve_download_url(
    url: Optional[str],
    storage_download_url: str = DEFAULT_STORAGE_DOWNLOAD_URL,
) -> Optional[str]:
    if not url:
        return None
        
    if url.startswith(("http://", "https://")):
        return url
        
    base_url = storage_download_url.rstrip("/")
    path = f"/{url.lstrip('/')}"
    
    return f"{base_url}{path}"

def transform_image_urls_deep(data: Any, cdn_url: str = DEFAULT_CDN_URL) -> Any:
    if data is None:
        return None
        
    if isinstance(data, list):
        return [transform_image_urls_deep(item, cdn_url) for item in data]
        
    if isinstance(data, dict):
        result = {}
        
        # Skip transformation for download links
        if "url" in data and ("vipOnly" in data or "isActive" in data):
            return data
            
        for key, value in data.items():
            if key in IMAGE_FIELDS and isinstance(value, str):
                result[key] = resolve_image_url(value, cdn_url)
            elif key == "images" and isinstance(value, list):
                result[key] = [
                    {**img, "url": resolve_image_url(img["url"], cdn_url)}
                    if isinstance(img, dict) and "url" in img
                    else img
                    for img in value
                ]
            elif isinstance(value, (dict, list)):
                result[key] = transform_image_urls_deep(value, cdn_url)
            else:
                result[key] = value
        return result
        
    return data

def transform_download_urls_deep(
    data: Any, 
    storage_download_url: str = DEFAULT_STORAGE_DOWNLOAD_URL
) -> Any:
    if data is None:
        return None
        
    if isinstance(data, list):
        return [transform_download_urls_deep(item, storage_download_url) for item in data]
        
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key == "url" and isinstance(value, str) and not value.startswith(("http://", "https://")):
                result[key] = resolve_download_url(value, storage_download_url)
            elif isinstance(value, (dict, list)):
                result[key] = transform_download_urls_deep(value, storage_download_url)
            else:
                result[key] = value
        return result
        
    return data
