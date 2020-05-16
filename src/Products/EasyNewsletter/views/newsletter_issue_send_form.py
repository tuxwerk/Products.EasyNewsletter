# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView


class NewsletterIssueSendForm(BrowserView):

    def __call__(self):
        self.newsletter = self.context.get_newsletter()
        return self.index()

    @property
    def sender_name(self):
        return self.newsletter.sender_name

    @property
    def sender_email(self):
        return self.newsletter.sender_email

    @property
    def subject(self):
        return self.context.title

    @property
    def test_receiver(self):
        return self.request.get('test_receiver') or self.newsletter.test_email

    @property
    def receivers_size(self):
        return len(self.context.get_receivers())
