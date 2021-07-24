================
django3-robokassa
================

*fork of https://github.com/kmike for Django 3+*

Official documentation ROBOKASSA: http://docs.robokassa.ru

INSTALL
=========

::

    $ pip install git+git://github.com/EugeneFadeev/django3-robokassa@master

Then add 'robokassa' to INSTALLED_APPS and execute ::

    $ python manage.py migrate

Setup
=========

settings.py:

* ROBOKASSA_LOGIN
* ROBOKASSA_PASSWORD1

Optional parameters:

* ROBOKASSA_PASSWORD2 - пароль №2. It can be omitted if django-robokassa is used 
  only for displaying a payment form. If django-robokassa is used to accept payments, 
  then this parameter is required.

* ROBOKASSA_USE_POST - whether the POST method is used when receiving results 
  from ROBOKASSA. The default is True.

* ROBOKASSA_STRICT_CHECK - whether to use strict validation 
  (require prior notice on ResultURL). The default is True.

* ROBOKASSA_TEST_MODE - whether test mode is enabled. The default is False 
  (i.e. combat mode is enabled).

* ROBOKASSA_EXTRA_PARAMS - a list of names of additional parameters that will be 
  passed along with requests. "Shp" does not need to be assigned to them.

* ROBOKASSA_TEST_FORM_TARGET - url of the checkout counter for the test mode. 
  The setting is intended for the case when there is no domain available on 
  the Internet (for example, development on localhost) and instead of the 
  robobox server, you need to use your own.
