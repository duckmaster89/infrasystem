from django.shortcuts import render
from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

def custom_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorador personalizado que verifica si el usuario está autenticado.
    Si no lo está, muestra la página de acceso denegado.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=None,
        redirect_field_name=redirect_field_name
    )
    if function:
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return render(request, 'unauthorized.html')
            return function(request, *args, **kwargs)
        return wrapper
    return actual_decorator 