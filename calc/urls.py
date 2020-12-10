from django.urls import path 
from . import views
# from django.conf.urls import  url
# from django.views.decorators.csrf import csrf_exempt
from . import views 

urlpatterns = [
    # path('',)
    # url(r'^object/$', csrf_exempt(views.ObjectView.as_view())),
    path('',views.home,name="home"),
    path('upload',views.upload,name="upload")

]
