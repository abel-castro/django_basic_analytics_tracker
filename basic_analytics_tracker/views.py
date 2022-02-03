from django.http import JsonResponse
from django.views.generic import View

from basic_analytics_tracker.mixins import TrackingMixin


class DummyView(TrackingMixin, View):
    def get(self, request, *args, **kwargs):
        data = {"success": True}
        return JsonResponse(data)
