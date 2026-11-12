import logging

import boto3

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from django_bucketav.config import conf
from django_bucketav.enums import (
    BUCKETAV_STATUS_MAP,
    UNSCANNED_STATUSES,
    FileScanStatus,
)
from django_bucketav.models import BucketAVMixin


logger = logging.getLogger(__name__)


def get_file_tags(key):
    """Return the S3 object tags for the given key as a plain dict.

    Extracted as a module-level function so tests can patch it without
    needing a real S3 connection.
    """
    client = boto3.client("s3")
    response = client.get_object_tagging(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
    )
    return {tag["Key"]: tag["Value"] for tag in response.get("TagSet", [])}


class Command(BaseCommand):
    help = (
        "Check S3 tags for unscanned documents and update their scan status. "
        "Run regularly to catch any webhooks that were missed."
    )

    def handle(self, *args, **options):
        for model_string in conf.models:
            model = apps.get_model(model_string)

            if not issubclass(model, BucketAVMixin):
                continue

            self.process_queryset(
                model.objects.filter(bucketav_scan_status__in=UNSCANNED_STATUSES),
                label=model._meta.label,
            )

    def process_queryset(self, queryset, label):
        count = queryset.count()
        logger.info("Checking %d unscanned %s(s) for BucketAV tags", count, label)

        for obj in queryset:
            tags = get_file_tags(obj.file.name)
            status_str = tags.get("bucketav")

            if status_str is None:
                logger.info(
                    "No bucketav tag yet for %s %d (%s)", label, obj.pk, obj.file.name
                )
                continue

            scan_status = BUCKETAV_STATUS_MAP.get(status_str)
            if scan_status is None:
                logger.warning(
                    "Unknown bucketav tag value %r for %s %d (%s)",
                    status_str,
                    label,
                    obj.pk,
                    obj.file.name,
                )
                continue

            obj.update_bucketav_scan_status(scan_status)

            if scan_status == FileScanStatus.CLEAN:
                logger.info(
                    "%s %d (%s) marked as clean",
                    label.capitalize(),
                    obj.pk,
                    obj.file.name,
                )
            else:
                logger.warning(
                    "%s %d (%s) marked as %s",
                    label.capitalize(),
                    obj.pk,
                    obj.file.name,
                    status_str,
                )
