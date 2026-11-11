from django.test import TestCase, override_settings
from testapp.models import MyModelWithBucketAVMixin

from django_bucketav.utils import get_object_for_key

from .utils import get_mymodel_with_bucketav_mixin_instance


class UtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.instance = get_mymodel_with_bucketav_mixin_instance()
        cls.file_key = str(cls.instance.file)

    def test_get_instance_with_key(self):
        discovered_object = get_object_for_key(self.file_key)
        self.assertIsInstance(discovered_object, MyModelWithBucketAVMixin)
        self.assertEqual(discovered_object.pk, self.instance.pk)

    def test_get_unknown_file_key(self):
        discovered_object = get_object_for_key("not-a-file")
        self.assertIsNone(discovered_object)

    @override_settings(DJANGO_BUCKETAV={"MODELS": {}})
    def test_no_models(self):
        discovered_object = get_object_for_key(self.file_key)
        self.assertIsNone(discovered_object)

    @override_settings(DJANGO_BUCKETAV={"MODELS": {"testapp.MyModel": ["file"]}})
    def test_model_not_covered_by_settings(self):
        discovered_object = get_object_for_key(self.file_key)
        self.assertIsNone(discovered_object)

    @override_settings(DJANGO_BUCKETAV={"MODELS": {"testapp.GenericModel": ["name"]}})
    def test_unrelated_model(self):
        discovered_object = get_object_for_key(self.file_key)
        self.assertIsNone(discovered_object)
