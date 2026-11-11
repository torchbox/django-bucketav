from typing import TYPE_CHECKING

from . import logger
from .models import BucketAVMixin, FileScanStatus


if TYPE_CHECKING:
    from django.db import models


def log_scanned_instance(
    sender, instance: "models.Model", file_scan_status: FileScanStatus, **kwargs
) -> None:
    if file_scan_status == FileScanStatus.ERRORED:
        logger.error("BucketAV scan failed type=%s id=%d", sender.__name__, instance.pk)
    else:
        logger.info(
            "BucketAV scanned type=%s id=%d status=%s",
            sender.__name__,
            instance.pk,
            file_scan_status,
        )


def update_scan_status_for_instance(
    sender, instance: "models.Model", file_scan_status: FileScanStatus, **kwargs
):
    if isinstance(instance, BucketAVMixin):
        instance.update_bucketav_scan_status(file_scan_status)
