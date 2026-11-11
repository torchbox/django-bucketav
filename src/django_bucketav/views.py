import json
import logging

from typing import TYPE_CHECKING

from django_sns_view.views import SNSEndpoint

from .config import conf
from .enums import BUCKETAV_STATUS_MAP
from .signals import scan_result_received
from .utils import get_object_for_key


if TYPE_CHECKING:
    from django_sns_view.types import Notification

logger = logging.getLogger("django_bucketav")


class BucketAVWebhookView(SNSEndpoint):
    """Receive BucketAV scan results via SNS and update document scan status.

    SNSEndpoint handles signature verification for us — only AWS-signed
    messages will reach handle_message(). When SNS_TOPIC_ARN is set in the
    DJANGO_BUCKETAV setting, SNSEndpoint also validates the topic ARN header so that
    only our own SNS topic can call this endpoint, not messages from other accounts.
    """

    def get_topic_allowlist(self) -> list[str] | None:
        return conf.sns_topic_arn_list

    def handle_message(self, message: str, notification: "Notification") -> None:
        if not conf.enabled:
            return None

        data = json.loads(message)  # Actually parse the JSON

        # validate the bucket
        bucket = data.get("bucket")
        if conf.storage_bucket_name and bucket != conf.storage_bucket_name:
            logger.warning("Received BucketAV webhook for unexpected bucket=%s", bucket)
            return None

        file_key: str | None = data.get("key")
        if file_key is None:
            logger.warning("Received BucketAV webhook with missing file key")
            return None

        status_str: str | None = data.get("status")
        file_scan_status = BUCKETAV_STATUS_MAP.get(status_str)
        if file_scan_status is None:
            logger.warning(
                "Received BucketAV webhook with unknown status=%s for key=%s",
                status_str,
                file_key,
            )
            return None

        logger.debug(
            "Received BucketAV webhook with key=%s status=%s",
            file_key,
            file_scan_status,
        )

        instance = get_object_for_key(file_key)

        if instance is None:
            logger.error("Received BucketAV webhook for unknown file key=%s", file_key)
            return None

        scan_result_received.send(
            sender=instance.__class__,
            instance=instance,
            file_scan_status=file_scan_status,
        )

        return None
