#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Site tools form widgets module
===============================================

.. module:: sitetools.forms.widgets
    :platform: Django
    :synopsis: Site tools form widgets module
.. moduleauthor:: (C) 2014 Oliver Gutiérrez
"""

# Python imports
import uuid
import json
import warnings

# Django imports
from django import forms
from django.utils.translation import ugettext
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

class RECAPTCHAWidget(forms.widgets.Input):
    """
    reCAPTCHA field widget
    """
    def __init__(self, api_server, pubkey, lang='en', theme='red', *args, **kwargs):
        """
        Initialization method
        """
        self.lang = lang
        self.theme = theme
        self.pubkey = pubkey
        self.api_server = api_server
        super(RECAPTCHAWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        """
        Render method overload
        """
        return mark_safe(u"""
        <script type="text/javascript">var RecaptchaOptions = {theme : '%s',lang: '%s'};</script>
        <script type="text/javascript" src="%s/challenge?k=%s"></script>
        <noscript>
           <iframe src="%s/noscript?k=%s" width="500" height="300"></iframe>
           <br />
           <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
           <input type="hidden" name="recaptcha_response_field" value="manual_challenge">
        </noscript>
        <input id="%s" type="text" name="recaptcha_django_field" value="" style="display: none;">
        """ % (self.theme, self.lang, self.api_server, self.pubkey, self.api_server, self.pubkey, attrs['id']))

    def value_from_datadict(self, data, files, name):
        """
        Obtaining data from form submission
        """
        return (data.get('recaptcha_challenge_field', None), data.get('recaptcha_response_field', None))

class TinyMCEWidget(forms.Textarea):
    """
    TinyMCE HTML editor widget
    """
    class Media:
        """
        Media class
        """
        extend = False
        js = ('//tinymce.cachefly.net/4.0/tinymce.min.js',)

    def __init__(self, attrs=None):
        final_attrs = {
            'class': 'tinymce',
            'style': 'display: inline-block;'
        }
        if attrs is not None:
            final_attrs.update(attrs)
        super(TinyMCEWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None):
        output = super(TinyMCEWidget, self).render(name, value, attrs)
        # TODO: Add language option (current cdn does not have language files)
        return mark_safe(output + "\n<script>tinymce.init({selector: '#%s', menubar:false, statusbar: true, plugins: 'code fullscreen', toolbar: 'undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | code fullscreen' });</script>"  % attrs['id'])


class AceEditorWidget(forms.Textarea):
    """
    Ace code editor widget

    FIXME: Browser got locked with Ace initialization
    """
    class Media:
        """
        Media class
        """
        extend = False
        js = ('//cdnjs.cloudflare.com/ajax/libs/ace/1.1.3/ace.js',)

    def __init__(self, attrs=None):
        warnings.warn('Using AceEditorWidget will probably lock your browser.')
        final_attrs = {'class': 'aceeditor'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AceEditorWidget, self).__init__(attrs=final_attrs)

    def render(self, name, value, attrs=None):
        output = super(AceEditorWidget, self).render(name, value, attrs)
        return mark_safe(output + "<script>var editor = ace.edit('%s');</script></div>" % attrs['id'])


class VectorWidget(forms.MultiWidget):
    """
    N dimensional float vector widget
    """

    def __init__(self, attrs={}):
        """
        Initialization method
        """
        self.dimensions = attrs['dimensions']
        widgets = [forms.NumberInput for i in range(self.dimensions)]
        attrs.setdefault('step', 'any')
        super(VectorWidget, self).__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        """
        Decompress value
        """
        if value and isinstance(value, (list, tuple)):
            return [value[i] for i in range(self.dimensions)]
        return [None for i in range(self.dimensions)]


class LocationWidget(forms.MultiWidget):
    """
    Location widget

    Picker: http://api.mygeoposition.com/geopicker/
    """
    class Media:
        """
        Widget media class
        """
        js = (
            'http://api.mygeoposition.com/api/geopicker/api.js',
        )

    def __init__(self, attrs={}):
        """
        Initialization method
        """
        widgets = [forms.NumberInput, forms.NumberInput]
        attrs.setdefault('step', 'any')
        super(LocationWidget, self).__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value):
        """
        Decompress value
        """
        if value and isinstance(value, dict):
            return [value.get('lat', None), value.get('lon', None)]
        return [None, None]

    def render(self, name, value, attrs=None):
        HTML = """
            <script type="text/javascript">
                function fn%s_location_popup() {            
                    myGeoPositionGeoPicker({
                        startPositionLat : '%s',
                        startPositionLng : '%s',
                        zoomLevel: 10,
                        returnFieldMap   : {
                                             'id_%s_0' : '<LAT>',
                                             'id_%s_1' : '<LNG>',
                                           }
                    });
                }
            </script>
            <input id="id_%s_0" name="%s_0" step="any" type="number" value="%s">
            <input id="id_%s_1" name="%s_1" step="any" type="number" value="%s">
            <button type="button" onclick="fn%s_location_popup();">&gt;</button>
        """
        try:
            if not isinstance(value, dict):
                value = json.loads(value)
            lat = value['lat']
            lon = value['lon']
        except:
            lat = ''
            lon = ''
        uniqueid = str(uuid.uuid4()).replace('-', '')
        return mark_safe(HTML % (uniqueid, lat, lon, name, name, name, name, lat, name, name, lon, uniqueid))
