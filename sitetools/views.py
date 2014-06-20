# -*- coding: utf-8 -*-
"""
 Site tools views module
===============================================

.. module:: sitetools.views
    :platform: Django
    :synopsis: Site tools views module
.. moduleauthor:: (C) 2014 Oliver Gutiérrez
"""

# Django imports
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.conf import settings

# Application imports
from sitetools.utils import get_client_ip,get_site_from_request
from sitetools.models import LegalDocument, LegalDocumentAcceptance

def service_unavailable(request,template_name='503.html'):
    """
    Default service unavailable view
    """
    return TemplateResponse(request,template_name,status=503)

def robots(request,template_name='robots.txt',options={}):
    """
    Robots view
    """
    # Global robots
    try:
        data=render_to_string(template_name,options)
    except IOError:
        data=''
    # Per site robots
    try:
        site=request.site
    except:
        # Get current site
        site = get_site_from_request(request)
    try:
        data+=site.siteinfo.robots
    except:
        pass
    # Return robots.txt contents
    return HttpResponse(data,mimetype='text/plain')

def legal_document_view(req,docid=None,version=None, template_name='legal/document_view.html'):
    """
    View for legal documents acceptance
    """
    # Get document
    document=LegalDocument.get_document_version(docid,version)
    if document is None:
        raise Http404(ugettext('No legal document matching given parameters'))
    # Check if we can show previous versions of the document
    if not settings.SHOW_PREVIOUS_LEGAL_DOCUMENT_VERSIONS and document.document.get_latest() != document:
        return redirect(reverse('legals_document_latest',args=[docid]))
    ctx={
        'document': document,
        'legalpage': True
    }
    return TemplateResponse(req, template_name, ctx)

@login_required
def legal_document_acceptance(req,docid=None,version=None,template_name='legal/document_acceptance.html'):
    """
    View for legal documents acceptance
    """
    # Get document
    document=LegalDocument.get_document_version(docid,version)
    if document is None:
        raise Http404(ugettext('No legal document matching given parameters'))

    # Get next URL
    next=req.GET.get('next',None)
    accepted=req.GET.get('accept',False)
    if accepted:
        # Mark document as accepted
        ip=get_client_ip(req)
        LegalDocumentAcceptance(documentversion=document,user=req.user,ip=ip).save()
        if next is not None:
            return redirect(next)
        else:
            return redirect(reverse('profile'))
    ctx={
        'document': document,
        'next': next,
    }
    return TemplateResponse(req, template_name, ctx)
