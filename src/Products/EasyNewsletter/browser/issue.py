# -*- coding: utf-8 -*-
from plone import api
from plone.protect import PostOnly
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.resources import add_resource_on_request
from Products.EasyNewsletter import _
from Products.EasyNewsletter import log
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides

import transaction


class IssueView(BrowserView):
    """Single Issue View
    """

    def __call__(self):
        add_resource_on_request(self.request, 'iframeResizer')
        return self.index()

    @property
    def here_url(self):
        return self.context.absolute_url()

    def get_public_body(self):
        """ Return the rendered HTML version without placeholders.
        """
        issuedatafetcher = IIssueDataFetcher(self.context)
        preview_html = issuedatafetcher.preview_html()
        return preview_html

    def get_preview(self):
        """ Return the rendered HTML version with all placeholder,
            for admin preview.
        """
        test_receiver = {
            'email': 'john@example.com',
            'fullname': 'John Doe',
            'firstname': 'John',
            'lastname': 'Doe',
            'salutation': 'Dear Mr.',
            'nl_language': 'de',
            'uid': 'xyz',

        }
        issuedatafetcher = IIssueDataFetcher(self.context)
        preview_html = issuedatafetcher.preview_html(
            disable_filter=True, receiver=test_receiver)
        return preview_html
