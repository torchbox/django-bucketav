from django.urls import path

from .views import BucketAVWebhookView


app_name = "django_bucketav"

urlpatterns = [
    path("sns-hook/", BucketAVWebhookView.as_view(), name="sns-hook"),
]
