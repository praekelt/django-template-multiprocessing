Django Template Multiprocessing
===============================
**Use all your CPU cores to render templates.**

.. figure:: https://travis-ci.org/praekelt/django-template-multiprocessing.svg?branch=develop
   :align: center
   :alt: Travis

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``django-template-multiprocessing`` to your Python path.

#. Add ``template_multiprocessing`` to your ``INSTALLED_APPS`` setting.

Overview
--------

Django's context object that is used by the template engine is not thread-safe
by design, but your template tags may be thread safe. You should make use of
parallel processing for those cases.

Usage
-----

Mark your template tag node as multiprocess safe by using a decorator::

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

Frequently asked questions
--------------------------

**How do I know if my template tag is thread safe?**

If you push the context in the render method before modifying it then your tag
is probably thread safe.

**What is the speedup?**

It depends :) If you have more than one heavy template tag in a template then
the speedup is large, else it may even make things slower. Don't decorate
lightweight template tags nodes with multiprocess.

**Will it help on a busy site?**

Unless all the cores for the server hosting your site are constantly under load
it should help.

**You use threads and multiprocess interchangably in this doc!**

Threading is an older concept and better understood by developers. Also, if
something is thread-safe then it will probably work with multiprocessing, so I
stuck with that terminology.

