from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('qrcode:gerar_zip_qrcodes')
        else:
            messages.error(request, 'As credenciais fornecidas estão incorretas. Por favor, verifique nome de usuário e senha e tente novamente.')
            return redirect('account:login')
    else:
        context_render = {}
        return render(request, 'accounts/login/loginpage.html', context_render)
