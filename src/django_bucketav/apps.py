from django.apps import AppConfig


class DjangoBucketAVAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "django_bucketav"

    def ready(self) -> None:
        from .signal_handlers import (
            log_scanned_instance,
            update_scan_status_for_instance,
        )
        from .signals import scan_result_received

        scan_result_received.connect(
            log_scanned_instance, dispatch_uid="bucketav_log_scanned_instance"
        )
        scan_result_received.connect(
            update_scan_status_for_instance,
            dispatch_uid="bucketav_update_scan_status_for_instance",
        )
