# -*- coding: utf-8 -*-
from Products.CMFPlone.resources import add_resource_on_request
from Products.Five.browser import BrowserView


class NewsletterIssue(BrowserView):
    def __call__(self):
        add_resource_on_request(self.request, "iframeResizer")
        return self.index()

    @property
    def here_url(self):
        return self.context.absolute_url()
