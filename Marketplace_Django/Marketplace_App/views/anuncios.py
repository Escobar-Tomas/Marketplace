from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator # Importante para la paginación
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Importamos los modelos desde el paquete superior
from Marketplace_App.models import Anuncio, Categoria, Reporte
from Marketplace_App.forms import AnuncioForm, ReporteForm

# --- TUPLA DE LOCALIDADES DE TUCUMÁN (Hardcodeada) ---
LOCALIDADES_TUCUMAN = (
    ('Acheral', 'Acheral'),
    ('Aguilares', 'Aguilares'),
    ('Alderetes', 'Alderetes'),
    ('Alpachiri', 'Alpachiri'),
    ('Alto Verde', 'Alto Verde'),
    ('Amaicha del Valle', 'Amaicha del Valle'),
    ('Amberes', 'Amberes'),
    ('Anca Juli', 'Anca Juli'),
    ('Arcadia', 'Arcadia'),
    ('Atahona', 'Atahona'),
    ('Banda del Río Salí', 'Banda del Río Salí'),
    ('Bella Vista', 'Bella Vista'),
    ('Benjamín Paz', 'Benjamín Paz'),
    ('Buena Vista', 'Buena Vista'),
    ('Burruyacú', 'Burruyacú'),
    ('Capitán Cáceres', 'Capitán Cáceres'),
    ('Cevil Redondo', 'Cevil Redondo'),
    ('Choromoro', 'Choromoro'),
    ('Ciudacita', 'Ciudacita'),
    ('Colalao del Valle', 'Colalao del Valle'),
    ('Colombres', 'Colombres'),
    ('Concepción', 'Concepción'),
    ('Delfín Gallo', 'Delfín Gallo'),
    ('El Bracho', 'El Bracho'),
    ('El Cadillal', 'El Cadillal'),
    ('El Cercado', 'El Cercado'),
    ('El Chañar', 'El Chañar'),
    ('El Manantial', 'El Manantial'),
    ('El Mojón', 'El Mojón'),
    ('El Mollar', 'El Mollar'),
    ('El Naranjito', 'El Naranjito'),
    ('El Naranjo', 'El Naranjo'),
    ('El Polear', 'El Polear'),
    ('El Puestito', 'El Puestito'),
    ('El Sacrificio', 'El Sacrificio'),
    ('El Sunchal', 'El Sunchal'),
    ('El Timbó', 'El Timbó'),
    ('Escaba', 'Escaba'),
    ('Esquina y Mancopa', 'Esquina y Mancopa'),
    ('Estación Aráoz', 'Estación Aráoz'),
    ('Famaillá', 'Famaillá'),
    ('Gastona', 'Gastona'),
    ('Gobernador Garmendia', 'Gobernador Garmendia'),
    ('Gobernador Piedrabuena', 'Gobernador Piedrabuena'),
    ('Graneros', 'Graneros'),
    ('Huasa Pampa', 'Huasa Pampa'),
    ('Juan Bautista Alberdi', 'Juan Bautista Alberdi'),
    ('La Cocha', 'La Cocha'),
    ('La Florida', 'La Florida'),
    ('La Madrid', 'La Madrid'),
    ('La Ramada', 'La Ramada'),
    ('La Trinidad', 'La Trinidad'),
    ('Las Cejas', 'Las Cejas'),
    ('Las Talitas', 'Las Talitas'),
    ('León Rougés', 'León Rougés'),
    ('Los Bulacio', 'Los Bulacio'),
    ('Los Gómez', 'Los Gómez'),
    ('Los Nogales', 'Los Nogales'),
    ('Los Pereyra', 'Los Pereyra'),
    ('Los Pérez', 'Los Pérez'),
    ('Los Puestos', 'Los Puestos'),
    ('Los Ralos', 'Los Ralos'),
    ('Los Sarmientos', 'Los Sarmientos'),
    ('Los Sosa', 'Los Sosa'),
    ('Lules', 'Lules'),
    ('Manuela Pedraza', 'Manuela Pedraza'),
    ('Medinas', 'Medinas'),
    ('Monte Bello', 'Monte Bello'),
    ('Monteagudo', 'Monteagudo'),
    ('Monteros', 'Monteros'),
    ('Padre Monti', 'Padre Monti'),
    ('Pampa Mayo', 'Pampa Mayo'),
    ('Quilmes', 'Quilmes'),
    ('Raco', 'Raco'),
    ('Ranchillos', 'Ranchillos'),
    ('Río Chico', 'Río Chico'),
    ('Río Colorado', 'Río Colorado'),
    ('Río Seco', 'Río Seco'),
    ('Rumi Punco', 'Rumi Punco'),
    ('San Andrés', 'San Andrés'),
    ('San Felipe', 'San Felipe'),
    ('San Ignacio', 'San Ignacio'),
    ('San Javier', 'San Javier'),
    ('San José de la Cocha', 'San José de la Cocha'),
    ('San Miguel de Tucumán', 'San Miguel de Tucumán'),
    ('San Pablo', 'San Pablo'),
    ('San Pedro de Colalao', 'San Pedro de Colalao'),
    ('Santa Ana', 'Santa Ana'),
    ('Santa Cruz', 'Santa Cruz'),
    ('Santa Lucía', 'Santa Lucía'),
    ('Santa Rosa de Leales', 'Santa Rosa de Leales'),
    ('Sargento Moya', 'Sargento Moya'),
    ('Simoca', 'Simoca'),
    ('Soldado Maldonado', 'Soldado Maldonado'),
    ('Taco Ralo', 'Taco Ralo'),
    ('Tafí del Valle', 'Tafí del Valle'),
    ('Tafí Viejo', 'Tafí Viejo'),
    ('Tapia', 'Tapia'),
    ('Teniente Berdina', 'Teniente Berdina'),
    ('Trancas', 'Trancas'),
    ('Villa Belgrano', 'Villa Belgrano'),
    ('Villa Benjamín Aráoz', 'Villa Benjamín Aráoz'),
    ('Villa Chiligasta', 'Villa Chiligasta'),
    ('Villa de Leales', 'Villa de Leales'),
    ('Villa Fiad', 'Villa Fiad'),
    ('Villa Nougués', 'Villa Nougués'),
    ('Villa Padre Monti', 'Villa Padre Monti'),
    ('Villa Quinteros', 'Villa Quinteros'),
    ('Yanima', 'Yanima'),
    ('Yerba Buena', 'Yerba Buena'),
)

def home(request, categoria_slug=None):
    # 1. Obtener categorías y productos base
    categorias = Categoria.objects.all()
    productos = Anuncio.objects.filter(activo=True).order_by('-fecha_publicacion')

    # 2. DEFINIR UBICACIONES (MODIFICADO)
    # En lugar de consultar la BD, extraemos solo los nombres de la tupla hardcodeada.
    # Esto asegura que el select del frontend tenga TODAS las opciones,
    # independientemente de si hay anuncios creados o no.
    ubicaciones = [loc[0] for loc in LOCALIDADES_TUCUMAN]
    
    # 3. FILTRO: Categoría
    categoria_actual = None
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    # 4. FILTRO: Ubicación
    ubicacion_actual = request.GET.get('ubicacion')
    if ubicacion_actual:
        # Filtramos los productos cuya ubicación coincida con la selección
        productos = productos.filter(ubicacion=ubicacion_actual)
        
    # 5. FILTRO: Búsqueda (Texto)
    busqueda = request.GET.get('q')
    if busqueda:
        productos = productos.filter(
            Q(titulo__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )

    # 6. ORDENAMIENTO: Precio
    orden = request.GET.get('orden')
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
        
    # 7. FILTRO: Tiempo de publicación
    tiempo = request.GET.get('tiempo')
    if tiempo:
        hoy = timezone.now()
        fecha_limite = None
        
        if tiempo == '24h':
            fecha_limite = hoy - timedelta(days=1)
        elif tiempo == '7d':
            fecha_limite = hoy - timedelta(days=7)
        elif tiempo == '30d':
            fecha_limite = hoy - timedelta(days=30)
            
        if fecha_limite:
            # Filtramos los que sean MAYORES o IGUALES a la fecha límite
            productos = productos.filter(fecha_publicacion__gte=fecha_limite)

    # 8. PAGINACIÓN
    paginator = Paginator(productos, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'productos': page_obj, 
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'ubicaciones': ubicaciones,     # Ahora pasamos la lista completa de Tucumán
        'ubicacion_actual': ubicacion_actual,
        'busqueda': busqueda,
        'orden': orden,
        'tiempo_actual': tiempo,
    }
    return render(request, 'Marketplace_App/home.html', context)

@login_required
def crear_anuncio(request):
    # --- CANDADO DE SEGURIDAD MEJORADO ---
    try:
        perfil = request.user.perfil
        # 1. Chequeamos el tilde de verificado
        # 2. Y ADEMÁS chequeamos que realmente tenga un número escrito (que no esté vacío)
        if not perfil.telefono_verificado or not perfil.telefono_contacto:
            messages.warning(request, "⚠️ Para publicar anuncios, primero debes verificar tu número de celular.")
            return redirect('verificar_telefono')
    except Exception:
        # Si no tiene perfil, lo mandamos a crear uno verificando el teléfono
        return redirect('verificar_telefono')
    
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.usuario = request.user
            anuncio.save()
            messages.success(request, '¡Tu anuncio ha sido publicado con éxito!')
            return redirect('home')
    else:
        form = AnuncioForm()
        
    context = {'form': form}
    # NOTA: Actualizamos la ruta al template
    return render(request, 'Marketplace_App/anuncios/crear_anuncio.html', context)

def detalle_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk, activo=True)
    context = {'anuncio': anuncio}
    # NOTA: Actualizamos la ruta al template
    return render(request, 'Marketplace_App/anuncios/detalle_anuncio.html', context)

@login_required
def editar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio actualizado correctamente.')
        else:
            messages.error(request, 'Error al actualizar el anuncio.')
            
    return redirect('mi_perfil')

@login_required
def eliminar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    
    if anuncio.usuario != request.user:
        messages.error(request, "No tienes permiso para eliminar este anuncio.")
        return redirect('mi_perfil')
    
    if request.method == 'POST':
        anuncio.delete()
        messages.success(request, "El anuncio ha sido eliminado correctamente.")
        return redirect('mi_perfil')
        
    return redirect('mi_perfil')

@login_required
def marcar_vendido(request, pk):
    # Solo el dueño puede marcarlo
    anuncio = get_object_or_404(Anuncio, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Cambiamos el estado (asumiendo que 'vendido' es una opción válida en tu modelo o texto)
        # Si usas choices, asegúrate de que el valor coincida. Si es texto libre:
        anuncio.estado = 'Vendido' 
        anuncio.activo = False # Lo ocultamos de la home
        anuncio.save()
        
        messages.success(request, f'¡Felicidades! El anuncio "{anuncio.titulo}" se ha marcado como vendido.')
        
    return redirect('mi_perfil')

@login_required
def reportar_anuncio(request, pk):
    anuncio = get_object_or_404(Anuncio, pk=pk)
    
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            # Llenamos los datos automáticos
            reporte.usuario_reportador = request.user
            reporte.tipo_entidad_reportada = 'ANUNCIO'
            reporte.identificador_entidad_reportada = anuncio.id
            reporte.save()
            
            messages.success(request, "El reporte ha sido enviado a los administradores.")
            return redirect('detalle_anuncio', pk=pk)
    else:
        form = ReporteForm()
        
    context = {
        'form': form,
        'anuncio': anuncio
    }
    return render(request, 'Marketplace_App/formularios/reportar_anuncio.html', context)