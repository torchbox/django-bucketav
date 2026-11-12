from typing import TYPE_CHECKING

from django.http import HttpResponseForbidden
from wagtail import hooks

from django_bucketav.enums import FileScanStatus
from django_bucketav.models import BucketAVMixin


if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from wagtail.documents.models import AbstractDocument

    type Document = AbstractDocument | BucketAVMixin


@hooks.register("before_serve_document")
def block_unscanned_or_infected(
    doc: "Document", request: "HttpRequest"
) -> HttpResponseForbidden | None:
    """Block downloads of documents that have not passed an antivirus scan.

    Documents start as NOT_SCANNED and move to CLEAN once BucketAV confirms
    they are safe. INFECTED and ERRORED documents are also blocked.
    """
    if not isinstance(doc, BucketAVMixin):
        return None

    if doc.bucketav_scan_status != FileScanStatus.CLEAN:
        return HttpResponseForbidden("This file is not available for download.")
