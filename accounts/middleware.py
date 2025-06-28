from django.shortcuts import redirect
from django.urls import reverse

class TwoFactorAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        if 'pre_2fa_user_id' in request.session:
            allowed_paths = [
                reverse('accounts:verify_2fa'), 
                reverse('accounts:logout')
            ]
            if request.path not in allowed_paths:
                return redirect('accounts:verify_2fa')

        return self.get_response(request)
