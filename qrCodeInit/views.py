from django.shortcuts import render

# Create your views here.
def qrCode_Home(request):
    return render(request, 'qrcodetpl/pages/home.html')