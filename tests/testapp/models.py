from django.db import models
from wagtail.documents.models import AbstractDocument
from wagtail.documents.models import Document as WagtailDocument

from django_bucketav.models import BucketAVMixin


class MyModel(models.Model):
    file = models.FileField()

    def __str__(self) -> str:
        return self.pk


# Only this model is referenced in the test app's DJANGO_BUCKETAV setting,
# and will have bucketav_scan_status, bucketav_last_scanned_at updated
class MyModelWithBucketAVMixin(BucketAVMixin, models.Model):
    file = models.FileField()

    def __str__(self) -> str:
        return self.pk


class GenericModel(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name


class CustomDocument(BucketAVMixin, AbstractDocument):
    admin_form_fields = WagtailDocument.admin_form_fields
