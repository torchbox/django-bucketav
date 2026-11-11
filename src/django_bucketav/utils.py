import operator

from functools import reduce
from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models import Q

from .config import conf


if TYPE_CHECKING:
    from django.db import models

    ObjectForKeyReturnType = type[models.Model] | None


def get_object_for_key(file_key: str) -> "ObjectForKeyReturnType":
    for model_string, fields in conf.models.items():
        model = apps.get_model(model_string)

        filters = reduce(operator.or_, [Q(**{field: file_key}) for field in fields])

        instance = model.objects.filter(filters).first()
        if instance is not None:
            return instance

    return None
