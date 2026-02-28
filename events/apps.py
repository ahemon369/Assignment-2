from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        import events.signals
        from django.db.models.signals import m2m_changed, post_migrate
        from events.signals import send_rsvp_confirmation

        # Connect m2m signal after models are loaded
        from django.apps import apps

        def create_groups(sender, **kwargs):
            from django.contrib.auth.models import Group
            for group_name in ['Admin', 'Organizer', 'Participant']:
                Group.objects.get_or_create(name=group_name)

        post_migrate.connect(create_groups, sender=self)

        # Connect RSVP signal
        from events.models import Event
        m2m_changed.connect(send_rsvp_confirmation, sender=Event.rsvp_users.through)
