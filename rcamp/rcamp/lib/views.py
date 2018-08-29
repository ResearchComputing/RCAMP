from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

def index_view(request):
    if request.user.is_authenticated():
        return redirect('projects:project-list')

    context_instance = RequestContext(request)
    response = render_to_response('index.html', {}, context_instance=context_instance)
    return response
