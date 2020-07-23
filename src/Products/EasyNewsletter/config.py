# -*- coding: utf-8 -*-
# flake8: noqa

from plone import api
from zope.i18nmessageid import MessageFactory

import re

_ = MessageFactory('EasyNewsletter')

PROJECTNAME = 'EasyNewsletter'

ENL_ISSUE_TYPES = ['Newsletter Issue']
ENL_EDITHELPER_TYPES = ['Newsletter', 'Newsletter Issue']

SALUTATION = {
    'ms': _(u'label_salutation_ms', 'Ms.'),
    'mr': _(u'label_salutation_mr', 'Mr.'),
}

# NL_LANGUAGE = DisplayList((
#     ('', _(u'label_choose_nl_language', 'Choose language...')),
#     ('de', _(u'label_salutation_de', 'DE')),
#     ('en', _(u'label_salutation_en', 'EN')),
#     ('fr', _(u'label_salutation_fr', 'FR')),
# ))

MESSAGE_CODE = {
    'email_added': _(
        u'Your email has been registered. A confirmation email was'
        u' sent to your address. Please check your inbox and click '
        u' on the link in the email in order to confirm your'
        u' subscription.'
    ),
    'invalid_email': _(
        u'Please enter a valid email address.'),
    'email_exists': _(
        u'Your email address is already registered.'),
    'invalid_hashkey': _(
        u'Please enter a valid email address.'),
    'subscription_confirmed': _(
        u'Your subscription was successfully confirmed.'),
}

EMAIL_RE = re.compile(
    r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,63}(?:\s|$)", re.IGNORECASE)
