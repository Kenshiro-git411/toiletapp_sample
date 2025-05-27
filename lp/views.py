from django.shortcuts import render

def display_lp(request):
    return render(request, 'lp/service_introduction.html')