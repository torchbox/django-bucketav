from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from django_bucketav.enums import FileScanStatus

from .utils import get_wagtail_document


@patch("django_bucketav.management.commands.update_bucketav_scan_status.get_file_tags")
@override_settings(DJANGO_BUCKETAV={"MODELS": {"testapp.CustomDocument": ["file"]}})
class UpdateBucketAVScanStatusTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.document = get_wagtail_document()

    def run_command(self):
        call_command(
            "update_bucketav_scan_status",
            stdout=StringIO(),
            stderr=StringIO(),
        )

    def test_clean_tag_updates_status_to_clean(self, mock_get_tags):
        mock_get_tags.return_value = {"bucketav": "clean"}
        self.run_command()
        self.document.refresh_from_db()
        self.assertEqual(self.document.bucketav_scan_status, FileScanStatus.CLEAN)

    def test_infected_tag_updates_status_to_infected(self, mock_get_tags):
        mock_get_tags.return_value = {"bucketav": "infected"}
        self.run_command()
        self.document.refresh_from_db()
        self.assertEqual(self.document.bucketav_scan_status, FileScanStatus.INFECTED)

    def test_errored_document_is_also_rechecked(self, mock_get_tags):
        doc = get_wagtail_document(status=FileScanStatus.ERRORED)
        mock_get_tags.return_value = {"bucketav": "clean"}
        self.run_command()
        doc.refresh_from_db()
        # ERRORED docs are retried in case the scan eventually succeeds
        self.assertEqual(doc.bucketav_scan_status, FileScanStatus.CLEAN)

    def test_already_clean_document_is_not_updated(self, mock_get_tags):
        doc = get_wagtail_document(status=FileScanStatus.CLEAN)
        mock_get_tags.return_value = {"bucketav": "infected"}
        self.run_command()
        doc.refresh_from_db()
        # CLEAN docs are not re-processed
        self.assertEqual(doc.bucketav_scan_status, FileScanStatus.CLEAN)

    @override_settings(DJANGO_BUCKETAV={"MODELS": {"testapp.GenericModel": ["name"]}})
    def test_command_skips_non_mixin_models(self, mock_get_tags):
        mock_get_tags.return_value = {"bucketav": "infected"}
        self.run_command()
        mock_get_tags.assert_not_called()
