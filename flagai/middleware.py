from django.http import HttpResponseRedirect
from django.urls import reverse


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/login') and request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if request.path.startswith('/index') and {request.user.username: 'admin'}:
            return HttpResponseRedirect('/admin/')

        response = self.get_response(request)
        return response
