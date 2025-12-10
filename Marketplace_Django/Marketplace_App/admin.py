from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Anuncio, PerfilUsuario, Comentario, Reporte

# --- 1. ADMINISTRACIÓN DE CATEGORÍAS ---
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'cantidad_anuncios')
    prepopulated_fields = {"slug": ("nombre",)}

    def cantidad_anuncios(self, obj):
        # Cuenta cuántos anuncios hay en esta categoría
        return obj.anuncios_categoria.count()
    cantidad_anuncios.short_description = 'Nº Anuncios'

# --- 2. ADMINISTRACIÓN DE ANUNCIOS (Con fotos y filtros) ---
class AnuncioAdmin(admin.ModelAdmin):
    # Columnas que se ven en la tabla
    list_display = ('mostrar_imagen', 'titulo', 'precio', 'usuario', 'categoria', 'estado', 'activo', 'fecha_publicacion')
    
    # Filtros laterales
    list_filter = ('activo', 'estado', 'categoria', 'fecha_publicacion')
    
    # Barra de búsqueda (busca por título, descripción o nombre del usuario)
    search_fields = ('titulo', 'descripcion', 'usuario__username', 'usuario__email')
    
    # Acciones masivas (para activar/desactivar varios a la vez)
    actions = ['marcar_como_inactivo', 'marcar_como_activo']

    # --- Función para mostrar miniatura de la imagen ---
    def mostrar_imagen(self, obj):
        if obj.imagen_principal:
            # Renderiza HTML seguro para ver la imagen pequeña
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:5px;" />', obj.imagen_principal.url)
        return "Sin imagen"
    mostrar_imagen.short_description = "Imagen"

    # --- Acciones personalizadas ---
    def marcar_como_inactivo(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, "Los anuncios seleccionados ahora están INACTIVOS.")
    marcar_como_inactivo.short_description = "Pausar/Ocultar anuncios seleccionados"

    def marcar_como_activo(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, "Los anuncios seleccionados ahora están ACTIVOS.")
    marcar_como_activo.short_description = "Activar anuncios seleccionados"

# --- 3. ADMINISTRACIÓN DE PERFILES DE USUARIO ---
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mostrar_telefono', 'rol', 'telefono_verificado', 'fecha_registro')
    list_filter = ('telefono_verificado', 'rol', 'fecha_registro')
    search_fields = ('usuario__username', 'usuario__email', 'telefono_contacto')
    
    def mostrar_telefono(self, obj):
        return obj.telefono_contacto if obj.telefono_contacto else "-"
    mostrar_telefono.short_description = "Teléfono"

# --- 4. ADMINISTRACIÓN DE REPORTES ---
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'usuario_reportador', 'tipo_entidad_reportada', 'id_entidad', 'fecha_reporte')
    list_filter = ('tipo_entidad_reportada', 'fecha_reporte')
    search_fields = ('motivo', 'descripcion_reporte')
    
    def id_entidad(self, obj):
        return f"{obj.tipo_entidad_reportada} #{obj.identificador_entidad_reportada}"
    id_entidad.short_description = "Entidad Reportada"

# --- REGISTRO DE MODELOS ---
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Anuncio, AnuncioAdmin)
admin.site.register(PerfilUsuario, PerfilUsuarioAdmin)
admin.site.register(Reporte, ReporteAdmin)
# admin.site.register(Comentario) # Descomenta si quieres moderar comentarios también

# --- PERSONALIZACIÓN DEL PANEL ---
admin.site.site_header = "Administración Marketplace Tucumán"  # Texto en la barra azul superior
admin.site.site_title = "Portal de Admins"                     # Título de la pestaña del navegador
admin.site.index_title = "Bienvenido al Centro de Control"     # Título principal de la página de inicio