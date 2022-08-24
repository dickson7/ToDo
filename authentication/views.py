import threading

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_str, smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from validate_email import validate_email

from helpers.decorators import auth_user_should_not_access

from .models import User
from .utils import generate_token

EMAIL_FROM_USER = settings.EMAIL_FROM_USER

class EmailThread(threading.Thread):
    
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_action_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('authentication/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })
    print(settings.EMAIL_FROM_USER)
    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=EMAIL_FROM_USER,
                         to=[user.email]
                         )

    # email.send()
    if not settings.TESTING:
        EmailThread(email).start()


@auth_user_should_not_access
def register(request):
    if request.method == "POST":
        context = {'has_error': False, 'data':request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if len(password)<8:
            messages.add_message(request, messages.ERROR, "Password should be at least 6 characters") 
            context['has_error'] = True
        if password != password2:
            messages.add_message(request, messages.ERROR, "Password mismatch") 
            context['has_error'] = True
        if not validate_email(email):
            messages.add_message(request, messages.ERROR, "Enter a valid email address") 
            context['has_error'] = True
        if not username:
            messages.add_message(request, messages.ERROR, "Username is requered") 
            context['has_error'] = True
        if User.objects.filter(username=username).exists() :
            messages.add_message(request, messages.ERROR, "Username is taken, choose another one") 
            context['has_error'] = True
            return render(request, 'authentication/register.html', context, status=409)
        if User.objects.filter(email=email).exists() :
            messages.add_message(request, messages.ERROR, "Email is taken, choose another one") 
            context['has_error'] = True
            return render(request, 'authentication/register.html', context, status=409)
        
        if context['has_error']:
            return render(request, 'authentication/register.html', context)
        
        user=User.objects.create_user(username=username,email=email)
        user.set_password(password)
        user.save()
        if not context['has_error']:
            send_action_email(user, request)
            messages.add_message(request, messages.SUCCESS, "Account created, you can now login") 
            return redirect('login')
        
    return render(request, 'authentication/register.html')


@auth_user_should_not_access
def login_user(request):
    if request.method == "POST":
        context = {"data": request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')

        user=authenticate(request, username=username, password=password)
        
        if user and not user.is_email_verified:
            messages.add_message(request, messages.ERROR, 
                                 "Email is not verificated, please check your email inbox")
            return render(request, 'authentication/login.html', context, status=401)
        
        if not user:
            messages.add_message(request, messages.ERROR, "Invalid credentials")
            return render(request, 'authentication/login.html', context, status=401)
        
        login(request, user)
        messages.add_message(request, messages.SUCCESS, f'Welcome {user.username}') 
        return redirect(reverse('home'))
        
    return render(request, 'authentication/login.html')

def logout_user(request):
    logout(request)

    messages.add_message(request, messages.SUCCESS,
                         'Successfully logged out')

    return redirect(reverse('login'))


def activate_user(request, uidb64, token):
    
    try:
        uid = smart_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('login'))

    return render(request, 'authentication/activate-failed.html', {"user": user})