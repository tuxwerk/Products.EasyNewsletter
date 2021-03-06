# -*- coding: utf-8 -*-
# from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from bs4 import BeautifulSoup
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.EasyNewsletter import _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


VALID_TAGS = [
    'strong',
    'b',
    'em',
    'p',
    'a',
    'ul',
    'ol',
    'li',
    'br',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
]


def sanitize_html(value):
    soup = BeautifulSoup(value, features="lxml")

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.hidden = True

    return soup.renderContents()


class INewsletterSubscriberPortlet(IPortletDataProvider):

    portlet_title = schema.TextLine(
        title=_(u"Title for the portlet."),
        default=u"Newsletter",
        required=True,
    )

    portlet_description = schema.Text(
        title=_(u"Description"),
        default=u"",
        required=False,
    )

    newsletter = schema.Choice(
        title=_(u"Path to Newsletter"),
        vocabulary="Products.EasyNewsletter.newsletters",
        required=True,
    )

    query_salutation = schema.Bool(
        title=_(u"Ask for the salutation"),
        default=True,
        required=False,
    )

    query_firstname = schema.Bool(
        title=_(u"Ask for the firstname"),
        default=False,
        required=False,
    )

    query_name = schema.Bool(
        title=_(u"Ask for the name"),
        default=True,
        required=False,
    )

    query_name_prefix = schema.Bool(
        title=_(u"Ask for the name prefix (aka title)"),
        default=False,
        required=False,
    )

    query_organization = schema.Bool(
        title=_(u"Ask for the company/organization"),
        default=False,
        required=False,
    )

    additional_info = schema.Text(
        title=_(u"Additional info, like terms and conditions"),
        description=_(
            u"It can contain HTML, the following tags are allowed: {0}".format(", ".join(VALID_TAGS))
        ),
        default=u"",
        required=False,
    )


@implementer(INewsletterSubscriberPortlet)
class Assignment(base.Assignment):
    """
    """

    portlet_title = "Newsletter"
    portlet_description = u""
    newsletter = u""
    query_name = True
    query_firstname = False
    query_salutation = True
    query_name_prefix = False
    query_organization = False
    additional_info = u""

    def __init__(
        self,
        portlet_title=u"",
        portlet_description=u"",
        newsletter="",
        query_name=True,
        query_firstname=False,
        query_salutation=True,
        query_name_prefix=False,
        query_organization=False,
        additional_info=u"",
    ):

        self.portlet_title = portlet_title
        self.portlet_description = portlet_description
        self.newsletter = newsletter
        self.query_name = query_name
        self.query_firstname = query_firstname
        self.query_salutation = query_salutation
        self.query_name_prefix = query_name_prefix
        self.query_organization = query_organization
        self.additional_info = additional_info

    @property
    def title(self):
        """
        """
        return _(u"Newsletter subscriber portlet")


class Renderer(base.Renderer):
    """
    """

    render = ViewPageTemplateFile('subscriber.pt')

    @property
    def available(self):
        """
        """
        return True

    def header(self):
        return self.data.portlet_title

    def description(self):
        return self.data.portlet_description

    def get_newsletter(self):
        """
        """
        return self.data.newsletter

    def get_additional_info(self):
        return sanitize_html(self.data.additional_info)


class AddForm(base.AddForm):
    """
    """

    schema = INewsletterSubscriberPortlet

    def create(self, data):
        """
        """
        return Assignment(
            portlet_title=data.get("portlet_title", u""),
            portlet_description=data.get("portlet_description", u""),
            newsletter=data.get("newsletter", ""),
            query_name=data.get("query_name", ""),
            query_firstname=data.get("query_firstname", ""),
            query_salutation=data.get("query_salutation", ""),
            query_name_prefix=data.get("query_name_prefix", ""),
            query_organization=data.get("query_organization", ""),
            additional_info=data.get("additional_info", ""),
        )


class EditForm(base.EditForm):
    """
    """

    schema = INewsletterSubscriberPortlet

    label = _(u"Edit Newsletter portlet")
    description = _(u"This portlet displays the subscriber add form of a newsletter.")
