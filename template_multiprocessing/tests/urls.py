from django.conf.urls import url, include

from template_multiprocessing.tests.views import TestView


urlpatterns = [
    url(
        r"^test/",
        TestView.as_view(template_name="tests/test.html"),
        name="test"
    )
]
