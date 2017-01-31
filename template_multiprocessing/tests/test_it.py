from django.core.urlresolvers import reverse
from django.test import TestCase


class TheTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TheTestCase, cls).setUpTestData()

    def test_it(self):
        url = reverse("test")
        response = self.client.get(url)
        self.assertHTMLEqual("a_tag\n" * 16, response.content)
