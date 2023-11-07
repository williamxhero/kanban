from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("pds/<str:str_args>", views.pds, name="pds"),
    path("pls/<int:pd_id>/<str:str_args>", views.pls, name="pls"),
    path("its/<int:pl_id>/<str:str_args>", views.its, name="its"),
    path("it/<int:it_id>", views.it, name="it"),
]