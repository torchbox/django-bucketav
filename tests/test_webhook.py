from http import HTTPStatus
from unittest.mock import patch

from django.test import override_settings

from django_bucketav.enums import FileScanStatus

from .utils import (
    SNS_ARN,
    DjangoBucketAVTestBase,
    get_mymodel_instance,
    get_mymodel_with_bucketav_mixin_instance,
)


class WebhookTest(DjangoBucketAVTestBase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.instance = get_mymodel_with_bucketav_mixin_instance()
        cls.file_key = str(cls.instance.file)

    def test_ping_successful(self):
        self.assertEqual(self.instance.bucketav_scan_status, FileScanStatus.NOT_SCANNED)

        response = self.ping_webhook(key=self.file_key, status="clean")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.instance.refresh_from_db()
        self.assertEqual(self.instance.bucketav_scan_status, FileScanStatus.CLEAN)

    @override_settings(DJANGO_BUCKETAV={"MODELS": {"testapp.MyModel": ["file"]}})
    @patch("django_bucketav.views.scan_result_received")
    def ping_successful__model_without_mixin(self, mocked_scan_result_received):
        instance = get_mymodel_instance()
        response = self.ping_webhook(key=str(instance.file), status="clean")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mocked_scan_result_received.assert_not_called()

    @override_settings(DJANGO_BUCKETAV={"ENABLED": False})
    def test_with_scanning_disabled(self):
        self.assertEqual(self.instance.bucketav_scan_status, FileScanStatus.NOT_SCANNED)
        response = self.ping_webhook(key=self.file_key, status="clean")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.instance.bucketav_scan_status, FileScanStatus.NOT_SCANNED)

    def test_ping_with_no_key(self):
        with self.assertLogs("django_bucketav", level="WARNING") as log_output:
            response = self.ping_webhook(key=None, status="clean")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            log_output[0][0].message, "Received BucketAV webhook with missing file key"
        )

    def test_ping_with_unknown_status(self):
        with self.assertLogs("django_bucketav", level="WARNING") as log_output:
            response = self.ping_webhook(key=self.file_key, status="ignore")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            log_output[0][0].message,
            f"Received BucketAV webhook with unknown status=ignore for key={self.file_key}",
        )

    def test_ping_unknown_file(self):
        with self.assertLogs("django_bucketav", level="WARNING") as log_output:
            response = self.ping_webhook(key="not-a-file", status="clean")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(
            log_output[0][0].message,
            "Received BucketAV webhook for unknown file key=not-a-file",
        )

    @override_settings(DJANGO_BUCKETAV={"SNS_TOPIC_ARN": SNS_ARN})
    def test_wrong_topic_arn_is_rejected(self):
        response = self.ping_webhook(
            topic_arn="arn:aws:sns:eu-west-1:999999999999:other-topic"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @override_settings(DJANGO_BUCKETAV={"SNS_TOPIC_ARN": SNS_ARN})
    def test_missing_topic_arn_header_is_rejected(self):
        response = self.ping_webhook(
            headers={"x-amz-sns-message-type": "Notification"},
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @override_settings(DJANGO_BUCKETAV={"AWS_STORAGE_BUCKET_NAME": "new-target-bucket"})
    def test_wrong_bucket(self):
        with self.assertLogs("django_bucketav", level="WARNING") as log_output:
            self.ping_webhook()

        self.assertEqual(
            log_output[0][0].message,
            "Received BucketAV webhook for unexpected bucket=test-media-bucket",
        )
