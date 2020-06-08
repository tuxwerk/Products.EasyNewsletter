# -*- coding: utf-8 -*-

from plone import api
from plone.protect.utils import addTokenToUrl
from Products.EasyNewsletter import _
from Products.EasyNewsletter import log
from Products.EasyNewsletter import config
from Products.EasyNewsletter.interfaces import ISubscriberSource
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

class NewsletterSubscribers(BrowserView):
    # TODO: we should move these indexes from FieldIndex to ZCTextIndex
    # see setuphandlers.py for indexes creation
    searchable_params = ("SearchableText",)

    def __call__(self):
        if self.can_delete():
            self.delete()
        return self.index()

    # FIXME: use get_recipients method in newsletter
    def subscribers(self):
        query = dict(
            portal_type="Newsletter Subscriber",
            context=self.context,
            sort_on="email",
        )
        form = self.request.form
        for k in self.searchable_params:
            if form.get(k):
                if k == "SearchableText":
                    searchterm = form.get(k)
                    if not searchterm.endswith("*"):
                        searchterm += "*"
                    query[k] = searchterm
                else:
                    query[k] = form.get(k)
        subscribers = list()

        # Plone subscribers
        for brain in api.content.find(**query):
            if brain.salutation:
                salutation = config.SALUTATION.get(brain.salutation, "")
            else:
                salutation = ""
            subscribers.append(
                dict(
                    id=brain.getId,
                    source="plone",
                    deletable=True,
                    creation_date=brain.creation_date,
                    email=brain.email,
                    getURL=brain.getURL(),
                    salutation=salutation,
                    name_prefix=brain.name_prefix,
                    firstname=brain.firstname,
                    lastname=brain.lastname,
                    nl_language=brain.nl_language,
                    organization=brain.organization,
                )
            )

        return subscribers

    def can_delete(self):
        meth = self.request.get("REQUEST_METHOD")
        delete_button = self.request.get("delete")
        return meth.lower() == "post" and delete_button

    def delete(self):
        """ delete all the selected subscribers
        """
        ids = self.request.get("subscriber_ids", [])
        if not ids:
            msg = _(u"No subscriber selected!")
            api.portal.show_message(msg, request=self.request, type="error")
            return False
        existing = self.context.objectIds()
        # avoid wrong id to be submitted
        to_remove = [i for i in ids if i in existing]
        self.context.manage_delObjects(to_remove)
        msg = _(u"subscriber/s deleted successfully")
        api.portal.show_message(msg, request=self.request, type="info")
        return True

    def addTokenToUrl(self, url):
        return addTokenToUrl(url)
