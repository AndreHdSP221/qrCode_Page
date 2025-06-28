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
    }

    html_message = render_to_string(
        'accounts/emails/dj_verify_2fa.html', 
        context=context
    )

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

# Em Desenvolvimento
def send_action_email(request, user, action_type_enum):
    print("\n--- INÍCIO DO DIAGNÓSTICO: send_action_email ---")

    try:
        # PASSO 1: Criação dos objetos e do contexto
        token_obj = ActionToken.objects.create(user=user, action_type=action_type_enum)
        verification_url = request.build_absolute_uri(
            reverse('accounts:verify_action', kwargs={'token': token_obj.token})
        )
        context = {
            'user': user,
            'verification_url': verification_url,
            'action_type': token_obj.get_action_type_display()
        }
        print(f"[ETAPA 1 SUCESSO] Contexto criado: {context}")
        print(f"--> Usuário: {context['user'].username}, Ação: {context['action_type']}")

        # PASSO 2: Verificação do arquivo de template
        template_path = 'accounts/emails/dj_action_verification.html'
        print(f"[ETAPA 2 PENDENTE] Tentando renderizar o template: {template_path}")

        # PASSO 3: O TESTE CRÍTICO DE RENDERIZAÇÃO
        html_message = render_to_string(template_path, context=context)
        
        print("[ETAPA 3 SUCESSO] render_to_string executado. Analisando o resultado...")
        
        # Vamos verificar se as variáveis foram substituídas
        if '{{' in html_message and '}}' in html_message:
            print("\n[FALHA NO DIAGNÓSTICO] O HTML renderizado AINDA contém variáveis de template {{...}}!\n")
        else:
            print("\n[SUCESSO NO DIAGNÓSTICO] O HTML foi renderizado corretamente! As variáveis foram substituídas.\n")

        # Imprime uma amostra do HTML final para inspeção visual
        print("--- Amostra da Mensagem HTML Processada ---")
        print(html_message[:500] + "...") # Imprime os primeiros 500 caracteres
        print("-------------------------------------------\n")

        # PASSO 4: Criação da versão em texto puro
        plain_message = strip_tags(html_message)
        print("[ETAPA 4 SUCESSO] strip_tags executado.")
        
        # PASSO 5: Envio (comentado para o teste)
        print("[ETAPA 5 PENDENTE] A chamada send_mail() está desativada para este teste.")
        # send_mail(...) # Mantenha esta linha comentada durante o teste.

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Uma exceção ocorreu durante o processo: {e}\n")

    print("--- FIM DO DIAGNÓSTICO ---\n")
