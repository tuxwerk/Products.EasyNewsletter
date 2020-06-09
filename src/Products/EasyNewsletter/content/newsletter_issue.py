# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.EasyNewsletter import _
from Products.EasyNewsletter import log
from Products.EasyNewsletter.content.newsletter import INewsletter
from Products.EasyNewsletter.content.newsletter import get_content_aggregation_sources_base_path
from Products.EasyNewsletter.interfaces import IIssueDataFetcher
from Products.EasyNewsletter.interfaces import IReceiversPostSendingFilter
from datetime import datetime
from logging import ERROR
from persistent.dict import PersistentDict
from plone import api
from plone import schema
from plone.app import textfield
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.supermodel import model
from z3c import relationfield
from zope.annotation.interfaces import IAnnotations
from zope.component import subscribers
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
import emails
import emails.loader
import transaction
# from zope.component import adapter
# from Products.DCWorkflow.interfaces import IAfterTransitionEvent
# from Products.DCWorkflow.interfaces import IBeforeTransitionEvent
# from Products.DCWorkflow.interfaces import ITransitionEvent
# from Products.DCWorkflow.events import TransitionEvent

SEND_STATUS_KEY = 'PRODUCTS_EASYNEWSLETTER_SEND_STATUS'


@provider(IContextAwareDefaultFactory)
def get_default_output_template(parent):
    """ get ouput template from parent Newsletter
    """
    if INewsletter.providedBy(parent) and parent.__parent__:
        return parent.output_template

# @adapter(IAfterTransitionEvent)
# def transition_event(object, event):
#     print("iuggiuzfgzuifgzuifzuztfuzifuzfzufzufzui")
#     print(event)
#     print(object)

#     if not INewsletterIssue.providedBy(event.object):
#         print(event.object)
#     return

@provider(IContextAwareDefaultFactory)
def get_default_prologue(parent):
    """ get prologue from parent Newsletter
    """
    prologue_output = u""
    if INewsletter.providedBy(parent) and parent.__parent__ and parent.default_prologue:
        prologue_output = parent.default_prologue.raw
    default_prologue = textfield.RichTextValue(
        raw=prologue_output,
        mimeType="text/html",
        outputMimeType="text/x-plone-outputfilters-html",
    )
    return default_prologue


@provider(IContextAwareDefaultFactory)
def get_default_epilogue(parent):
    """ get epilogue from parent Newsletter
    """
    epilogue_output = u""
    if INewsletter.providedBy(parent) and parent.__parent__:
        epilogue_output = parent.default_epilogue.raw
    default_epilogue = textfield.RichTextValue(
        raw=epilogue_output,
        mimeType="text/html",
        outputMimeType="text/x-plone-outputfilters-html",
    )
    return default_epilogue


@provider(IContextAwareDefaultFactory)
def get_default_content_aggregation_sources(parent):
    """ get content_aggregation_sources from parent Newsletter
    """
    if INewsletter.providedBy(parent) and parent.__parent__:
        return parent.content_aggregation_sources


class INewsletterIssue(model.Schema):
    """ Marker interface and Dexterity Python Schema for NewsletterIssue
    """

    model.fieldset(
        "customizations",
        label=_(u"Customizations"),
        fields=[
            "prologue",
            "epilogue",
            "content_aggregation_sources",
            "exclude_all_subscribers",
            "banner",
            "hide_image",
            "output_template",
        ],
    )

    title = schema.TextLine(
        title=_(u"Title"),
        default=u"",
        required=True,
    )

    directives.widget(
        "content_aggregation_sources",
        pattern_options={
            "basePath": get_content_aggregation_sources_base_path,
            "selectableTypes": ["Collection"],
        },
    )
    content_aggregation_sources = relationfield.schema.RelationList(
        title=_(
            u"ENL_content_aggregation_sources_label",
            default=u"Content aggregation sources",
        ),
        description=_(
            u"ENL_content_aggregation_sources_desc",
            default=u"Choose sources to aggregate newsletter content from.",
        ),
        value_type=relationfield.schema.RelationChoice(
            title=u"content_aggretation_source",
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        defaultFactory=get_default_content_aggregation_sources,
        required=False,
    )

    directives.widget(exclude_all_subscribers=SingleCheckBoxBoolFieldWidget)
    exclude_all_subscribers = schema.Bool(
        title=_(u"ENL_label_excludeAllSubscribers", default=u"Exclude all subscribers"),
        description=_(
            u"ENL_help_excludeAllSubscribers",
            default=u"If checked, the newsletter/mailing will not be send  \
                to all subscribers inside the newsletter. Changing this \
                setting does not affect already existing issues.",
        ),
        required=False,
        default=False,
    )

    output_template = schema.Choice(
        title=_(u"enl_label_output_template", default="Output template"),
        description=_(
            u"enl_help_output_template",
            default=u"Choose the template to render the email. ",
        ),
        vocabulary=u"Products.EasyNewsletter.OutputTemplates",
        defaultFactory=get_default_output_template,
        required=True,
    )

    prologue = textfield.RichText(
        title=_(u"prologue", default=u"Prologue"),
        description=_(
            u"prologue_description",
            default=u"You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        defaultFactory=get_default_prologue,
        required=False,
    )

    epilogue = textfield.RichText(
        title=_(u"epilogue", default=u"Epilogue"),
        description=_(
            u"epilogue_description",
            default=u"You can use placeholders like\
                {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        defaultFactory=get_default_epilogue,
        required=False,
    )

    directives.widget(hide_image=SingleCheckBoxBoolFieldWidget)
    hide_image = schema.Bool(
        title=_(u"label_issueHideImage", default=u"Hide banner image."),
        description=_(
            u"enl_issue_help_hide_image",
            default=u"If checked, the banner image defined on newsletter \
                    or on this issue will not be used.",
        ),
        required=False,
        default=False,
        readonly=False,
    )

    banner = namedfile.NamedBlobImage(
        title=_(u"ENL_image_label", default=u"Banner image"),
        description=_(
            u"ENL_image_desc",
            default=u"Banner image, you can include in the templates by"
            + u"\n adding the {{banner}} placeholder into it."
            + u" By default it should be 600x200 pixel.",
        ),
        required=False,
    )

    # directives.order_after(content_aggregation_source="IBasic.title")
    # directives.order_after(output_template="IRichText.text")


def context_property(name):
    def getter(self):
        return getattr(self.context, name)

    def setter(self, value):
        setattr(self.context, name, value)

    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


@implementer(INewsletterIssue)
class NewsletterIssue(Container):
    """
    """

    context_property('content_aggregation_sources')

    def get_newsletter(self):
        return self.__parent__

    def get_receivers(self):
        receivers = self.get_newsletter().get_receivers()
        # Filter all receivers which already got an email
        for subscriber in subscribers([self],
                                      IReceiversPostSendingFilter):
            receivers = subscriber.filter(receivers)
        return receivers

    def has_image(self):
        has_image = bool(self.get_banner_src())
        return has_image

    def has_logo(self):
        enl = self.get_newsletter()
        has_logo = getattr(enl.aq_explicit, 'logo', None)
        return has_logo

    def send(self, test=False, recipients=None):
        enl = self.get_newsletter()
        sender_name = enl.sender_name
        sender_email = enl.sender_email
        receivers = test and recipients or self.get_receivers()

        self.mail_host = api.portal.get_tool('MailHost')
        log.info('Using mail delivery service "%r"' % self.mail_host)

        send_counter = 0
        send_error_counter = 0

        issue_data_fetcher = IIssueDataFetcher(self)
        # get issue data
        issue_data = issue_data_fetcher()
        status_adapter = ISendStatus(self)

        # prepare raw email
        m = emails.Message(
            subject=issue_data['subject'],
            mail_from=(sender_name, sender_email),
        )

        for receiver in receivers:
            # check for workflow state
            if not test and api.content.get_state(obj=self) != 'sending':
                log.exception(u"Newsletter sending aborted")
                return

            send_status = {
                'successful': None,
                'error': None,
                'datetime': datetime.now(),
            }
            html_text = issue_data_fetcher.personalize(
                receiver, issue_data['body_html']
            )
            plain_text = issue_data_fetcher.create_plaintext_message(html_text)
            m.set_html(html=html_text)
            m.set_text(text=plain_text)
            m.set_mail_to((receiver['fullname'], receiver['email']))
            m.transform(
                images_inline=True, # FIXME: Add option to newsletter
                base_url=self.absolute_url(),
                cssutils_logging_level=ERROR,
            )
            message_string = m.as_string()
            if 'HTTPLoaderError' in message_string:
                log.exception(u"Transform message failed: {0}".format(message_string))
            try:
                self.mail_host.send(message_string, immediate=True)
                send_status['successful'] = True
                log.info('Sent newsletter to "%s"' % receiver['email'])
                send_counter += 1
            except Exception as e:  # noqa
                send_status['successful'] = False
                send_status['error'] = e
                log.exception(
                    'Sending newsletter to "%s" failed, with error "%s"!'
                    % (receiver['email'], e)
                )
                send_error_counter += 1

            if test:
                continue

            # Update receivers information to annotations on each mail
            receiver['status'] = send_status
            status_adapter.add_records(receivers)
            transaction.commit()

        log.info(
            'Newsletter was sent to (%s) receivers. (%s) errors occurred!'
            % (send_counter, send_error_counter)
        )

        if test:
            return

        # change status only for a 'regular' send operation (not 'is_test')
        api.content.transition(obj=self, transition='sending_completed')
        # DONT SET THIS
        #self.context.setEffectiveDate(DateTime())
        #self.context.reindexObject(idxs=['effective'])

    # XXX we should cache this call, it's called twice
    def get_banner_src(self):
        """ find banner image, if not set on Issue we use the one from the Newsletter
        """
        img_src = ""
        if self.hide_image:
            return img_src

        scales = self.restrictedTraverse('@@images')
        if scales.scale('banner', scale='mini'):
            img_src = self.absolute_url() + "/@@images/banner/newsletter_banner"
            return img_src

        enl = self.get_newsletter()
        scales = enl.restrictedTraverse('@@images')
        if scales.scale('banner', scale='mini'):
            img_src = enl.absolute_url() + "/@@images/banner/newsletter_banner"

        return img_src

    def getHeader(self):
        if self.prologue:
            return self.prologue.output

        return u""

    def getFooter(self):
        if self.epilogue:
            return self.epilogue.output

        return u""

    def getText(self):
        if self.text:
            return self.text.output

        return u""

    def receivers_sent(self):
        return self.receivers_failed() + self.receivers_successful()

    def receivers_total(self):
        return len(self.status_adapter().get_records())

    def receivers_failed(self):
        return len(self.status_adapter().get_keys(successful=False))

    def receivers_successful(self):
        return len(self.status_adapter().get_keys(successful=True))

    def status_adapter(self):
        return ISendStatus(self)

    # bbb: we should print a deprecation message here
    def getOutputTemplate(self):
        return self.output_template

class ISendStatus(Interface):
    """Manage send status for newsletter issues."""

    def clear():  # noqa: N805
        """Clear all records."""

    def add_records(records):  # noqa: N805
        """Add new records."""

    def get_records(status=None):  # noqa: N805
        """Return a list of all status information records."""

    def get_keys(status=None):  # noqa: N805
        """Return a list of all status information keys."""


@implementer(ISendStatus)
class SendStatus(object):
    def __init__(self, context):
        self.context = context

    def clear(self):
        """Clear all records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY in annotations:
            del annotations[SEND_STATUS_KEY]

    def add_records(self, records, key='email'):
        """Add new records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            annotations[SEND_STATUS_KEY] = PersistentDict()
        data = {data.get(key): data for data in records if data.get(key) is not None}
        annotations[SEND_STATUS_KEY].update(data)

    def get_records(self, successful=None):
        """Return a list of all status information records."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            return []
        items = annotations[SEND_STATUS_KEY].values()
        if successful is not None:
            items = [
                item for item in items if
                item.get('status', {}).get('successful', None) == successful
            ]
        return items

    def get_keys(self, successful=None):
        """Return a list of all status information keys."""
        annotations = IAnnotations(self.context)
        if SEND_STATUS_KEY not in annotations:
            return []
        items = annotations[SEND_STATUS_KEY].items()
        if successful is not None:
            items = [
                key for key, item in items if
                item.get('status', {}).get('successful', None) == successful
            ]
        return items
