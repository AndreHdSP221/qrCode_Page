from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.urls import reverse
from .models import ActionToken

def send_2fa_code_email(user, code):
    subject = f'Seu código de Verificação de Login: {code}'

    context = {
        'user': user,
        'code': code,
        'temp_expirar': 10,
    }

    html_message = render_to_string('accounts/emails/verify_2fa.html', context)

    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL

    list_desti = [user.email]

    send_mail(
        subject,
        plain_message,
        from_email,
        list_desti,
        html_message=html_message
    )
    
def send_action_email(request, user, action_type_enum):
    token_obj = ActionToken.objects.create(user=user , action_type=action_type_enum)

    """ Url da verificação """
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_action', kwargs={'token': token_obj.token})
    )

    context = {
        'user': user,
        'verification_url': verification_url,
        'action_type': token_obj.get_action_type_display()
    }

    html_message = render_to_string('accounts/emails/action_verification.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=f'Confirmação Necessária: {token_obj.get_action_type_display()}',
        message=plain_message,
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message
    )