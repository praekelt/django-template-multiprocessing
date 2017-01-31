from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(ViewsTestCase, cls).setUpTestData()

    def test_element_partial(self):
        url = reverse("test")
        response = self.client.get(url)
        self.assertHTMLEqual("a_tag\n" * 16, response.content)
