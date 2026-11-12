from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from testapp.models import CustomDocument

from django_bucketav.enums import FileScanStatus


class DocumentDownloadBlockingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doc = CustomDocument(
            title="Test document",
            file=SimpleUploadedFile("test.pdf", b"file content"),
            bucketav_scan_status=FileScanStatus.NOT_SCANNED,
        )
        cls.doc.save()

        cls.serve_url = reverse(
            "wagtaildocs_serve", args=[cls.doc.pk, cls.doc.filename]
        )

    def _set_status(self, status):
        self.doc.bucketav_scan_status = status
        self.doc.save(update_fields=["bucketav_scan_status"])

    def test_not_scanned_document_returns_403(self):
        self._set_status(FileScanStatus.NOT_SCANNED)
        self.assertEqual(
            self.client.get(self.serve_url).status_code, HTTPStatus.FORBIDDEN
        )

    def test_infected_document_returns_403(self):
        self._set_status(FileScanStatus.INFECTED)
        self.assertEqual(
            self.client.get(self.serve_url).status_code, HTTPStatus.FORBIDDEN
        )

    def test_errored_document_returns_403(self):
        self._set_status(FileScanStatus.ERRORED)
        self.assertEqual(
            self.client.get(self.serve_url).status_code, HTTPStatus.FORBIDDEN
        )

    def test_clean_document_is_served(self):
        self._set_status(FileScanStatus.CLEAN)
        self.assertEqual(self.client.get(self.serve_url).status_code, HTTPStatus.OK)
