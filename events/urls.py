from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/update/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/<int:pk>/cancel-rsvp/', views.cancel_rsvp, name='cancel_rsvp'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),

    # Admin management
    path('dashboard/manage-roles/<int:user_id>/', views.manage_roles, name='manage_roles'),
    path('dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/create-group/', views.create_group, name='create_group'),
    path('dashboard/delete-group/<int:group_id>/', views.delete_group, name='delete_group'),
]
