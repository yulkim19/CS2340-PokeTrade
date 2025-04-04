from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the collections index.")


def about(request):
    return HttpResponse("Welcome to the About Page")
