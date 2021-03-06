# -*- coding: utf-8 -*-
"""
 Site tools views module
===============================================

.. module:: sitetools.views
    :platform: Django
    :synopsis: Site tools views module
.. moduleauthor:: (C) 2014 Oliver Gutiérrez
"""

# Python imports
import os

# Django imports
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext,ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.http import last_modified
from django.views.decorators.csrf import ensure_csrf_cookie

# Application imports
from sitetools.http import JSONResponse
from sitetools.utils import get_client_ip,get_site_from_request,static_serve,last_file_modification_date,generate_expiration_date
from sitetools.forms.forms import ContactForm
from sitetools.models import SiteLog, LegalDocument, LegalDocumentAcceptance

def close_cookies_alert(req):
    """
    Close cookies alert and avoid it to appear again
    """
    req.session['acceptcookies']=True
    if req.is_ajax():
        return JSONResponse({})
    else:
        return HttpResponse()

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
    return HttpResponse(data,content_type='text/plain')

def favicon(request,iconfile='favicon.ico',options={}):
    """
    Favicon view
    """
    # Return icon
    return static_serve('%s/%s' % (settings.STATIC_ROOT,iconfile))

@last_modified(last_file_modification_date)
def static_serve_view(request,path,root=settings.STATIC_ROOT):
    """
    Static serving
    """
    return static_serve(os.path.join(root,path), extra_headers={'Expires': generate_expiration_date()})

def legal_document_view(request,docid=None,version=None, template_name='legal/document_view.html'):
    """
    View for legal documents
    """
    # Get document
    document=LegalDocument.get_document_version(docid,version)
    if document is None:
        raise Http404(ugettext('No legal document matching given parameters'))
    # Check if we can show previous versions of the document
    if not settings.SHOW_PREVIOUS_LEGAL_DOCUMENT_VERSIONS and document.document.get_latest() != document:
        return redirect(reverse('legal_document_latest',args=[docid]))
    ctx={
        'document': document,
        'legalpage': True
    }
    return TemplateResponse(request, template_name, ctx)

@login_required
def legal_document_acceptance(request,docid=None,version=None,template_name='legal/document_acceptance.html'):
    """
    View for legal documents acceptance
    """
    # Get document
    document=LegalDocument.get_document_version(docid,version)
    if document is None:
        raise Http404(ugettext('No legal document matching given parameters'))

    # Get next URL
    next=request.GET.get('next',None)
    accepted=request.GET.get('accept',False)
    if accepted:
        # Mark document as accepted
        ip=get_client_ip(request)
        LegalDocumentAcceptance(documentversion=document,user=request.user,ip=ip).save()
        if next is not None:
            return redirect(next)
        else:
            return redirect(reverse('profile'))
    ctx={
        'document': document,
        'next': next,
    }
    return TemplateResponse(request, template_name, ctx)

@ensure_csrf_cookie
def contact_form_view(request,contact_form_template_name='sitetools/contact_form.html',legal_document_name=None,
                    alert_by_mail=settings.CONTACT_MESSAGE_MAIL_ALERT,log_callback=None):
    """
    Contact form view
    """
    if request.method == 'POST':
        # A form bound to the POST data
        form = ContactForm(request.POST)
        if form.is_valid():
            # All validation rules pass. Process the data in form.cleaned_data
            ip=get_client_ip(request)
            form.instance.ip=ip
            form.save()
            # Save legal document acceptance
            if legal_document_name:
                user=None
                if request.user.is_authenticated():
                    user=request.user
                # Add legal document acceptance
                LegalDocumentAcceptance(documentversion=LegalDocument.get_document_version('avisolegal'),user=user,ip=ip,desc=_('Contact form'),data=form.instance.email).save()
            # Save log entry
            SiteLog.log('contact_form',_('New contact message from %(name)s %(email)s') % {'name': form.instance.name, 'email': form.instance.email},
                    data={'messageid': form.instance.id, 'name': form.instance.name, 'email': form.instance.email, 'text': form.instance.text },
                    content_object=form.instance,request=request,mail_admins=alert_by_mail,callback=log_callback)
            # Redirect after post
            return redirect(reverse('contact_form_done'))
    else:
        # An unbound form
        form = ContactForm()
    ctx={
        'form': form,
    }
    # Render page and return   
    return TemplateResponse(request,contact_form_template_name,ctx)

def contact_form_done_view(request, template_name='sitetools/contact_form_done.html'):
    """
    Contact form done view
    """
    return TemplateResponse(request, template_name)