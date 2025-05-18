from django.shortcuts import render


def landing_1(request):
    return render(request, 'accounts/landing_1.html')


def landing_2(request):
    return render(request, 'accounts/landing_2.html')
