from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.groups.filter(name='Admin').exists() or request.user.is_superuser
        ):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    return wrapper


def organizer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Organizer').exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    return wrapper


def participant_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Participant').exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    return wrapper
