from django.shortcuts import render

def home_page(request):
    return render(request, 'home/home.html')
def about(request):
    return render(request, 'about.html')