from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from .models import Event, Category
from .forms import SignUpForm, EventForm, CategoryForm, RoleChangeForm, GroupForm
from .decorators import admin_required, organizer_required


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            participant_group, _ = Group.objects.get_or_create(name='Participant')
            user.groups.add(participant_group)
            messages.success(request, "Check your email for activation link.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_superuser or user.groups.filter(name='Admin').exists():
                    return redirect('admin_dashboard')
                elif user.groups.filter(name='Organizer').exists():
                    return redirect('organizer_dashboard')
                elif user.groups.filter(name='Participant').exists():
                    return redirect('participant_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Your account is not activated. Check your email.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can now log in.")
        return render(request, 'activation/activation_success.html')
    else:
        return render(request, 'activation/activation_failed.html')


def home_view(request):
    events = Event.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'events': events})


def event_list(request):
    events = Event.objects.all().order_by('-created_at')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvped = False
    if request.user.is_authenticated:
        user_rsvped = event.rsvp_users.filter(pk=request.user.pk).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'user_rsvped': user_rsvped})


@login_required
def event_create(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to create events.")
        return redirect('home')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully.")
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to edit events.")
        return redirect('home')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Update'})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to delete events.")
        return redirect('home')
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('event_list')
    return render(request, 'events/event_delete.html', {'event': event})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to create categories.")
        return redirect('home')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'categories/category_form.html', {'form': form, 'action': 'Create'})


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to edit categories.")
        return redirect('home')
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'categories/category_form.html', {'form': form, 'action': 'Update'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "You don't have permission to delete categories.")
        return redirect('home')
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('category_list')
    return render(request, 'categories/category_delete.html', {'category': category})


@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user.groups.filter(name='Participant').exists():
        messages.error(request, "Only participants can RSVP to events.")
        return redirect('event_detail', pk=pk)
    if event.rsvp_users.filter(pk=request.user.pk).exists():
        messages.warning(request, "You have already RSVP'd to this event.")
    else:
        event.rsvp_users.add(request.user)
        messages.success(request, "You have successfully RSVP'd to this event!")
    return redirect('event_detail', pk=pk)


@login_required
def cancel_rsvp(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.rsvp_users.filter(pk=request.user.pk).exists():
        event.rsvp_users.remove(request.user)
        messages.success(request, "Your RSVP has been cancelled.")
    else:
        messages.warning(request, "You haven't RSVP'd to this event.")
    return redirect('event_detail', pk=pk)


@login_required
@admin_required
def admin_dashboard(request):
    events = Event.objects.all()
    participants = User.objects.filter(groups__name='Participant')
    categories = Category.objects.all()
    groups = Group.objects.all()
    return render(request, 'dashboard/admin_dashboard.html', {
        'events': events,
        'participants': participants,
        'categories': categories,
        'groups': groups,
    })


@login_required
def organizer_dashboard(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Admin').exists() or
            request.user.groups.filter(name='Organizer').exists()):
        messages.error(request, "Access denied.")
        return redirect('home')
    events = Event.objects.filter(created_by=request.user)
    categories = Category.objects.all()
    return render(request, 'dashboard/organizer_dashboard.html', {
        'events': events,
        'categories': categories,
    })


@login_required
def participant_dashboard(request):
    rsvped_events = request.user.rsvped_events.all()
    all_events = Event.objects.all()
    return render(request, 'dashboard/participant_dashboard.html', {
        'rsvped_events': rsvped_events,
        'all_events': all_events,
    })


@login_required
@admin_required
def manage_roles(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = RoleChangeForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            target_user.groups.clear()
            target_user.groups.add(group)
            messages.success(request, f"Role updated for {target_user.username}.")
            return redirect('admin_dashboard')
    else:
        form = RoleChangeForm()
    return render(request, 'dashboard/manage_roles.html', {'form': form, 'target_user': target_user})


@login_required
@admin_required
def delete_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        target_user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('admin_dashboard')
    return render(request, 'dashboard/admin_dashboard.html', {'confirm_delete_user': target_user})


@login_required
@admin_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            Group.objects.get_or_create(name=form.cleaned_data['name'])
            messages.success(request, "Group created successfully.")
            return redirect('admin_dashboard')
    else:
        form = GroupForm()
    return render(request, 'dashboard/create_group.html', {'form': form})


@login_required
@admin_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')
