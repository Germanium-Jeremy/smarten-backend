from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def main_view(request):
    content = {
        'message': 'Welcome to the Smarten API',
    }
    return render(request, 'main/index.html', content)