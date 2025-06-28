from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .forms import Verify2FACodeForm, CreateNewAccountForm
from .models import ActionToken, LoginCode
from .utils import send_2fa_code_email, send_action_email

def create_a_account_view(request):
    if request.method == 'POST':
        form = CreateNewAccountForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_action_email(
                request, 
                user, 
                ActionToken.ActionTypes.ACCOUNT_ACTIVATION
            )
            
            messages.success(request, 'Conta criada com sucesso! Por favor, verifique seu e-mail para ativar sua conta e poder fazer o login.')

            return redirect('accounts:login')
    else:
        form = CreateNewAccountForm()
    
    context = {
        'form': form
    }
    return render(request, 'accounts/creataccount/creataccount.html', context)

def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta com sucesso.")
    return redirect('accounts:login')

def verify_2fa_view(request):
    try:
        user_id = request.session["pre_2fa_user_id"]
    except KeyError:
        return redirect('accounts:login')
    
    user = get_object_or_404(get_user_model(), id=user_id)

    if request.method == 'POST':
        form = Verify2FACodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            empty_limit = timezone.now() - timedelta(minutes=10)
            
            val_cod = LoginCode.objects.filter(
                user=user,
                code=code,
                is_used=False,
                created_at__gte=empty_limit

            ).first()
            
            if val_cod:
                val_cod.is_used = True
                val_cod.save()

                login(request, user)

                del request.session['pre_2fa_user_id']
                return redirect('qrCodeInit:gerar_zip_qrcodes') 
            else:
                messages.error(request, "Código inválido ou expirado.")
    else:
        form = Verify2FACodeForm()

    context = {
        "form": form
    }

    return render(request, 'accounts/dj_verify_2fa_page.html', context)

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login_code = LoginCode.objects.create(user=user)

            send_2fa_code_email(user, login_code.code)

            print(f'DEBUG: O código de 2FA para {user.username} é {login_code.code}')
            request.session['pre_2fa_user_id'] = user.id

            return redirect('accounts:verify_2fa')
        else:
            messages.error(request, "Nome de usuário ou senha inválidos. Por favor tente novamente.")
    else:
        form = AuthenticationForm()

    context = {
        "form": form
    }

    return render(request, "accounts/login/loginpage.html", context)

def verify_action(request, token):
    token_obj = get_object_or_404(ActionToken, token=token)

    if token_obj.is_used:
        messages.error(request, "Este link já foi utilizado e não é mais válido.")
        return redirect("accounts:login")
    
    if token_obj.is_expired():
        messages.error(request, "Este link de verificação expirou. Por favor, solicite um novo.")
        return redirect("accounts:login")
    
    user = token_obj.user
    action = token_obj.action_type
    
    if action == ActionToken.ActionTypes.ACCOUNT_ACTIVATION:
        user.is_active = True
        user.save()

        login(request, user)

        messages.success(request, "Sua conta foi ativada com sucesso! Bem-vindo(a)!")
    
    elif action == ActionToken.ActionTypes.ACCOUNT_DELETION:
        user.delete()
        messages.success(request, "Sua conta foi excluida permanentemente. Sentiremos sua falta!")

    token_obj.is_used = True
    token_obj.save()

    return redirect("accounts:login")