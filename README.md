# django-bucketav

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://img.shields.io/pypi/v/django-bucketav.svg?style=flat)](https://pypi.org/project/django-bucketav)
[![Build status](https://img.shields.io/github/actions/workflow/status/torchbox/django-bucketav/test.yml?branch=main)](https://github.com/torchbox/django-bucketav/actions)

## Links

- [Documentation](https://github.com/torchbox/django-bucketav/blob/main/README.md)
- [Changelog](https://github.com/torchbox/django-bucketav/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/torchbox/django-bucketav/blob/main/CONTRIBUTING.md)
- [Discussions](https://github.com/torchbox/django-bucketav/discussions)
- [Security](https://github.com/torchbox/django-bucketav/security)

## Overview

Scan Django/Wagtail uploads using [BucketAV](https://bucketav.com/).
The package provides a webhook endpoint that is pinged by BucketAV with the results of the scan.

## Installation

```sh
$ pip install django-bucketav
# Or, with uv:
$ uv pip install django-bucketav
# Or, with Poetry:
$ poetry add django-bucketav
```

Update your URLs file:

```python
# urls.py

from django.urls import include, path

urlpatterns = [
    path("bucketav/", include("django_bucketav.urls")),
]
```

Note that the "bucketav/" prefix can be anything of your choosing.

## Configuration

Add or update the `DJANGO_BUCKETAV_MODELS` configuration dictionary in your project's settings file.
The setting is used to configure which `FileField`s this package should handle.

```python
# settings.py

DJANGO_BUCKETAV = {
    "ENABLED": True,  # defaults to true
    "MODELS": {
        "myapp.Document": ["file", "another_file_field"],
        "myapp.Image": ["image"],
    },
    "AWS_STORAGE_BUCKET_NAME": "<bucket name>",  # Optional. The BucketAV bucket name, usually the same as the file storage one
    "SNS_TOPIC_ARN": "ARN string",  # Optional. An SNS topic ARN to use for the allowlist
    "SNS_TOPIC_ARNS": ["ARN1", "ARN2"],  # -OR- a list of topic ARNS
}
```

In the above example, BucketAV will ping the Django app on the `/bucketav/sns-hook/` URL path with the result of
an antivirus scan. `django-bucketav` will look for the given file path in the `file` and `another_file_field` fields
of the `Document` model, as well as the `image` field of the `Image` model.

If it finds such a reference, it will emit a `scan_result_received` Django signal that your app can handle
following [the established Django signals processes](https://docs.djangoproject.com/en/6.1/topics/signals/) :

```python
# myapp/signal_handlers.py

from typing import TYPE_CHECKING
from django.utils import timezone

if TYPE_CHECKING:
    from django_bucketav.models import FileScanStatus

from .models import Document


def update_scan_status_for_instance(
    sender, instance: Document, file_scan_status: FileScanStatus, **kwargs
):
    instance.scan_status = file_scan_status
    instance.last_scanned_at = timezone.now()
    instance.save()
```

### The (optional) `BucketAVMixin` class

The package provides a `BucketAVMixin` model mixin which you can use for convenience. Any Django model that
inherits from `BucketAVMixin` will get a `bucketav_scan_status` and a `bucketav_last_scanned_at` field.
And if the model is referenced in the `DJANGO_BUCKETAV_MODELS` Django setting, it will automatically be updated
every time BucketAV sends an update for a file managed by it.

## Wagtail

To make your Wagtail instance work with the package, add `django_bucketav.wagtail` to your `INSTALLED_APPS`, and ensure
your custom document model inherits from `BucketAVMixin`:

```python
from wagtail.documents.models import AbstractDocument
from wagtail.documents.models import Document as WagtailDocument

from django_bucketav.models import BucketAVMixin


class CustomDocument(BucketAVMixin, AbstractDocument):
    admin_form_fields = WagtailDocument.admin_form_fields
    ...
```

`django_bucketav.wagtail` adds a [`before_serve_document`](https://docs.wagtail.org/en/stable/reference/hooks.html#before-serve-document) hook
that will block serving any documents that are not marked as clean. Note that this will be skipped if
[`WAGTAILDOCS_SERVE_METHOD`](https://docs.wagtail.org/en/stable/reference/settings.html#wagtaildocs-serve-method) is set to `redirect`.

## Contributing

All contributions are welcome! See [CONTRIBUTING.md](https://github.com/torchbox/django-bucketav/blob/main/CONTRIBUTING.md)

Supported versions:

- Python 3.12, 3.13, 3.14, 3.15
- Django 5.2, 6.0, 6.1
- Wagtail 7.4 (LTS), 8.0, 8.1
