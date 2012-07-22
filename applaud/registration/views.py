"""
Views which allow users to create and activate accounts.
"""


from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.core.urlresolvers import reverse
import urllib2
from registration.backends import get_backend
import forms
from applaud import models as applaud_models
from applaud import settings
import json

import sys

@csrf_protect
def activate(request, backend,
             template_name='registration/activate.html',
             success_url=None, extra_context=None, **kwargs):
    """
    Activate a user's account.

    The actual activation of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    the backend's ``activate()`` method will be called, passing any
    keyword arguments captured from the URL, and will be assumed to
    return a ``User`` if activation was successful, or a value which
    evaluates to ``False`` in boolean context if not.

    Upon successful activation, the backend's
    ``post_activation_redirect()`` method will be called, passing the
    ``HttpRequest`` and the activated ``User`` to determine the URL to
    redirect the user to. To override this, pass the argument
    ``success_url`` (see below).

    On unsuccessful activation, will render the template
    ``registration/activate.html`` to display an error message; to
    override thise, pass the argument ``template_name`` (see below).

    **Arguments**

    ``backend``
        The dotted Python import path to the backend class to
        use. Required.

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context. Optional.

    ``success_url``
        The name of a URL pattern to redirect to on successful
        acivation. This is optional; if not specified, this will be
        obtained by calling the backend's
        ``post_activation_redirect()`` method.
    
    ``template_name``
        A custom template to use. This is optional; if not specified,
        this will default to ``registration/activate.html``.

    ``\*\*kwargs``
        Any keyword arguments captured from the URL, such as an
        activation key, which will be passed to the backend's
        ``activate()`` method.
    
    **Context:**
    
    The context will be populated from the keyword arguments captured
    in the URL, and any extra variables supplied in the
    ``extra_context`` argument (see above).
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    backend = get_backend(backend)
    account = backend.activate(request, **kwargs)

    if account:
        if success_url is None:
            to, args, kwargs = backend.post_activation_redirect(request, account)
            return redirect(to, *args, **kwargs)
        else:
            return redirect(success_url)

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              kwargs,
                              context_instance=context)

@csrf_protect
def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='registration/registration_form.html',
             extra_context=None, **kwargs):
    """
    Allow a new user to register an account.

    The actual registration of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    it will be used as follows:

    1. The backend's ``registration_allowed()`` method will be called,
       passing the ``HttpRequest``, to determine whether registration
       of an account is to be allowed; if not, a redirect is issued to
       the view corresponding to the named URL pattern
       ``registration_disallowed``. To override this, see the list of
       optional arguments for this view (below).

    2. The form to use for account registration will be obtained by
       calling the backend's ``get_form_class()`` method, passing the
       ``HttpRequest``. To override this, see the list of optional
       arguments for this view (below).

    3. If valid, the form's ``cleaned_data`` will be passed (as
       keyword arguments, and along with the ``HttpRequest``) to the
       backend's ``register()`` method, which should return the new
       ``User`` object.

    4. Upon successful registration, the backend's
       ``post_registration_redirect()`` method will be called, passing
       the ``HttpRequest`` and the new ``User``, to determine the URL
       to redirect the user to. To override this, see the list of
       optional arguments for this view (below).
    
    **Required arguments**
    
    None.
    
    **Optional arguments**

    ``backend``
        The dotted Python import path to the backend class to use.

    ``disallowed_url``
        URL to redirect to if registration is not permitted for the
        current ``HttpRequest``. Must be a value which can legally be
        passed to ``django.shortcuts.redirect``. If not supplied, this
        will be whatever URL corresponds to the named URL pattern
        ``registration_disallowed``.
    
    ``form_class``
        The form class to use for registration. If not supplied, this
        will be retrieved from the registration backend.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``success_url``
        URL to redirect to after successful registration. Must be a
        value which can legally be passed to
        ``django.shortcuts.redirect``. If not supplied, this will be
        retrieved from the registration backend.
        
    ``template_name``
        A custom template to use. If not supplied, this will default
        to ``registration/registration_form.html``.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    registration/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)


        if form.is_valid():
            new_user = backend.register(request, **form.cleaned_data)
            # django-registration does not take care of names. Do it here.
            new_user.first_name = request.POST['first_name']
            new_user.last_name = request.POST['last_name']
            new_user.save()
            
            # Each user (business, emp or enduser) has an inbox, associated with the User model
            inbox = applaud_models.Inbox(user=new_user)
            inbox.save()
            
            # Welcome message
            message = applaud_models.MessageItem(text="Welcome to the Apatapa family! We're happatapy to have you here",
                                                 date_created = datetime.utcnow().replace(tzinfo=utc),
                                                 inbox = inbox,
                                                 subject = 'Oh Hello!',
                                                 sender = User.objects.get(pk=1))
            message.save()

            # This section modified by Luke & Peter on Tue Jun 19 21:26:42 UTC 2012
            # This section modified again by Jack and Shahab on Thu June 21
            if 'profile_type' in kwargs:

                # We are registering a business
                if kwargs['profile_type'] is 'business':
                    profile = applaud_models.BusinessProfile(latitude=request.POST['latitude'],
                                                             longitude=request.POST['longitude'],
                                                             address=request.POST['address'],
                                                             phone=request.POST['phone'],
                                                             business_name=request.POST['business_name'],
                                                             user=new_user,
                                                             goog_id=request.POST['goog_id'],
                                                             first_time=True)

                    profile.save()

                    # Create a generic rating profile
                    rp = applaud_models.RatingProfile(title="Employee",
                                                      dimensions=['rating'],
                                                      business=profile)
                    rp.save()

                #We know that we're registering an employee
                elif kwargs['profile_type'] is 'employee':

                    #First, determine which business this employee works for
                    business_profile = applaud_models.BusinessProfile.objects.get(goog_id=kwargs['goog_id'])
                    # There is only one rating profile at this point.
                    rp = business_profile.ratingprofile_set.all()[0]
                    profile = applaud_models.EmployeeProfile(business = business_profile,
                                                             user=new_user,
                                                             rating_profile=rp,
                                                             first_time=True)
                    profile.save()


                # Registering an end-user
                elif kwargs['profile_type'] is 'user':

                    profile=applaud_models.UserProfile(user=new_user,
                                                       first_time=True)
                    profile.save()
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(request, new_user)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()
    
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():

        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              {'form': form},
                              # context
                              context_instance=RequestContext(request))

def register_business(request, backend, success_url=None, form_class=forms.BusinessRegistrationForm,
                      disallowed_url='registration_disallowed',
                      template_name='registration/business_registration_form.html',
                      extra_context=None):
    return register(request, backend, success_url, form_class, disallowed_url, template_name, profile_type='business')


def register_employee(request, backend, goog_id, success_url=None, form_class=forms.EmployeeRegistrationForm,
                      disallowed_url='registration_disallowed',
                      template_name='registration/employee_registration_form.html',
                      extra_context=None):
    return register(request, backend, success_url, form_class, disallowed_url, template_name, profile_type='employee', goog_id=goog_id)

def register_user(request, backend, success_url=None, form_class=forms.UserRegistrationForm,
                  disallowed_url='registration_disallowed',
                  template_name='registration/user_registration_form.html',
                  extra_context=None):
    return register(request, backend, success_url, form_class, disallowed_url, template_name, profile_type='user')

def mobile_login(request):
    if request.method == 'POST':
        user = auth.authenticate( username=request.POST['username'],
                                  password=request.POST['password'] )
        if user:
            auth.login( request, user )
            return HttpResponse(request.session.session_key)
        else:
            return HttpResponseForbidden("Bad login.")
    return HttpResponseBadRequest("Your shit dont make no sense.")

def profile(request):
    '''Redirect the user to the appropriate page after login.
    '''

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("auth_login"))
    
    profile = ""
    prefix = ""
    # Are we a business?
    try:
        profile = request.user.businessprofile
        prefix = "business"
    except applaud_models.BusinessProfile.DoesNotExist:
        # Are we an employee?
        try:
            profile = request.user.employeeprofile
            prefix = "employee"
        except applaud_models.EmployeeProfile.DoesNotExist:
            # Are we an end-user?
            try:
                profile = request.user.userprofile
                prefix = "user"
            except applaud_models.UserProfile.DoesNotExist:
                return HttpResponseRedirect("/")


    # sys.stderr.write('prefix is: %s' % prefix)
    if profile.first_time:
        profile.first_time = False
        profile.save()
        return HttpResponseRedirect("/%s/welcome/"%prefix)
    else:
        # /x/ should be the homepage for an entity (business, employee, etc.)
        # of type x
        return HttpResponseRedirect('/%s/'%prefix)
