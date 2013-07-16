# encoding: utf8
from django.http import HttpResponseRedirect

from django.template.response import TemplateResponse

from django.utils.http import is_safe_url

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.forms import AuthenticationForm

@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    
    error_text = ""
    
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
                
            user = form.get_user()
            
            if not user.mo:
                error_text = 'Вы не можете войти, т.к. у Вас не установлена медицинская организация' 

            else:
                # Okay, security check complete. Log the user in.
                auth_login(request, user)

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)
        user = request.user
        if user.is_authenticated() and not user.mo: # TODO: need refactoring!!
            error_text = 'Вы не можете войти, т.к. у Вас не установлена медицинская организация' 

    request.session.set_test_cookie()


    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'error': error_text
    }
    
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

