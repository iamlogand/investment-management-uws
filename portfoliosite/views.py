from django.http import HttpResponseNotFound


def custom_404(request):
    return HttpResponseNotFound()