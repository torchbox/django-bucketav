from django.db import models
from django.utils.translation import gettext_lazy as _


class FileScanStatus(models.TextChoices):
    NOT_SCANNED = "not_scanned", _("Not scanned")
    CLEAN = "clean", _("Clean")
    INFECTED = "infected", _("Infected")
    ERRORED = "no", _("Errored")


BUCKETAV_STATUS_MAP = {
    "clean": FileScanStatus.CLEAN,
    "infected": FileScanStatus.INFECTED,
    "no": FileScanStatus.ERRORED,
}

UNSCANNED_STATUSES = [FileScanStatus.NOT_SCANNED, FileScanStatus.ERRORED]
