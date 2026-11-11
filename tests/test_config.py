from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from django_bucketav.config import Settings, conf


class ConfigTest(SimpleTestCase):
    def setUp(self):
        self.settings = Settings()

    def test_module_level_conf(self):
        self.assertIsInstance(conf, Settings)

    def test_enabled(self):
        self.assertTrue(conf.enabled)

        with override_settings(DJANGO_BUCKETAV={"ENABLED": True}):
            self.assertTrue(conf.enabled)

        with override_settings(DJANGO_BUCKETAV={"ENABLED": False}):
            self.assertFalse(conf.enabled)

    def test_models(self):
        # this is the default in testapp.settings
        self.assertEqual(conf.models, {"testapp.MyModelWithBucketAVMixin": ["file"]})

        with override_settings(DJANGO_BUCKETAV={"MODELS": {}}):
            self.assertEqual(conf.models, {})

    def test_incorrect_models_setting_raises_error(self):
        with (
            override_settings(DJANGO_BUCKETAV={"MODELS": "foo"}),
            self.assertRaises(ImproperlyConfigured),
        ):
            conf.models  # noqa: B018

    def test_storage_bucket_name(self):
        self.assertIsNone(conf.storage_bucket_name)

        with override_settings(DJANGO_BUCKETAV={"AWS_STORAGE_BUCKET_NAME": "foo"}):
            self.assertEqual(conf.storage_bucket_name, "foo")

    def test_sns_topic_arn_not_set(self):
        self.assertIsNone(conf.sns_topic_arn_list)

    @override_settings(DJANGO_BUCKETAV={"SNS_TOPIC_ARN": "foo"})
    def test_sns_topic_arn_list_with_arn_string(self):
        self.assertEqual(conf.sns_topic_arn_list, ["foo"])

    @override_settings(DJANGO_BUCKETAV={"SNS_TOPIC_ARNS": ["foo"]})
    def test_sns_topic_arn_list(self):
        self.assertEqual(conf.sns_topic_arn_list, ["foo"])

    @override_settings(DJANGO_BUCKETAV={"SNS_TOPIC_ARNS": {}})
    def test_sns_topic_arn_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            conf.sns_topic_arn_list  # noqa: B018
