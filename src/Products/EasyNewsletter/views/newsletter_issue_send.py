# -*- coding: utf-8 -*-

from datetime import datetime
from DateTime import DateTime
from plone import api
from plone.protect import PostOnly
from Products.EasyNewsletter import _
from Products.EasyNewsletter import log
from Products.EasyNewsletter.content.newsletter_issue import ISendStatus
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.Five.browser import BrowserView
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility
from logging import ERROR

import emails
import emails.loader
import transaction

class PloneMessageSendMixin:
    """
    """

    def __init__(self):
        pass


class Message(
    PloneMessageSendMixin,
    emails.message.MessageTransformerMixin,
    emails.message.MessageSignMixin,
    emails.message.MessageBuildMixin,
    emails.message.BaseMessage,
):
    """
    Email message with:
    - DKIM signer
    - mailhost compatible send
    - Message.transformer object
    """


class NewsletterIssueSend(BrowserView):
    @property
    def is_test(self):
        return self.request.form.get('test') or False

    def __call__(self):
        """
        sets workflow state to sending and then redirects to step2 with UID as
        parameter as simple safety belt.
        """
        PostOnly(self.request)
        if self.is_test:  # test must not modify the state
            enl = self.context.get_newsletter()
            self.context.send(True, self._get_test_recipients())
            api.portal.show_message(
                message=_('Newsletter was sent to test recipients'),
                request=self.request,
            )
            return self.request.response.redirect(self.context.absolute_url())

        # Queue the newsletter issue
        self._send_issue_prepare()
        api.portal.show_message(
            message=_("The newsletter issue has been queued for sending."),
            request=self.request,
        )
        return self.request.response.redirect(self.context.absolute_url())

    def _send_issue_prepare(self):
        self.request['enlwf_guard'] = True
        api.content.transition(obj=self.context, transition='send')
        # commit the transaction so that identical incoming requests, for
        # whatever reason, will not trigger another send
        transaction.commit()
        self.request['enlwf_guard'] = False

    # FIXME: remove this?
    def send_issue_immediately(self):
        """convinience view for cron and similar

        never call this from UI - needs a way to protect
        currently manager only
        """
        self._send_issue_prepare()
        self.context.send()

    def _get_test_recipients(self):
        enl = self.context.get_newsletter()

        # test sending
        test_receiver = self.request.get('test_receiver', enl.test_email)

        salutation = enl.salutation_mappings.get('mr', '')
        receivers = [
            {
                'email': test_receiver,
                'fullname': 'Test Member',
                'salutation': salutation.get(self.context.language, ''),
                # 'nl_language': self.language
            }
        ]
        return receivers
