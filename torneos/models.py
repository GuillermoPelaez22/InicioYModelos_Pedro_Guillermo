from django.db import models


class Deporte(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    por_equipos = models.BooleanField(default=True)
    jugadores_por_equipo = models.IntegerField(default=5)

    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    capacidad = models.IntegerField(null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    deportes = models.ManyToManyField(Deporte, related_name='ubicaciones')

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    NIVELES = [
        ('aficionado', 'Aficionado'),
        ('intermedio', 'Intermedio'),
        ('competitivo', 'Competitivo'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    biografia = models.TextField(blank=True)
    nivel = models.CharField(max_length=20, choices=NIVELES, default='aficionado')
    valoracion = models.FloatField(default=0)

    def __str__(self):
        return f"Perfil de {self.usuario.nombre}"


class Equipo(models.Model):
    nombre = models.CharField(max_length=60)
    fecha_creacion = models.DateField()
    color = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    capitan = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='equipos_capitaneados')
    miembros = models.ManyToManyField(Usuario, related_name='equipos')

    def __str__(self):
        return self.nombre


class Torneo(models.Model):
    FORMATOS = [
        ('liga', 'Liga'),
        ('eliminatoria', 'Eliminatoria'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    formato = models.CharField(max_length=20, choices=FORMATOS, default='liga')
    fecha_inicio = models.DateField()
    hora_partidos = models.TimeField(null=True, blank=True)
    max_participantes = models.IntegerField(default=8)
    es_publico = models.BooleanField(default=True)
    codigo_invitacion = models.CharField(
        max_length=10, unique=True, null=True, blank=True)
    cuota_inscripcion = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE)
    organizador = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='torneos_organizados')
    sede = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, related_name='torneos')
    equipos = models.ManyToManyField(Equipo, through='Inscripcion')

    def __str__(self):
        return self.nombre


class ReglasTorneo(models.Model):
    torneo = models.OneToOneField(Torneo, on_delete=models.CASCADE)
    puntos_victoria = models.IntegerField(default=3)
    puntos_empate = models.IntegerField(default=1)
    puntos_derrota = models.IntegerField(default=0)
    normas = models.TextField(blank=True)

    def __str__(self):
        return f"Reglas de {self.torneo.nombre}"


class Inscripcion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    pagada = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.equipo.nombre} en {self.torneo.nombre}"


class Partido(models.Model):
    ESTADOS = [
        ('programado', 'Programado'),
        ('jugado', 'Jugado'),
        ('suspendido', 'Suspendido'),
    ]
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    equipo_local = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='partidos_local')
    equipo_visitante = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='partidos_visitante')
    fecha_hora = models.DateTimeField()
    jornada = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programado')
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante}"


class Resultado(models.Model):
    partido = models.OneToOneField(Partido, on_delete=models.CASCADE)
    puntos_local = models.IntegerField(default=0)
    puntos_visitante = models.IntegerField(default=0)
    validado = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"{self.puntos_local} - {self.puntos_visitante}"