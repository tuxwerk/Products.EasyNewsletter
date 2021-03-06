# -*- coding: utf-8 -*-
import os
import tempfile
import zc.lockfile

from Products.Five.browser import BrowserView
from Products.EasyNewsletter import log
from Products.EasyNewsletter import config
from plone.uuid.interfaces import IUUID
from plone import api

import time

class NewsletterQueueSend(BrowserView):
    def __call__(self):
        """
        xxx
        """
        #PostOnly(self.request)
        return self.send_queued_newsletter_issues()

    def send_queued_newsletter_issues(self):
        """Sends queued issues
        """
        LOCKFILE_NAME = os.path.join(tempfile.gettempdir(),
                                     __name__ + "_" + str(self.context.aq_base.id)) + ".lock"

        try:
            lock = zc.lockfile.LockFile(LOCKFILE_NAME)
        except zc.lockfile.LockError:
            log.info("EasyNewsletter: NewsletterQueueSend is locked by another process (%r)" % (LOCKFILE_NAME))
            return

        try:
            issues = api.content.find(
                context=self.context,
                portal_type=config.ENL_ISSUE_TYPES,
                review_state='sending',
                sort_on='effective',
                sort_order='reverse',
            )
            for brain in issues:
                issue = brain.getObject()
                log.info("EasyNewsletter: send issue %s" % (issue.id))
                issue.send()
            log.info("EasyNewsletter: %d issues sent" % (len(issues)))
            return
        finally:
            lock.close()
