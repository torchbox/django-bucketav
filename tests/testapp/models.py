from django.db import models

from django_bucketav.models import BucketAVMixin


# Only this model is referenced in the test app's DJANGO_BUCKETAV setting
class MyModel(models.Model):
    file = models.FileField()

    def __str__(self) -> str:
        return self.pk


# This should be picked by tests that override settings, and have
# bucketav_scan_status, bucketav_last_scanned_at updated
class MyModelWithBucketAVMixin(BucketAVMixin, models.Model):
    file = models.FileField()

    def __str__(self) -> str:
        return self.pk


class GenericModel(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name
