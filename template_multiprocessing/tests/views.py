from django.contrib.auth.models import User
from django.views.generic import TemplateView


class TestView(TemplateView):
    template_name = "tests/aview.html"

    def get_context_data(self, **kwargs):
        di = super(TestView, self).get_context_data()
        # Waste CPU
        for i in range(10000):
            list(User.objects.all())
        return di
