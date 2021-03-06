# -*- coding: utf-8 -*-
"""
Django site tools application default settings
===============================================

.. module:: sitetools.settings
    :platform: Django
    :synopsis: Django site tools application default settings
.. moduleauthor:: (C) 2014 Oliver Gutiérrez
"""

# Static sendfile backend
STATIC_SENDFILE_BACKEND = 'mod_xsendfile'

# Site under maintenance
SITE_UNDER_MAINTENANCE = False

# URLs that will not check maintenance mode
MAINTENANCE_URL_WHITELIST = ()

# URLs allowed to use HTTPS
ALLOWED_SECURE_URLS = (r'^/.*$',)

# URLs forced to use HTTPS
FORCED_SECURE_URLS = ()

# Use secure URLs in debug mode
SECURE_URLS_DEBUG = False

# Case sensitive URLs
CASE_SENSITIVE_URLS = ()

# Force legal documents acceptance by user
FORCE_LEGAL_ACCEPTANCE = False

# URLs that will not force legal documents acceptance (Admin site, logout, etc.)
FORCE_LEGAL_ACCEPTANCE_WHITELIST_URLS = ('/admin/','/accounts/logout/')

# Legal documents forced acceptance document
FORCED_LEGAL_DOCUMENT = None

# Legal documents forced acceptance document version
FORCED_LEGAL_DOCUMENT_VERSION = None

# Specify if previous versions of legal documents should be served if requested
SHOW_PREVIOUS_LEGAL_DOCUMENT_VERSIONS = False

# Site log level for mailing administrators
SITE_LOG_MAIL_ADMINS_LEVEL = 0

# Site template prefix
SITE_TEMPLATE_PREFIX='site_templates'

# Alert by email on new contact messages (Used in contact form view)
CONTACT_MESSAGE_MAIL_ALERT=True

# ReCAPTCHA keys
RECAPTCHA_PUB_KEY=None
RECAPTCHA_PRIV_KEY=None