from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("kanban/<str:input>", views.kanban, name="kanban")
]