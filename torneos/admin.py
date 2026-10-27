from django.contrib import admin
from .models import (Deporte, Ubicacion, Usuario, PerfilUsuario, Equipo,
                     Torneo, ReglasTorneo, Inscripcion, Partido, Resultado)

admin.site.register([Deporte, Ubicacion, Usuario, PerfilUsuario, Equipo,
                     Torneo, ReglasTorneo, Inscripcion, Partido, Resultado])