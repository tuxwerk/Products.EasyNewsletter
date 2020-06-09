# -*- coding: utf-8 -*-
# from z3c.form.browser.radio import RadioFieldWidget
from plone import api
from plone import schema
from plone.app import textfield
from plone.app.z3cform.widget import SingleCheckBoxBoolFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.namedfile import field as namedfile
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from Products.EasyNewsletter import _
from Products.EasyNewsletter import log
from Products.EasyNewsletter.behaviors.plone_user_group_recipients import IPloneUserGroupRecipients
from z3c import relationfield
from zope.component import getUtility
from zope.interface import implementer

def get_default_output_template():
    registry = getUtility(IRegistry)
    templates_keys = list(registry.get("Products.EasyNewsletter.output_templates"))
    if not templates_keys:
        return
    if "output_default" not in templates_keys:
        default_tmpl_key = "output_default"
    else:
        default_tmpl_key = templates_keys[0]
    return default_tmpl_key


def _get_base_path(path):
    base_obj = api.content.get(path)
    if not base_obj:
        return
    base_path = "/".join(base_obj.getPhysicalPath())
    return base_path


def get_content_aggregation_sources_base_path(context):
    return _get_base_path("/")


class INewsletter(model.Schema):
    """ Marker interface and Dexterity Python Schema for Newsletter
    """

    model.fieldset(
        "personalization",
        label=_(u"Personalization"),
        fields=[
            "salutations",
            "fullname_fallback",
            "default_prologue",
            "default_epilogue",
        ],
    )

    model.fieldset(
        "subscription",
        label=_(u"Subscription"),
        fields=[
            "unsubscribe_string",
            "subscriber_confirmation_mail_subject",
            "subscriber_confirmation_mail_text",
        ],
    )

    model.fieldset(
        "layout",
        label=_(u"Layout"),
        fields=[
            "logo",
            "banner",
            "output_template",
            "custom_css",
            "footer",
        ],
    )

    model.fieldset(
        "recipients",
        label=_(u"Recipients"),
        fields=["exclude_all_subscribers"]
    )

    sender_email = schema.TextLine(
        title=_(u"Sender email"),
        description=_(
            u"Default for the sender address of the newsletters.",
        ),
        required=True,
    )

    sender_name = schema.TextLine(
        title=_(u"Sender name"),
        description=_(
            u"Default for the sender name of the newsletters.",
        ),
        required=True,
    )

    test_email = schema.TextLine(
        title=_(u"Test email"),
        description=_(
            u"Default for the test email address."
        ),
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
            u"Content aggregation sources",
        ),
        description=_(
            u"Choose sources to aggregate newsletter content from.",
        ),
        value_type=relationfield.schema.RelationChoice(
            title=u"content_aggretation_source",
            vocabulary="plone.app.vocabularies.Catalog",
        ),
        required=False,
    )

    salutations = schema.List(
        title=_(u"Subscriber salutations."),
        description=_(
            u'Define here possible salutations for subscriber. \
            One salutation per line in the form of: "mr|Dear Mr.". \
            The left hand value "mr" or "ms" is mapped to salutation \
            of each subscriber and then the right hand value, which \
            you can customize is used as salutation.',
        ),
        default=[u"mr|Dear Mr.", u"ms|Dear Ms.", u"default|Dear"],
        value_type=schema.TextLine(title=u"salutation"),
        required=True,
    )

    fullname_fallback = schema.TextLine(
        title=_(
            u"Fallback for subscribers without a name.",
        ),
        description=_(
            u"This will be used if the subscriber has no fullname.",
        ),
        default=_(u"Sir or Madam"),
        required=True,
    )

    unsubscribe_string = schema.TextLine(
        title=_(u"Text for the unsubscribe link"),
        description=_(
            u"This will replace the placeholder {{UNSUBSCRIBE}}.",
        ),
        default=_(u"Click here to unsubscribe"),
        required=True,
    )

    banner = namedfile.NamedBlobImage(
        title=_(u"Banner image"),
        description=_(
            u"Banner image, you can include in the templates by \
            adding the {{banner}} placeholder into it. \
            By default it should be 600x200 pixel.",
        ),
        required=False,
    )

    logo = namedfile.NamedBlobImage(
        title=_(u"Logo image"),
        description=_(
            u"Logo image, you can include it in the templates by \
            adding the {{logo}} placeholder into it.",
        ),
        required=False,
    )

    footer = textfield.RichText(
        title=_(u"Footer"),
        description=_(
            u"This is used as a the footer in the newsletter.",
        ),
        default=u"""
<table border="0" cellpadding="10" cellspacing="0" width="100%">
  <tr>
    <td valign="top" style="color:#FFFFFF;">
      Publisher:<br />
      <br />
      <b>Example organization</b><br />
      <br />
      Example street 43<br />
      04170 Leipzig<br />
      GERMANY<br />
      <br />
      Phone: 03274754983<br />
      <br />
    </td>
    <td valign="top" style="color:#FFFFFF;">
      Responsible:<br />
      <br />
      <b>Jon Doe</b><br />
      CEO<br />
      <br />
      Editorial office:<br />
      <b>Jonny Cash</b>
    </td>
  </tr>
</table>
""",
        required=False,
    )

    default_prologue = textfield.RichText(
        title=_(u"Default prologue"),
        description=_(
            u"This is used as a default \
            for new issues. You can use placeholders like\
            {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        default=_(u"<p>{{SUBSCRIBER_SALUTATION}}</p><br />"),
        required=False,
    )

    default_epilogue = textfield.RichText(
        title=_(u"Default epilogue"),
        description=_(
            u"This is used as a default \
            for new issues. You can use placeholders like \
            {{SUBSCRIBER_SALUTATION}} and {{UNSUBSCRIBE}} here.",
        ),
        default=_(u"<h1>Newsletter for Plone</h1>\n<p>{{UNSUBSCRIBE}}</p>"),
        required=False,
    )

    # FIXME: what does the text mean?
    directives.widget(exclude_all_subscribers=SingleCheckBoxBoolFieldWidget)
    exclude_all_subscribers = schema.Bool(
        title=_(u"Exclude all subscribers"),
        description=_(
            u"If checked, the newsletter/mailing will not be send  \
            to all subscribers inside the newsletter. Changing this \
            setting does not affect already existing issues.",
        ),
        required=False,
        default=False,
    )

    output_template = schema.Choice(
        title=_(u"Output template"),
        description=_(
            u"Choose the template to render the email. ",
        ),
        vocabulary=u"Products.EasyNewsletter.OutputTemplates",
        defaultFactory=get_default_output_template,
        required=True,
    )

    custom_css = schema.Text(
        title=_(u"CSS customisation"),
        description=_(
            u"Will be included in the output template.",
        ),
        default=_(u""),
        required=False,
    )

    subscriber_confirmation_mail_subject = schema.TextLine(
        title=_(
            u"Subscriber confirmation mail subject",
        ),
        default=_(u'Confirm your newsletter subscription'),
        required=True,
    )

    subscriber_confirmation_mail_text = schema.Text(
        title=_(
            u"Subscriber confirmation mail text",
        ),
        description=_(
            u"Text used for confirmation email. It may \
            include the following placeholders: \
            ${newsletter_title}, ${subscriber_email} and \
            ${confirmation_url}!",
        ),
        default=_(
            u"""\
            You subscribe to the ${newsletter_title}.

Your registered email is: ${subscriber_email}
Please click on the link to confirm your subscription:
${confirmation_url}"""
        ),
        required=True,
    )

    directives.order_after(content_aggregation_sources="IBasic.title")
    directives.order_after(test_email="IBasic.title")
    directives.order_after(sender_name="IBasic.title")
    directives.order_after(sender_email="IBasic.title")


@implementer(INewsletter)
class Newsletter(Container):
    """
    """

    def get_newsletter(self):
        return self

    def get_receivers(self):
        enl_receivers = []
        if not self.exclude_all_subscribers:
            for subscriber_brain in api.content.find(
                portal_type='Newsletter Subscriber', context=self
            ):
                if not subscriber_brain:
                    continue
                subscriber = subscriber_brain.getObject()
                salutation_key = subscriber.salutation or 'default'
                salutation = self.salutation_mappings.get(salutation_key, {})
                enl_receiver = {
                    'email': subscriber.email,
                    'gender': subscriber.salutation,
                    'name_prefix': subscriber.name_prefix,
                    'firstname': subscriber.firstname or u'',
                    'lastname': subscriber.lastname or u'',
                    'fullname': ' '.join(
                        [subscriber.firstname or u'', subscriber.lastname or u'']
                    ),
                    'salutation': salutation.get(
                        None,  # subscriber.getNl_language(),
                        salutation.get(self.language or 'en', ''),
                    ),
                    'uid': subscriber.UID(),
                    # 'nl_language': subscriber.getNl_language()
                }

                enl_receivers.append(enl_receiver)

        receivers_raw = enl_receivers

        # get subscribers over selected plone members anpid groups
        plone_receivers = []
        try:
            plone_receivers_adapter = IPloneUserGroupRecipients(self)
            plone_receivers = plone_receivers_adapter.get_plone_subscribers()
        except TypeError:
            plone_receivers_adapter = None

        receivers_raw += plone_receivers
        receivers = self._unique_receivers(receivers_raw)

        return receivers

    @property
    def salutation_mappings(self):
        """
        returns mapping of salutations. Each salutation itself is a dict
        with key as language. (prepared for multilingual newsletter)
        """
        result = {}
        lang = self.language or 'en'

        for line in self.salutations:
            if "|" not in line:
                continue
            key, value = line.split('|')
            result[key.strip()] = {lang: value.strip()}
        return result

    def _unique_receivers(self, receivers_raw):
        receivers = []
        mails = []
        for receiver in receivers_raw:
            if receiver['email'] in mails:
                continue
            mails.append(receiver['email'])
            receivers.append(receiver)
        return receivers
