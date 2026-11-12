import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from testapp.models import CustomDocument, MyModel, MyModelWithBucketAVMixin

from django_bucketav.enums import FileScanStatus


SNS_ARN = "arn:aws:sns:eu-west-1:123456789012:bucketav-topic"
SNS_HEADERS = {
    "HTTP_X_AMZ_SNS_MESSAGE_TYPE": "Notification",
    "HTTP_X_AMZ_SNS_TOPIC_ARN": SNS_ARN,
}
AWS_BUCKET_NAME = "test-media-bucket"


def sample_file() -> SimpleUploadedFile:
    return SimpleUploadedFile("test.pdf", b"file content")


def get_mymodel_instance(file=None) -> MyModel:
    if file is None:
        file = sample_file()
    return MyModel.objects.create(file=file)


def get_mymodel_with_bucketav_mixin_instance(file=None) -> MyModelWithBucketAVMixin:
    if file is None:
        file = sample_file()
    return MyModelWithBucketAVMixin.objects.create(file=file)


def get_wagtail_document(status=FileScanStatus.NOT_SCANNED):
    doc = CustomDocument(
        title="Test document",
        file=SimpleUploadedFile("test.pdf", b"file content"),
        bucketav_scan_status=status,
    )
    doc.save()
    return doc


class DjangoBucketAVTestBase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.webhook_url = reverse("django_bucketav:sns-hook")

    def ping_webhook(
        self,
        *,
        key="test.pdf",
        status=FileScanStatus.CLEAN,
        bucket=AWS_BUCKET_NAME,
        topic_arn=SNS_ARN,
        headers: dict[str, str] | None = None,
    ):
        if headers is None:
            headers = {
                "HTTP_X_AMZ_SNS_MESSAGE_TYPE": "Notification",
                "HTTP_X_AMZ_SNS_TOPIC_ARN": topic_arn,
            }

        return self.client.post(
            self.webhook_url,
            data=self.get_sns_post_body(bucket, key, status),
            content_type="application/json",
            **headers,
        )

    def get_sns_post_body(self, bucket, key, status):
        """Build a minimal SNS Notification payload for webhook tests."""
        message = json.dumps({"bucket": bucket, "key": key, "status": status})
        return json.dumps(
            {
                "Type": "Notification",
                "MessageId": "62acea4d-630a-5a7f-8a4e-b886c17258dd",
                "TopicArn": SNS_ARN,
                "Message": message,
                "Timestamp": "2026-01-11T12:34:56.000Z",
                "SignatureVersion": "1",
                "Signature": "dGVzdA==",
                # SNS signing certs always come from amazonaws.com — used in test payloads
                "SigningCertURL": "https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-cert.pem",
                "UnsubscribeURL": "https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe",
            }
        )
