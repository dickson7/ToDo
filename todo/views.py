from django.shortcuts import render


def index(request):
    return render(request, 'todo/index.html')

def create_todo(request):
    return render(request, 'todo/create-todo.html')
