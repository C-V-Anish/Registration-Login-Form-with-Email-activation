from email.message import EmailMessage
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from LoginSys import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string
from .tokens import generate_token
# Create your views here.
def index(request):
    return render(request,'index.html')
    

def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']


        if User.objects.filter(username=username):
            messages.error(request,"Username already exists.Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"E-Mail already in use.Please use another e-mail")
            return redirect('home')

        if not username.isalnum():
            messages.error('Username must contain only letters and numbers.')
            return redirect('home')

        if pass1 != pass2:
            messages.error(request,"Passwords don't match!! Please enter correct password")
            return redirect('home')

        if len(username)>15:
            messages.error(request,"Username too big!! Please use a shorter one")
            return redirect('home')


        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.is_active=False
        myuser.save()

        messages.success(request,"You have successfully created your account")

        #Welcome Mail
        subject="Demo E-Mail "
        message="This is a demo mail sent to " + myuser.first_name + ".\n This mail doesnt support any replies.\n\n"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)
        

        #Confirmation Mail

        current_site = get_current_site(request)
        subject1 = "Confirm your mail-Django Login System"
        message1 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email = EmailMessage(subject1,message1,settings.EMAIL_HOST_USER,[myuser.email])
        email.fail_silently=True
        email.send()
        return redirect('signin')
    return render(request,'signup.html')

def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['pass']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,'index.html',{'fname':fname})
        else:
            messages.error(request,"Bad Credentials")
            return redirect('home')
    return render(request,'signin.html')


def signout(request):
    logout(request)
    messages.success(request,"You have been successfully logged out!!")
    return redirect('home')

