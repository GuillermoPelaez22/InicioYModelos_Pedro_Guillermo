import random

from django.core.management.base import BaseCommand
from faker import Faker

from torneos.models import (Deporte, Ubicacion, Usuario, PerfilUsuario, Equipo,
                            Torneo, ReglasTorneo, Inscripcion, Partido, Resultado)


class Command(BaseCommand):
    help = 'Genera 10 registros aleatorios de cada modelo con Faker'

    def handle(self, *args, **kwargs):
        fake = Faker('es_ES')

        # 1. Deportes (10, nombres distintos porque 'nombre' es unique)
        nombres_deportes = ['Fútbol', 'Baloncesto', 'Pádel', 'Tenis', 'Voleibol',
                            'Balonmano', 'Rugby', 'Hockey', 'Bádminton',
                            'Tenis de mesa']
        deportes = []
        for nombre in nombres_deportes:
            deporte, _ = Deporte.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': fake.paragraph(nb_sentences=2),
                    'por_equipos': random.choice([True, False]),
                    'jugadores_por_equipo': random.randint(1, 11),
                })
            deportes.append(deporte)

        # 2. Ubicaciones (10) + relación ManyToMany con deportes
        ubicaciones = []
        for _ in range(10):
            ubicacion = Ubicacion.objects.create(
                nombre=f"Pabellón {fake.last_name()}",
                direccion=fake.address().replace('\n', ', '),
                capacidad=random.randint(50, 2000),
                latitud=float(fake.latitude()),
            )
            ubicacion.deportes.set(random.sample(deportes, random.randint(1, 3)))
            ubicaciones.append(ubicacion)

        # 3. Usuarios (10)
        usuarios = []
        for _ in range(10):
            usuarios.append(Usuario.objects.create(
                nombre=fake.name(),
                email=fake.unique.email(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=16, maximum_age=60),
                activo=random.choice([True, True, True, False]),
            ))

        # 4. Perfiles (10, uno por usuario: relación OneToOne)
        for usuario in usuarios:
            PerfilUsuario.objects.create(
                usuario=usuario,
                telefono=fake.numerify('6########'),
                biografia=fake.paragraph(nb_sentences=2),
                nivel=random.choice(['aficionado', 'intermedio', 'competitivo']),
                valoracion=round(random.uniform(0, 5), 1),
            )

        # 5. Equipos (10) + miembros (ManyToMany)
        equipos = []
        for _ in range(10):
            equipo = Equipo.objects.create(
                nombre=f"{fake.city()} {random.choice(['FC', 'United', 'CB', 'Club'])}",
                fecha_creacion=fake.date_between(start_date='-5y', end_date='today'),
                color=fake.color_name(),
                activo=random.choice([True, True, False]),
                capitan=random.choice(usuarios),
            )
            equipo.miembros.set(random.sample(usuarios, random.randint(3, 6)))
            equipos.append(equipo)

        # 6. Torneos (10)
        torneos = []
        for _ in range(10):
            es_publico = random.choice([True, False])
            torneos.append(Torneo.objects.create(
                nombre=f"Copa {fake.city()}",
                descripcion=fake.paragraph(nb_sentences=3),
                formato=random.choice(['liga', 'eliminatoria']),
                fecha_inicio=fake.date_between(start_date='today', end_date='+6M'),
                hora_partidos=fake.time_object(),
                max_participantes=random.choice([4, 8, 16]),
                es_publico=es_publico,
                # Solo los torneos privados tienen código de invitación
                codigo_invitacion=None if es_publico else fake.unique.bothify(
                    text='??####', letters='ABCDEFGHJKLMNPQRSTUVWXYZ'),
                cuota_inscripcion=random.randint(0, 30),
                deporte=random.choice(deportes),
                organizador=random.choice(usuarios),
                sede=random.choice(ubicaciones),
            ))

        # 7. Reglas (10, una por torneo: relación OneToOne)
        for torneo in torneos:
            ReglasTorneo.objects.create(
                torneo=torneo,
                puntos_victoria=random.choice([2, 3]),
                puntos_empate=1,
                puntos_derrota=0,
                normas=fake.paragraph(nb_sentences=3),
            )

        # 8, 9 y 10. Inscripciones, partidos y resultados (10 de cada uno)
        # Se eligen 5 torneos; en cada uno se inscriben 2 equipos que juegan
        # partido de ida y de vuelta: 5x2 = 10 inscripciones, 10 partidos
        # y 10 resultados (uno por partido).
        for torneo in random.sample(torneos, 5):
            local, visitante = random.sample(equipos, 2)
            for equipo in (local, visitante):
                Inscripcion.objects.create(
                    torneo=torneo,
                    equipo=equipo,
                    estado='aceptada',
                    pagada=random.choice([True, False]),
                    observaciones=fake.sentence(),
                )
            enfrentamientos = [(local, visitante), (visitante, local)]
            for jornada, (a, b) in enumerate(enfrentamientos, start=1):
                partido = Partido.objects.create(
                    torneo=torneo,
                    equipo_local=a,
                    equipo_visitante=b,
                    fecha_hora=fake.date_time_between(start_date='-1M', end_date='+1M'),
                    jornada=jornada,
                    estado='jugado',
                    notas=fake.sentence(),
                )
                Resultado.objects.create(
                    partido=partido,
                    puntos_local=random.randint(0, 5),
                    puntos_visitante=random.randint(0, 5),
                    validado=random.choice([True, False]),
                    comentarios=fake.sentence(),
                )

        self.stdout.write(self.style.SUCCESS('Datos generados correctamente'))