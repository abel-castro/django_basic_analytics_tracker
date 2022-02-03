# Django Basic Analytics Tracker

Django app that provides utilities for sending data to the [Basic Analytics](https://github.com/abel-castro/basic_analytics) API.

## Quick start

1. Add "tracker" to your INSTALLED_APPS setting like this::

    ```
    INSTALLED_APPS = [
        ...
        'basic_analytics_tracker'
    ]
    ```

2. Use it in a view:
    ```
    from basic_analytics_tracker.mixins import TrackingMixin
    
    class YourView(TrackingMixin, View):
        ...
    ```


