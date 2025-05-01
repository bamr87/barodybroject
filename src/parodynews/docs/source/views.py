from django.http import HttpResponse

"""
This module contains the views for the parodynews app.
"""

def example_view(request):
    """
    An example view function.

    :param request: The HTTP request object.
    :return: An HTTP response object.
    """
    return HttpResponse("Hello, world!")