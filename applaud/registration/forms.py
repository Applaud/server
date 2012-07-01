"""
Forms and validation code for user registration.

"""


from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from applaud.models import EmployeeProfile, BusinessProfile, UserProfile
from PIL import Image

import sys

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"))
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.
    
    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which disallows registration with
    email addresses from popular free webmail services; moderately
    useful for preventing automated spam registrations.
    
    To change the list of banned domains, subclass this form and
    override the attribute ``bad_domains``.
    
    """
    bad_domains = ['trashmail.com', 'mailinator.com']
    
    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.
        
        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(_("Registration using temporary email addresses is prohibited. Please supply a different email address."))
        return self.cleaned_data['email']


class BusinessRegistrationForm(RegistrationForm):
    phone = forms.RegexField(regex=r'^\d?[ -.]?\d{3}[ -.]?\d{3}[ -.]?\d{4}',
                             widget=forms.TextInput(attrs=attrs_dict),
                             error_messages={'invalid':"Please enter a valid phone number, including the area code."})
    latitude = forms.FloatField(widget=forms.HiddenInput)
    longitude = forms.FloatField(widget=forms.HiddenInput)
    address = forms.CharField(max_length=500, widget=forms.HiddenInput)
    goog_id = forms.CharField(max_length=1000, widget=forms.HiddenInput)

    business_name = forms.CharField(max_length=500, label="Business Name")

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = BusinessProfile

class EmployeeRegistrationForm(RegistrationForm):	
    
    username = forms.CharField(max_length=100,label="Username")
    #Eventually we should use a password field, for now an employee will just select the business by name
    #business_password = forms.CharField(max_length=100, widget=forms.PasswordInput, label="Business Password")

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

class EmployeeProfileForm(forms.ModelForm):
    # Maximum image size = 1Mb
    max_image_size = 1048576
    # Acceptable file formats
    image_formats = ('JPEG','JPG','BMP','PNG','GIF','image')

    def clean_profile_picture(self):
        image = self.cleaned_data['profile_picture']

        if image:
            print image.name
            image_format = image.content_type.split('/')[0]

            if len(image.name.split('.')) == 1:
                raise forms.ValidationError(_('File type unsupported.'))

            if image_format in self.image_formats:
                if image.size > self.max_image_size:
                    raise forms.ValidationError("Image size must be under 1Mb.")
            else:
                raise forms.ValidationError(_('File type unsupported.'))

        return image

    class Meta:
        model = EmployeeProfile
        fields = ('bio','profile_picture',)


class UserRegistrationForm(RegistrationForm):
    # The RegistrationForm (at the top of this page) only has the username, email and password.
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    
    class Meta:
        model = UserProfile
