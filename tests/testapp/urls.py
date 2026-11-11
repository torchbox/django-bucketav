from django.urls import include, path


urlpatterns = [
    path("bucketav/", include("django_bucketav.urls")),
]
