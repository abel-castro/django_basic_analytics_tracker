import pytest
import requests_mock
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse_lazy

URL = reverse_lazy("dummy_view")
TEST_BASIC_ANALYTICS_URL = "https://test-url.com/api/tacker"
TEST_BASIC_ANALYTICS_ID = "test-id"

return_value = {"message": "PageView created"}


def create_test_user(is_superuser: bool = False):
    username = "user"
    password = "password"
    return get_user_model().objects.create_user(
        username=username, password=password, is_superuser=is_superuser
    )


@pytest.fixture
def logged_user(client):
    user = create_test_user()
    client.force_login(user)


@pytest.fixture
def logged_superuser(client):
    user = create_test_user(is_superuser=True)
    client.force_login(user)


@requests_mock.Mocker(kw="request_mocker")
class TestTrackingMixin:
    pytestmark = pytest.mark.django_db

    def assert_success_tracking(self, client, caplog, **kwargs):
        self.mock_basic_analytics_request(kwargs["request_mocker"])
        response = client.get(URL)
        assert response.status_code == 200
        assert len(caplog.records) == 1

        expected_message = "Basic analytics API responded with status 201 and message: 'PageView created'"
        for record in caplog.records:
            assert record.levelname == "INFO"
            assert record.message == expected_message

    @staticmethod
    def mock_basic_analytics_request(request_mocker):
        request_mocker.post(
            TEST_BASIC_ANALYTICS_URL, json=return_value, status_code=201
        )

    @override_settings(
        BASIC_ANALYTICS_ID=TEST_BASIC_ANALYTICS_ID,
        BASIC_ANALYTICS_URL=TEST_BASIC_ANALYTICS_URL,
    )
    def test__logged_user__is_not_superuser__track(
        self, client, caplog, logged_user, **kwargs
    ):
        self.assert_success_tracking(client, caplog, **kwargs)

    @override_settings(
        BASIC_ANALYTICS_ID=TEST_BASIC_ANALYTICS_ID,
        BASIC_ANALYTICS_URL=TEST_BASIC_ANALYTICS_URL,
    )
    def test__not_logged_user__track(self, client, caplog, **kwargs):
        self.assert_success_tracking(client, caplog, **kwargs)

    @override_settings(
        BASIC_ANALYTICS_ID=TEST_BASIC_ANALYTICS_ID,
        BASIC_ANALYTICS_URL=TEST_BASIC_ANALYTICS_URL,
    )
    def test__logged_user__is_superuser__not_track(
        self, client, caplog, logged_superuser, **kwargs
    ):
        self.mock_basic_analytics_request(kwargs["request_mocker"])
        response = client.get(URL)
        assert response.status_code == 200
        assert len(caplog.records) == 0

    def test__not_configured__not_track(self, client, caplog, **kwargs):
        self.mock_basic_analytics_request(kwargs["request_mocker"])
        response = client.get(URL)
        assert response.status_code == 200
        assert len(caplog.records) == 0
