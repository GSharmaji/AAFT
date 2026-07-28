"""
Thin wrapper around LinkedIn's official Posts API (the versioned /rest endpoints).

This uses first-party publishing only — posting your own content to a page or
profile you control. It does NOT scrape, auto-connect, auto-like, or fake
engagement (all of which violate LinkedIn's terms).

Docs:
  - Posts API:  https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
  - Images API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api
"""

from __future__ import annotations

import os
import requests

API_BASE = "https://api.linkedin.com/rest"

# LinkedIn requires a versioned API date header (YYYYMM). Override with the
# LINKEDIN_VERSION env var if LinkedIn deprecates this one.
DEFAULT_VERSION = "202409"

# Characters that must be backslash-escaped in the Posts API "commentary" field
# so they render as literal text instead of breaking the request. We keep '#'
# unescaped so hashtags still work.
_RESERVED = r"\<>~(){}[]@|"


class LinkedInError(RuntimeError):
    pass


def escape_commentary(text: str) -> str:
    """Escape reserved 'little text' characters LinkedIn requires escaping."""
    out = []
    for ch in text:
        if ch in _RESERVED:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


class LinkedInClient:
    def __init__(self, access_token: str | None = None, author_urn: str | None = None,
                 version: str | None = None):
        self.access_token = access_token or os.environ.get("LINKEDIN_ACCESS_TOKEN")
        self.author_urn = author_urn or os.environ.get("LINKEDIN_AUTHOR_URN")
        self.version = version or os.environ.get("LINKEDIN_VERSION", DEFAULT_VERSION)

        if not self.access_token:
            raise LinkedInError("Missing LINKEDIN_ACCESS_TOKEN")
        if not self.author_urn:
            raise LinkedInError(
                "Missing LINKEDIN_AUTHOR_URN "
                "(e.g. 'urn:li:organization:12345678' for a Company Page, "
                "or 'urn:li:person:abcd1234' for a personal profile)"
            )

    # -- headers ---------------------------------------------------------------
    def _headers(self, extra: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "LinkedIn-Version": self.version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    # -- image upload ----------------------------------------------------------
    def upload_image(self, image_path: str) -> str:
        """Register + upload an image, returning its urn:li:image:... id."""
        if not os.path.isfile(image_path):
            raise LinkedInError(f"Image not found: {image_path}")

        # 1. Initialize the upload to get a one-time upload URL + image URN.
        init = requests.post(
            f"{API_BASE}/images?action=initializeUpload",
            headers=self._headers(),
            json={"initializeUploadRequest": {"owner": self.author_urn}},
            timeout=30,
        )
        if init.status_code >= 300:
            raise LinkedInError(f"initializeUpload failed [{init.status_code}]: {init.text}")
        value = init.json()["value"]
        upload_url = value["uploadUrl"]
        image_urn = value["image"]

        # 2. PUT the raw bytes to the upload URL.
        with open(image_path, "rb") as fh:
            put = requests.put(
                upload_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                data=fh.read(),
                timeout=120,
            )
        if put.status_code >= 300:
            raise LinkedInError(f"image PUT failed [{put.status_code}]: {put.text}")

        return image_urn

    # -- posting ---------------------------------------------------------------
    def create_post(self, commentary: str, image_urn: str | None = None,
                    alt_text: str = "", visibility: str = "PUBLIC") -> str:
        """Publish a post. Returns the created post URN."""
        body = {
            "author": self.author_urn,
            "commentary": escape_commentary(commentary),
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if image_urn:
            body["content"] = {
                "media": {
                    "id": image_urn,
                    "altText": alt_text or "",
                }
            }

        resp = requests.post(
            f"{API_BASE}/posts",
            headers=self._headers(),
            json=body,
            timeout=30,
        )
        if resp.status_code >= 300:
            raise LinkedInError(f"create post failed [{resp.status_code}]: {resp.text}")

        # LinkedIn returns the new post URN in the x-restli-id / x-linkedin-id header.
        return resp.headers.get("x-restli-id") or resp.headers.get("x-linkedin-id", "unknown")
