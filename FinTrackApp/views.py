from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from rest_framework import status
from django.http import HttpResponse
class Home(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        # html_content = "<html><body><h1>Bienvenido</h1></body></html>"
        # # return Response('Bienvenido', status=status.HTTP_200_OK)
        # return Response(html_content, status=status.HTTP_200_OK, content_type="text/html")
    
        # html_content = "<html><body><h1>Bienvenido</h1></body></html>"
        html = render(request, 'home.html')
        return HttpResponse(html, status=status.HTTP_200_OK, content_type="text/html")
    

# Create your views here.
