EasyNewsletter
==============

.. image:: https://secure.travis-ci.org/collective/Products.EasyNewsletter.png?branch=master
    :target: http://travis-ci.org/collective/Products.EasyNewsletter

.. image:: https://coveralls.io/repos/github/collective/Products.EasyNewsletter/badge.svg?branch=master
    :target: https://coveralls.io/github/collective/Products.EasyNewsletter?branch=master

EasyNewsletter is a simple but powerful newsletter/mailing product for Plone.

Compatibility
-------------

EasyNewsletter versions >= 4.x Plone 5.1 only, they are using DX but still have Archetypes dependencies for migration.
EasyNewsletter versions >= 5.x are Plone 5.1 above only, they are free of Archetypes and support Python 3.
For Plone versions < 5.1, use the 3.x branch and releases of EasyNewsletter!

For Python 2.7 you have to pin down html2text:

    html2text = <2019.8.11


Features
========

* Plain text and HTML newsletters (including images)

* manual written newsletters/mailings

* automatic Plonish newsletters/mailings: Utilize Plone's Collections to collect content)

* send out daily/weekly/monthly issues automatically,
  based on collections (by cron or clock-server)

* flexible templates for Collections, to generate newsletter content

* TTW customizable output template to generate HTML newsletters

* personalized emails

* subscribing/ unsubscribing

* import/export subscribers via CSV

* use Plone Members/Groups as receivers (works also with Membrane)

* external subscriber filtering/manipulation with plugins (filter out or add more subscribers)

* synchronous/ asynchronous send out [currently not reimplemented, if you need this, you have to wait for future versions or fund the work on this feature]


* external

  * subscriber sources (configured through a Zope utility) [currently not reimplemented]
  * delivery services (other than Plone MailHost) [currently not reimplemented]


Requirements
============

* Plone 5.1 (tested)
* Dexterity (Archetypes for migration)


Installation
============

1. Add ``Products.EasyNewsletter`` to your buildout
2. Run your buildout script
3. Restart zope
4. Install EasyNewsletter via Plone Management Interface
5. Add a "Newsletter Subscriber" portlet and select a Newsletter
   (To this newsletter the subscribers will be added).

Documentation
=============

TODO

Message Queue
=============

To process queued newsletters setup ClockServer in your Zope instance:

  zope-conf-additional =
      <clock-server>
        # plonesite is your plone path
        # www.mysite.com your site url
        method /VirtualHostBase/http/www.mysite.com:80/plonesite/VirtualHostRoot/send-queued-newsletter-issues
        period 300
        user admin
        password admin
      </clock-server>

**Note**: Do not set up this ClockServer on more than one
instance.  The processing makes sure it's not invoked twice at the
same time by using file locking. This file locking won't work if you
configure the clock server on two different servers.

Source Code
===========

Source code is at GitHub: https://github.com/collective/Products.EasyNewsletter


Bug tracker
===========

Issue tracker is at GitHub: https://github.com/collective/Products.EasyNewsletter/issues

ToDo
====

funding welcome ;)

- async task queue for WGSI as an alternative to collective.taskqueue which will not support WGSI
- Integration of Mosaico newsletter editor
- External subscriber sources / delivery services
- content migration AT >> DX


Authors
=======

* initial release: Kai Dieffenbach
* Maik Derstappen [MrTango] md@derico.de


Contributors
============

* Andreas Jung
* Dinu Gherman
* Jens W. Klein
* Peter Holzer
* Philip Bauer
* Thomas Massman [tmassmann]
* Timo Stollenwerk
