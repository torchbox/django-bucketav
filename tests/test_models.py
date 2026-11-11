import datetime as dt

from unittest.mock import patch

import time_machine

from django.test import TestCase
from testapp.models import MyModel, MyModelWithBucketAVMixin

from django_bucketav.models import FileScanStatus
from django_bucketav.signals import scan_result_received

from .utils import get_mymodel_instance, get_mymodel_with_bucketav_mixin_instance


@time_machine.travel(dt.datetime(2026, 1, 11, 12, 34, 56), tick=False)
class BucketAVModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.instance = get_mymodel_with_bucketav_mixin_instance()

    def test_document_with_av_mixin_is_updated_on_scan_result_received_signal(self):
        # Check our initial state:
        self.assertEqual(self.instance.bucketav_scan_status, FileScanStatus.NOT_SCANNED)
        self.assertIsNone(self.instance.bucketav_last_scanned_at)

        scenarios = [
            # signal_status_input, expected_scan_status
            ("clean", FileScanStatus.CLEAN),
            ("infected", FileScanStatus.INFECTED),
            ("no", FileScanStatus.ERRORED),
        ]

        for signal_status_input, expected_scan_status in scenarios:
            with self.subTest(msg=f"{signal_status_input=}, {expected_scan_status=}"):
                scan_result_received.send(
                    MyModelWithBucketAVMixin,
                    instance=self.instance,
                    file_scan_status=signal_status_input,
                )

                self.instance.refresh_from_db()
                self.assertEqual(
                    self.instance.bucketav_scan_status, expected_scan_status
                )
                self.assertEqual(
                    self.instance.bucketav_last_scanned_at,
                    dt.datetime(2026, 1, 11, 12, 34, 56, tzinfo=dt.UTC),
                )

    @patch("testapp.models.MyModelWithBucketAVMixin.update_bucketav_scan_status")
    def test_update_bucketav_scan_status_called(self, mocked):
        scan_result_received.send(
            MyModelWithBucketAVMixin,
            instance=self.instance,
            file_scan_status="clean",
        )
        mocked.assert_called_once()

    @patch("testapp.models.MyModelWithBucketAVMixin.update_bucketav_scan_status")
    def test_update_bucketav_scan_status_not_called_for_non_mixin_models(self, mocked):
        scan_result_received.send(
            MyModel,
            instance=get_mymodel_instance(),
            file_scan_status="clean",
        )
        mocked.assert_not_called()
