from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import redirect


def handler404(request, exception=None):
    return render(request, '404.html', {}, status=404)


def handler500(request):
    return render(request, '500.html', {}, status=500)

def index_view(request):
    if request.user.is_authenticated():
        return redirect('projects:project-list')

    return render(request, 'index.html', {})
