from django import template

from template_multiprocessing.decorators import multiprocess


register = template.Library()


@register.tag
def a_tag(parser, token):
    return ATagNode()


@multiprocess
class ATagNode(template.Node):

    def render(self, context):
        with context.push():
            context["must_not_persist"] = 1
            return "a_tag"
