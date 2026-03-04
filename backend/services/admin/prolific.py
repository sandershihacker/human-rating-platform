"""Prolific API client for automated study management.

All Prolific HTTP calls live here. The service is stateless -- it receives
the API token and base URL from config, and is only called when Prolific
integration is enabled.
"""

from __future__ import annotations

import logging
import secrets
import string

import httpx

from config import ProlificSettings

logger = logging.getLogger(__name__)

COMPLETION_CODE_LENGTH = 8
COMPLETION_URL_TEMPLATE = "https://app.prolific.com/submissions/complete?cc={code}"


def generate_completion_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(COMPLETION_CODE_LENGTH))


def build_completion_url(code: str) -> str:
    return COMPLETION_URL_TEMPLATE.format(code=code)


async def create_study(
    *,
    settings: ProlificSettings,
    name: str,
    description: str,
    external_study_url: str,
    estimated_completion_time: int,
    reward: int,
    total_available_places: int,
    completion_code: str,
    device_compatibility: list[str] | None = None,
) -> dict:
    payload = {
        "name": name,
        "description": description,
        "external_study_url": external_study_url,
        "estimated_completion_time": estimated_completion_time,
        "reward": reward,
        "total_available_places": total_available_places,
        "prolific_id_option": "url_parameters",
        "device_compatibility": device_compatibility or ["desktop"],
        "completion_codes": [
            {
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "AUTOMATICALLY_APPROVE"}],
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.base_url}/studies/",
            json=payload,
            headers={"Authorization": f"Token {settings.api_token}"},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def publish_study(
    *,
    settings: ProlificSettings,
    study_id: str,
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.base_url}/studies/{study_id}/transition/",
            json={"action": "PUBLISH"},
            headers={"Authorization": f"Token {settings.api_token}"},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


async def delete_study(
    *,
    settings: ProlificSettings,
    study_id: str,
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.base_url}/studies/{study_id}/",
            headers={"Authorization": f"Token {settings.api_token}"},
            timeout=30.0,
        )
        if response.status_code == 404:
            logger.warning("Prolific study %s already deleted (404)", study_id)
            return
        response.raise_for_status()
