from django.urls import include, path

urlpatterns = [path('api/ussd/', include('apps.ussd.urls'))]
