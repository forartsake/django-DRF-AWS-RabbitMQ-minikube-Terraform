from django.http import HttpResponse



def index(request):
    return HttpResponse("<h1>Testing page</h1>")
