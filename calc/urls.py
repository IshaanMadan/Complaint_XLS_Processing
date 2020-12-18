from django.urls import path 
from . import views
# from django.conf.urls import  url
# from django.views.decorators.csrf import csrf_exempt
from . import views 

urlpatterns = [
    path('upload',views.upload,name="upload"),
    # path('',views.home,name="upload")



]
