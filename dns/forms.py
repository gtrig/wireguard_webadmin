import re

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Fieldset, HTML, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import DNSFilterList
from .models import DNSSettings, StaticHost


class DNSSettingsForm(forms.ModelForm):
    class Meta:
        model = DNSSettings
        fields = ['dns_primary', 'dns_secondary']

    def __init__(self, *args, **kwargs):
        super(DNSSettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['dns_primary'].label = _('Primary DNS')
        self.fields['dns_secondary'].label = _('Secondary DNS')
        self.fields['dns_primary'].required = True
        back_label = _('Back')
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                _('Resolver Settings'),
                Div(
                    Field('dns_primary', css_class='form-control'),
                    Field('dns_secondary', css_class='form-control'),
                    css_class='col-md-6'
                ),
            ),
            FormActions(
                Submit('save', _('Save'), css_class='btn btn-primary'),
                HTML(f'<a class="btn btn-outline-primary" href="/dns/">{back_label}</a>'),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        dns_primary = cleaned_data.get('dns_primary')
        dns_secondary = cleaned_data.get('dns_secondary')
        if dns_secondary and not dns_primary:
            dns_primary = dns_secondary
            dns_secondary = ''
            cleaned_data['dns_primary'] = dns_primary
            cleaned_data['dns_secondary'] = dns_secondary
        if dns_primary and dns_primary == dns_secondary:
            raise ValidationError('Primary and secondary DNS cannot be the same')
        return


class StaticHostForm(forms.ModelForm):
    class Meta:
        model = StaticHost
        fields = ['hostname', 'ip_address', 'is_wildcard']

    def __init__(self, *args, **kwargs):
        super(StaticHostForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.fields['hostname'].label = _('Hostname')
        self.fields['ip_address'].label = _('IP Address')
        self.fields['is_wildcard'].label = _('Wildcard domain')
        self.fields['is_wildcard'].help_text = _(
            'Match this domain and all subdomains (e.g. example.com matches www.example.com, api.example.com, etc.)'
        )
        back_label = _('Back')
        delete_label = _('Delete')
        if self.instance.pk:
            delete_html = f"<a href='javascript:void(0)' class='btn btn-outline-danger' data-command='delete' onclick='openCommandDialog(this)'>{delete_label}</a>"
        else:
            delete_html = ''
        self.helper.layout = Layout(
            Fieldset(
                _('Static DNS'),
                Div(
                    Field('hostname', css_class='form-control'),
                    Field('ip_address', css_class='form-control'),
                    Field('is_wildcard', css_class='form-check-input'),
                    css_class='col-md-6'
                ),
            ),
            FormActions(
                Submit('save', _('Save'), css_class='btn btn-primary'),
                HTML(f'<a class="btn btn-outline-primary" href="/dns/">{back_label}</a> '),
                HTML(delete_html),
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        hostname = cleaned_data.get('hostname')
        is_wildcard = cleaned_data.get('is_wildcard', False)
        if hostname:
            # Normalize wildcard: store "example.com" even if user entered "*.example.com"
            if hostname.startswith('*.'):
                hostname = hostname[2:].strip()
                cleaned_data['hostname'] = hostname
                cleaned_data['is_wildcard'] = True
            if not hostname:
                raise ValidationError(_('Invalid hostname'))
            # Allow letters, digits, hyphens, dots; must start with letter or digit, end with letter or digit
            regex = r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$'
            if not re.match(regex, hostname):
                raise ValidationError(_('Invalid hostname'))
        return cleaned_data


class DNSFilterListForm(forms.ModelForm):
    class Meta:
        model = DNSFilterList
        # Only allow editable fields
        fields = ['name', 'description', 'list_url']

    def __init__(self, *args, **kwargs):
        super(DNSFilterListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        back_label = _('Back')
        delete_label = _('Delete')
        self.fields['name'].label = _('Name')
        self.fields['description'].label = _('Description')
        self.fields['list_url'].label = _('List URL')

        if self.instance.pk:
            delete_html = (
                "<a href='javascript:void(0)' class='btn btn-outline-danger' "
                f"data-command='delete' onclick='openCommandDialog(this)'>{delete_label}</a>"
            )
            self.fields['name'].widget.attrs['readonly'] = True
        else:
            delete_html = ''
        self.helper.layout = Layout(
            Fieldset(
                _('DNS Filter List Details'),
                Div(
                    Div(Field('name', css_class='form-control'), css_class='col-md-12'),
                    Div(Field('description', css_class='form-control'), css_class='col-md-12'),
                    Div(Field('list_url', css_class='form-control'), css_class='col-md-12'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('save', _('Save'), css_class='btn btn-primary'),
                HTML(f'<a class="btn btn-outline-primary" href="/dns/">{back_label}</a>'),
                HTML(delete_html),
            )
        )
