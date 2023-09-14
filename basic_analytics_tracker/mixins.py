import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TrackingMixin:
    @staticmethod
    def _build_request_meta(request):
        return {
            "HTTP_ACCEPT_LANGUAGE": request.META.get("HTTP_ACCEPT_LANGUAGE"),
            "HTTP_HOST": request.META.get("HTTP_HOST"),
            "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
            "HTTP_X_FORWARDED_FOR": request.META.get("HTTP_X_FORWARDED_FOR"),
            "PATH_INFO": request.META.get("PATH_INFO"),
            "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
        }

    def build_payload(self, request):
        return {
            "domain_id": settings.BASIC_ANALYTICS_ID,
            "request_meta": self._build_request_meta(request),
            "url": request.build_absolute_uri(),
        }

    @staticmethod
    def is_configured() -> bool:
        return (
            hasattr(settings, "BASIC_ANALYTICS_URL")
            and hasattr(settings, "BASIC_ANALYTICS_ID")
            and getattr(settings, "BASIC_ANALYTICS_URL") is not None
            and getattr(settings, "BASIC_ANALYTICS_ID") is not None
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and self.is_configured():
            payload = self.build_payload(request)
            try:
                basic_analytics_response = requests.post(
                    settings.BASIC_ANALYTICS_URL, json=payload
                )
                logger.info(
                    f"Basic analytics API responded with status {basic_analytics_response.status_code}"
                    f" and message: '{basic_analytics_response.json()['message']}'"
                )
            except Exception as e:
                logger.info(f"Error sending the request to the Basic Analytics API: {e}")
        return super().dispatch(request, *args, **kwargs)
