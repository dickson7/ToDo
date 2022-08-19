from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('create-todo/', views.create_todo, name='create-todo'),
    path('todo-detail/<id>/', views.todo_detail, name='todo'),
    path('todo-delete/<id>/', views.todo_delete, name='todo-delete'),
    path('todo-edit/<id>/', views.todo_edit, name='todo-edit'),
]
