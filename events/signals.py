from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_link = f"http://localhost:8000/activate/{uid}/{token}/"
        subject = "Activate Your Account"
        message = render_to_string('activation/activation_email.html', {
            'user': instance,
            'activation_link': activation_link,
        })
        send_mail(subject, message, 'noreply@eventmanagement.com', [instance.email])


def send_rsvp_confirmation(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and pk_set:
        for user_pk in pk_set:
            try:
                user = User.objects.get(pk=user_pk)
                subject = f"RSVP Confirmation: {instance.title}"
                message = (
                    f"You have successfully RSVP'd to {instance.title} "
                    f"on {instance.date} at {instance.location}."
                )
                send_mail(subject, message, 'noreply@eventmanagement.com', [user.email])
            except User.DoesNotExist:
                pass
