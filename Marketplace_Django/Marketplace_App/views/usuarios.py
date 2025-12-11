import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from Marketplace_App.forms import RegisterForm, PerfilUsuarioForm, AnuncioForm
from Marketplace_App.models import PerfilUsuario, Anuncio
from django.contrib.auth.decorators import login_required

# --- 1. LOGIN PERSONALIZADO (Con "Recordarme") ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Lógica de "Recordarme"
            if request.POST.get('remember_me'):
                request.session.set_expiry(30 * 24 * 60 * 60) 
            else:
                request.session.set_expiry(0) 
                
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

# --- 2. REGISTRO (Mejorado para fallos de mail) ---
def registro(request):
    if request.method == 'POST':
        formulario_registro = RegisterForm(request.POST)
        if formulario_registro.is_valid():
            username = formulario_registro.cleaned_data['username']
            email = formulario_registro.cleaned_data['email']
            password = formulario_registro.cleaned_data['password']
            password2 = formulario_registro.cleaned_data['password2']
            
            if password == password2:
                user = None
                try:
                    # 1. Verificar si el email existe
                    usuario_existente = User.objects.filter(email=email).first()
                    
                    if usuario_existente:
                        # SI existe pero NO está activo, es un intento fallido anterior. Lo reciclamos.
                        if not usuario_existente.is_active:
                            user = usuario_existente
                            user.username = username
                            user.set_password(password)
                            user.save()
                        else:
                            messages.error(request, "Este correo electrónico ya está registrado y activo.")
                            return render(request, 'Marketplace_App/usuarios/registro.html', {'formulario_registro': formulario_registro})
                    else:
                        # Verificar username
                        if User.objects.filter(username=username).exists():
                             messages.error(request, "Este nombre de usuario ya está en uso.")
                             return render(request, 'Marketplace_App/usuarios/registro.html', {'formulario_registro': formulario_registro})

                        # Crear usuario nuevo INACTIVO
                        user = User.objects.create_user(username=username, email=email, password=password)
                        user.is_active = False 
                        user.save()
                    
                    # 2. Generar código
                    codigo = random.randint(100000, 999999)
                    
                    # 3. Guardar en sesión
                    request.session['registro_user_id'] = user.id
                    request.session['registro_codigo'] = codigo
                    
                    # 4. Intentar enviar correo (Punto crítico)
                    print(f"Intentando enviar correo a {email} usando {settings.EMAIL_HOST_USER}") # Log para consola
                    send_mail(
                        'Verifica tu cuenta - Marketplace',
                        f'Tu código de activación es: {codigo}',
                        settings.EMAIL_HOST_USER or 'noreply@marketplace.com', # Fallback para evitar error None
                        [email],
                        fail_silently=False,
                    )
                    
                    messages.info(request, f'Te hemos enviado un código a {email}. Ingrésalo para activar tu cuenta.')
                    return redirect('verificar_registro') # Esta URL debe existir en urls.py como 'validar-sms' o similar
                    
                except Exception as e:
                    # SI FALLA EL MAIL: Borramos el usuario para que no quede "zombi" y pueda reintentar
                    if user and not usuario_existente: # Solo borramos si lo acabamos de crear
                        user.delete()
                    
                    print(f"ERROR ENVIO MAIL: {str(e)}") # Importante para ver en la consola de PythonAnywhere
                    messages.error(request, f"Hubo un error enviando el correo. Por favor verifica que el email sea real. Error: {e}")
            else:
                messages.error(request, "Las contraseñas no coinciden.")
    else:
        formulario_registro = RegisterForm()
    
    return render(request, 'Marketplace_App/usuarios/registro.html', {'formulario_registro': formulario_registro})

# --- 3. VERIFICACIÓN DE REGISTRO (Paso 2) ---
# Nota: Asegúrate de tener una URL apuntando aquí, ej: path('verificar-registro/', views.verificar_registro, name='verificar_registro')
def verificar_registro(request):
    # Si no hay un proceso de registro en curso, mandar al home
    if 'registro_user_id' not in request.session:
        return redirect('home')
        
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_generado = request.session.get('registro_codigo')
        user_id = request.session.get('registro_user_id')
        
        # Comparar strings y quitar espacios
        if str(codigo_ingresado).strip() == str(codigo_generado).strip():
            try:
                # Activar el usuario
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                # Crear perfil si no existe
                PerfilUsuario.objects.get_or_create(usuario=user)
                
                # Limpiar sesión temporal
                if 'registro_user_id' in request.session: del request.session['registro_user_id']
                if 'registro_codigo' in request.session: del request.session['registro_codigo']
                
                # Iniciar sesión automáticamente
                login(request, user)
                
                messages.success(request, '¡Cuenta verificada exitosamente! Bienvenido.')
                return redirect('home')
                
            except User.DoesNotExist:
                messages.error(request, 'Error al encontrar el usuario. Intenta registrarte de nuevo.')
                return redirect('registro')
        else:
            messages.error(request, 'Código incorrecto. Inténtalo de nuevo.')

    return render(request, 'Marketplace_App/formularios/verificacion_2fa.html')

@login_required
def verificar_telefono(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        
        if telefono:
            perfil.telefono_contacto = telefono
            perfil.telefono_verificado = False 
            perfil.save()
            
            codigo = random.randint(100000, 999999)
            request.session['sms_codigo'] = codigo
            
            # SIMULACIÓN (Ya que no hay SMS real configurado)
            print(f">>> SIMULACIÓN SMS: El código para {telefono} es {codigo} <<<")
            
            messages.info(request, f"Te enviamos un código de verificación al {telefono}.")
            return redirect('validar_codigo_telefono')
        else:
            messages.error(request, "Por favor ingresa un número válido.")
            
    return render(request, 'Marketplace_App/formularios/verificar_telefono.html', {'perfil': perfil})

@login_required
def validar_codigo_telefono(request):
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo')
        codigo_real = request.session.get('sms_codigo')
        
        if codigo_real and str(codigo_ingresado).strip() == str(codigo_real):
            perfil = request.user.perfil
            perfil.telefono_verificado = True
            perfil.save()
            
            if 'sms_codigo' in request.session:
                del request.session['sms_codigo']
            
            messages.success(request, "¡Teléfono verificado correctamente!")
            return redirect('crear_anuncio') 
        else:
            messages.error(request, "Código incorrecto. Inténtalo de nuevo.")
            
    return render(request, 'Marketplace_App/formularios/validar_codigo_telefono.html')

# --- 4. PERFIL DE USUARIO ---
@login_required
def mi_perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    form_perfil = PerfilUsuarioForm(instance=perfil)

    mis_anuncios_qs = Anuncio.objects.filter(usuario=request.user).order_by('-fecha_publicacion')
    anuncios_con_forms = []
    
    for anuncio in mis_anuncios_qs:
        form = AnuncioForm(instance=anuncio)
        anuncios_con_forms.append((anuncio, form))

    context = {
        'perfil': perfil,
        'form_perfil': form_perfil,
        'anuncios_con_forms': anuncios_con_forms
    }
    return render(request, 'Marketplace_App/usuarios/mi_perfil.html', context)

@login_required
def editar_perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        
        if form.is_valid():
            if 'telefono_contacto' in form.changed_data:
                instancia = form.save(commit=False)
                instancia.telefono_verificado = False
                instancia.save()
                if not instancia.telefono_contacto:
                     messages.warning(request, 'Has eliminado tu teléfono. Necesitarás verificar uno nuevo para publicar.')
                else:
                     messages.info(request, 'Al cambiar tu número, deberás verificarlo nuevamente para publicar.')
            else:
                form.save()

            messages.success(request, 'Perfil actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el perfil.')
            
    return redirect('mi_perfil')