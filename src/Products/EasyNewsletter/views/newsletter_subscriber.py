# -*- coding: utf-8 -*-

from Products.EasyNewsletter import _
from Products.Five.browser import BrowserView


class NewsletterSubscriber(BrowserView):

    def __call__(self):
        # Implement your own actions:
        return self.index()
