from django.http import HttpResponseRedirect
from django.shortcuts import render

from todo.forms import TodoForm
from todo.models import Todo
from django.urls import reverse


def index(request):
    todos = Todo.objects.all()
    completed_count = todos.filter(is_completed=True).count()
    incomplete_count = todos.filter(is_completed=False).count()
    all_count = todos.count()
    
    context = {'todos': get_showing_todos(request, todos), 
               'completed_count':completed_count, 
               'incomplete_count':incomplete_count, 
               'all_count':all_count
               }
    return render(request, 'todo/index.html', context)

def get_showing_todos(request, todos):
    if request.GET and request.GET.get('filter'):
        if request.GET.get('filter') == 'complete':
            return todos.filter(is_completed=True)
        if request.GET.get('filter') == 'incomplete':
            return todos.filter(is_completed=False)
        
    return todos


def create_todo(request):
    form = TodoForm()
    context = {'form': form} 
    
    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        is_completed = request.POST.get("is_completed", False)
        todo = Todo()
        todo.title = title
        todo.description = description
        todo.is_completed = True if is_completed=='on' else False
        todo.save()
        
        return HttpResponseRedirect(reverse("todo", kwargs={'id':todo.pk}))
    
    return render(request, 'todo/create-todo.html', context)

def todo_detail(request, id):
    return render(request, 'todo/todo-detail.html', {})