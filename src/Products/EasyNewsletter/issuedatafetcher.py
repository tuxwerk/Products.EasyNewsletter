# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from html2text import HTML2Text
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter import log
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from zope.event import notify
from zope.interface import implementer

import jinja2

@implementer(IIssueDataFetcher)
class IssueDataFetcher(object):
    def __init__(self, issue):
        self.issue = issue

    def __call__(self):
        """
        returns a dict of issue_data, like subject and several parts of
        the issue. This is done so, to split up the send method and
        make it more hookable.
        """
        data = {}

        request = self.issue.REQUEST
        data["subject"] = safe_unicode(request.get("subject")) or safe_unicode(self.issue.title)
        data["body_html"] = safe_unicode(self._render_output_html())

        return data

    def preview_html(self, disable_filter=False, receiver=None):
        receiver = receiver or {}
        html = self._render_output_html()
        html = self.personalize(receiver, html)
        soup = BeautifulSoup(html, features="lxml")
        if not disable_filter:
            for node in soup.findAll(True, {"class": "mailonly"}):
                node.extract()
        return soup.renderContents()

    @property
    def enl(self):
        if not hasattr(self, "_enl"):
            self._enl = self.issue.get_newsletter()
        return self._enl

    def _fullname(self, receiver):
        fullname = receiver.get("fullname") or ""
        fullname = fullname.strip()
        return fullname or self.enl.fullname_fallback

    def _salutation(self, receiver):
        return receiver.get("salutation") or u""

    def _subscriber_salutation(self, receiver):
        return u"{0} {1}".format(
            safe_unicode(self._salutation(receiver)),
            safe_unicode(self._fullname(receiver)),
        )

    def _unsubscribe_info(self, receiver):
        if "uid" not in receiver:
            return {"link": u"", "text": u"", "html": u""}
        unsubscribe_text = self.enl.unsubscribe_string
        unsubscribe_link = "{0}/unsubscribe?subscriber={1}".format(
            self.enl.absolute_url(), receiver["uid"]
        )
        unsubscribe_markup = """<a href="{0}" class="enl_unsubscribe_link">{1}.</a>""".format(
            unsubscribe_link, unsubscribe_text
        )
        return {
            "link": safe_unicode(unsubscribe_link),
            "text": safe_unicode(unsubscribe_text),
            "html": safe_unicode(unsubscribe_markup),
        }

    def _render_output_html(self):
        """ Return rendered newsletter
            with header+body+footer (raw html).
        """
        issue_tmpl = self.issue.restrictedTraverse(str(self.issue.output_template))
        return issue_tmpl.render()

    @property
    def plone_view(self):
        if hasattr(self, "_plone_view"):
            return self._plone_view
        self._plone_view = api.content.get_view(
            name="plone", context=self.enl, request=self.enl.REQUEST
        )
        return self._plone_view

    @property
    def issue_data(self):
        if hasattr(self, "_issue_data"):
            return self._issue_data
        self._issue_data = {}
        self._issue_data["title"]       = self.issue.title
        self._issue_data["description"] = self.issue.description
        self._issue_data["banner_src"]  = self.issue.get_banner_src()
        scales = self.enl.restrictedTraverse("@@images")
        logo_src = ""
        if scales.scale("logo", scale="mini"):
            logo_src = self.enl.absolute_url() + "/@@images/logo/newsletter_logo"
        self._issue_data["logo_src"]      = logo_src
        self._issue_data["date"]          = self.plone_view.toLocalizedTime(self.issue.effective(), long_format=0)
        self._issue_data["month"]         = self.issue.effective().month()
        self._issue_data["year"]          = self.issue.effective().year()
        self._issue_data["calendar_week"] = self.issue.effective().strftime("%V")
        return self._issue_data

    def personalize(self, receiver, text):
        issue_data = self.issue_data
        context = {}

        # receiver data:
        context["receiver"]              = receiver
        context["language"]              = self.enl.language
        context["fullname"]              = self._fullname(receiver)
        context["salutation"]            = self._salutation(receiver)
        context["unsubscribe_info"]      = self._unsubscribe_info(receiver)
        context["UNSUBSCRIBE"]           = context["unsubscribe_info"]["html"]
        context["SUBSCRIBER_SALUTATION"] = self._subscriber_salutation(receiver)
        # issue_data:
        context["language"]              = self.enl.language
        context["issue_title"]           = issue_data["title"]
        context["issue_description"]     = issue_data["description"]
        context["banner_src"]            = issue_data["banner_src"]
        context["logo_src"]              = issue_data["logo_src"]
        context["date"]                  = issue_data["date"]
        context["month"]                 = issue_data["month"]
        context["year"]                  = issue_data["year"]
        context["calendar_week"]         = issue_data["calendar_week"]

        template = jinja2.Template(safe_unicode(text))
        return template.render(**context)

    def create_plaintext_message(self, text):
        """ Create a plain-text-message by parsing the html
            and attaching links as endnotes
        """
        html_to_text = HTML2Text(baseurl=self.issue.absolute_url())
        html_to_text.ul_style_dash = True
        html_to_text.inline_links = False
        html_to_text.wrap_links = False
        return html_to_text.handle(text)
