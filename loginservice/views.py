from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render


# Create your views here.
def auth_view(request):
    """
    Vista combinada de login y registro de usuario.

    Flujo:
    1) Si la petición es POST se extraen los datos del formulario.
    2) Se verifica el tipo de formulario (login o register) mediante el botón enviado.
    3) Para registro:
        - Validaciones de campos requeridos
        - Verifica si email/usuario ya existe
        - Crea el nuevo usuario
        - Redirige a home
    4) Para login:
        - Validaciones de campos requeridos
        - Verifica credenciales
        - Redirige a home si son correctas
    5) Si no es POST -> renderiza el formulario combinado.
    """

    if request.method == "POST":
        form_type = request.POST.get('form_type')
        
        if form_type == 'register':
            # Lógica de registro
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            phone_number = request.POST.get("phone_number")

            # Validación de confirmación de contraseña
            if password != confirm_password:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, 'loginservice/login.html')

            # Obtiene CustomUser de settings.AUTH_USER_MODEL
            User = get_user_model()

            # Verifica si el email existe
            if User.objects.filter(email=email).exists():
                messages.error(request, "El email ya está registrado.")
                return render(request, 'loginservice/login.html')

            # Verifica si el username existe
            if User.objects.filter(username=username).exists():
                messages.error(request, "El usuario ya está registrado.")
                return render(request, 'loginservice/login.html')

            # Si pasa las validaciones, crea el nuevo usuario
            User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone_number=phone_number
            )

            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('loginservice:home')

        elif form_type == 'login':
            # Lógica de login
            username = request.POST.get("username")
            password = request.POST.get("password")

            # Valida los datos del formulario
            if not username:
                messages.error(request, "Debe ingresar su usuario.")
                return render(request, 'loginservice/login.html')

            if not password:
                messages.error(request, "Debe ingresar su contraseña.")
                return render(request, 'loginservice/login.html')

            # Obtiene el modelo settings.AUTH_USER_MODEL
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                # Valida el password
                if user.check_password(password):
                    messages.success(request, f"Bienvenido {user.first_name}!")
                    return redirect('loginservice:home')
                else:
                    messages.error(request, 'La contraseña no coincide.')
                    return render(request, 'loginservice/login.html')
            except User.DoesNotExist:
                messages.error(request, 'El usuario no existe.')
                return render(request, 'loginservice/login.html')

    # Si no es POST, renderiza el formulario combinado
    return render(request, 'loginservice/login.html')


# Vistas de compatibilidad (redirigen a la vista combinada)
def register_view(request):
    """Vista de compatibilidad - redirige a auth_view"""
    return auth_view(request)


def login_view(request):
    """Vista de compatibilidad - redirige a auth_view"""
    return auth_view(request)
        

def home(request):
    return render(request, 'loginservice/home.html')

