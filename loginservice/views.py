from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render


# Create your views here.
def register_view(request):
    """
    Vista de registro de usuario.

    Flujo:
    1) Si la petición es POST se extraen los datos del formulario.
    2) Se obtiene el usario de settings.AUTH_USER_MODEL
    3) Validaciones:
        Si el email ya existe -> muestra el error y vuelve al formulario.
        Si el usuario existe -> muestra el error y vuelve al formulario.
    4) Crea el nuevo usuario.
    5)Redirige a home.html
    6)Si la petición no es POST -> renderiza el formulario de nuevo. 
    """

    if request.method == "POST":
        #Extrae los datos del formulario
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")


        #Obtiene CustomUser de settings.AUTH_USER_MODEL
        User = get_user_model()

        #Verifica si el email existe.
        if User.objects.filter(email=email).exists():
            messages.error(request, "El email ya está registrado.")
            return render(request, 'loginservice/register.html')

        #Verifica si el username existe.
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya está registrado.")
            return render(request, 'loginservice/register.html')


        #Si pasa las validaciones, crea el nuevo usuario
        User.objects.create_user(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
            phone_number = phone_number
        )

        #Una vez creado el usuario, lo redirige a home.
        return redirect('loginservice:home')

    #SI el metodo no es POST, renderiza el FORM
    else:

        return render(request, 'loginservice/register.html')


def login_view(request):
    """
    Vista de login de usuario.

    Flujo:
    1) Si la petición es POST se extraen los datos del form.
    2) Validaciones:
        Si no hay username -> muestra error y renderiza form.
        Si no hay password -> muestra error y renderiza form.
    3) Se obtiene el modelo de settings.AUTH_USER_MODEL
    4) Validacion:
        Si la contraseña coincide -> redirige a home
        Si no -> muestra error y renderiza form
    5) Si no es POST -> renderiza el form.
    """
    if request.method == "POST":
        #Extrae los datos del form
        username = request.POST.get("username")
        password = request.POST.get("password")

        #Valida los datos del formulario
        if not username:
            messages.error(request, "Debe ingresar su usuario.")
            return render(request, 'loginservice/login.html')

        if not password:
            messages.error(request, "Debe ingresar su contraseña.")
            return render(request, 'loginservice/login.html')

        #Obtiene el modelo settings.AUTH_USER_MODEL. Lo busca y obtiene el usuario.
        User = get_user_model()
        user = User.objects.get(username=username)

        #Valida el password
        if user.check_password(password):
            return redirect('loginservice:home')
        else:
            messages.error(request, 'La contraseña no coincide.')
            return render(request, 'loginservice/login.html')

    #Si no es POST, renderiza el form
    else:
        return render(request, 'loginservice/login.html')
        

def home(request):
    return render(request, 'loginservice/home.html')

