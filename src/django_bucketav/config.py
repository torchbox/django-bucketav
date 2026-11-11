from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Settings:
    @property
    def _user_settings(self) -> dict[str, str]:
        user_settings = getattr(settings, "DJANGO_BUCKETAV", None)
        return user_settings if isinstance(user_settings, dict) else {}

    @property
    def enabled(self) -> bool:
        return str(self._user_settings.get("ENABLED", "True")).lower() == "true"

    @property
    def models(self) -> dict[str, list[str]]:
        _models = self._user_settings.get("MODELS", {})
        if not isinstance(_models, dict):
            raise ImproperlyConfigured
        return _models

    @property
    def storage_bucket_name(self) -> str | None:
        return self._user_settings.get("AWS_STORAGE_BUCKET_NAME")

    @property
    def sns_topic_arn_list(self) -> list[str] | None:
        if topic_arn := self._user_settings.get("SNS_TOPIC_ARN", None):
            return [topic_arn]

        topics = self._user_settings.get("SNS_TOPIC_ARNS", None)
        if topics is None:
            return None

        if not isinstance(topics, list):
            raise ImproperlyConfigured

        return topics


conf = Settings()
