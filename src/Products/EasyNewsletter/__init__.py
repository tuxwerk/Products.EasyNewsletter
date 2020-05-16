# -*- coding: utf-8 -*-
# avoid circular import
from Products.EasyNewsletter import config  # noqa
from zope.i18nmessageid import MessageFactory
from logging import getLogger

log = getLogger("Products.EasyNewsletter")
_ = MessageFactory('EasyNewsletter')
