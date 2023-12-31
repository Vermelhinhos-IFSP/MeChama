from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from MeChama import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "autenticacao/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        identificador = request.POST['identificador']
        email = request.POST['email']
        telefone = request.POST['telefone']
        cep = request.POST['cep']
        uf = request.POST['uf']
        cidade = request.POST['cidade']
        bairro = request.POST['bairro']
        logradouro = request.POST['logradouro']
        numero = request.POST['numero']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Nome de usuário existente. Por favor, tente outro.")
            return redirect('home')
        
        #if User.objects.filter(email=email).exists():
           # messages.error(request, "Email já registrado!")
            #return redirect('home')
        
        if len(username)>20:
            messages.error(request, "O nome de usuário precisa ter menos de 21 caracteres")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "As senhas não correspondem!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "O nome de usuário precisa ser alpha numérico")
            return redirect('home')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.pass_2 = pass2
        myuser.identificador_ = identificador
        myuser.telefone_ = telefone
        myuser.cep_ = cep
        myuser.uf_ = uf
        myuser.cidade = cidade
        myuser.bairro_ = bairro
        myuser.logradouro_ = logradouro
        myuser.numero = numero
       # myuser.is_active = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Sua conta foi criada com sucesso!! Por favor, confira o seu e-mail para ativar a sua conta.")

        # Welcome Email

        subject = "Seja bem-vindo ao MeChama!"
        message = "Olá, " + myuser.first_name + ". \n" + "Bem vindo ao MeChama! \nObrigado por visitar o nosso site. Esperamos que você tenha uma boa experiência! \n Nós também enviamos um email de confirmação. Por favor, confirme o seu endereço de email para ativar a sua conta. \n Obrigada, \n Vermelhinhos" 
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Email Address Confirmation Email
        
        current_site = get_current_site(request)
        email_subject = "Confirme o seu email - @ MeChama - Vermelhinhos"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()


    return render(request, "autenticacao/signup.html")

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "A sua conta foi ativada com sucesso!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "autenticacao/index.html",{"fname":fname})
        else:
            messages.error(request, "Usuário inexistente. Se cadastra aí, tmj")
            return redirect('home')
    
    return render(request, "autenticacao/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Deslogou com sucesso")
    return redirect('home')