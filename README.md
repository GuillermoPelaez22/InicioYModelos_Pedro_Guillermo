# TorneoHub

**TorneoHub** es una aplicación web hecha con Django que permite crear torneos deportivos y apuntarse a otros, tanto públicos como privados (por invitación). Permite buscar torneos por deporte, fecha, nivel y ubicación, inscribirse de forma individual o por equipos, generar calendarios, registrar resultados y consultar la clasificación.

El rol depende del torneo: quien lo crea es su administrador y los inscritos son participantes.

**Autor:** Guillermo Peláez y Pedro Rivas · 2º DAW · IES Polígono Sur

---

## Cómo ejecutarlo

```bash
git clone https://github.com/GuillermoPelaez22/InicioYModelos_Pedro_Guillermo.git
cd InicioYModelos_Pedro_Guillermo
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Ramas del repositorio

| Rama | Contenido |
|---|---|
| `Configuracion_inicial` | Proyecto Django y configuración |
| `Modelos` | Modelos, README, esquema E-R y seeders |
| `Backups` | Fixtures con copias de los datos |

---

## Esquema entidad-relación

![Esquema entidad-relación de TorneoHub](docs/modelo_er.png)

### Resumen de relaciones

| Tipo | Relación |
|---|---|
| OneToOne | `PerfilUsuario` ↔ `Usuario` |
| OneToOne | `ReglasTorneo` ↔ `Torneo` |
| OneToOne | `Resultado` ↔ `Partido` |
| ManyToOne | `Equipo` → `Usuario` (capitán) |
| ManyToOne | `Torneo` → `Deporte`, `Usuario` (organizador), `Ubicacion` (sede) |
| ManyToOne | `Partido` → `Torneo`, `Equipo` (local), `Equipo` (visitante) |
| ManyToOne | `Inscripcion` → `Torneo`, `Usuario`, `Rol` y `Equipo` (opcional) |
| ManyToOne | `Clasificacion` → `Torneo`, `Equipo` |
| ManyToMany | `Ubicacion` ↔ `Deporte` (tabla intermedia automática) |
| ManyToMany | `Equipo` ↔ `Usuario` (miembros; tabla intermedia automática) |
| ManyToMany | `Torneo` ↔ `Equipo` a través de `Inscripcion` (tabla intermedia con atributos extra) |

### Entidades débiles y fuertes

Una entidad es **débil** si no se puede identificar por sí sola y no tiene sentido sin otra entidad propietaria; su clave en el esquema es la de esa entidad. Es **fuerte** si tiene identidad propia. Aunque Django añade un `id` automático a todas las tablas, en el esquema la clave de las entidades débiles es la de su propietaria.

| Entidad | Tipo | Motivo |
|---|---|---|
| `PerfilUsuario` | Débil | Depende de `Usuario` (relación 1-1) |
| `ReglasTorneo` | Débil | Unas reglas no tienen sentido sin su torneo (relación 1-1) |
| `Resultado` | Débil | Depende de `Partido` (relación 1-1) |
| `Clasificacion` | Débil | Se identifica por la pareja torneo + equipo |
| `Deporte`, `Ubicacion`, `Usuario`, `Equipo`, `Torneo`, `Rol`, `Partido` | Fuerte | Existen por sí mismas y se identifican con su propio `id` |
| `Inscripcion` | Tabla intermedia | Une `Torneo`, `Usuario` y `Equipo` y guarda atributos extra |

### Roles

El rol depende del torneo y no del usuario, por eso se guarda en `Inscripcion`: cada inscripción une un usuario con un torneo y tiene un `Rol` (por ejemplo, administrador o participante). El mismo usuario puede ser administrador en un torneo y participante en otro. El campo `equipo` de la inscripción es opcional: si está vacío, la inscripción es individual.

---

## Modelos

### 1. Deporte
Deporte que se puede jugar en un torneo (fútbol, pádel, baloncesto...).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=50`, `unique=True` | Nombre del deporte, sin repetirse |
| descripcion | TextField | `blank=True` | Descripción opcional |
| por_equipos | BooleanField | `default=True` | Si se juega por equipos o individualmente |
| jugadores_por_equipo | IntegerField | `default=5` | Número de jugadores de cada equipo |
| categoria | CharField | `max_length=30` | Familia del deporte (pelota, raqueta, combate...) |
| duracion_partido | IntegerField | `default=60` | Duración de un partido en minutos |
| permite_empate | BooleanField | `default=True` | Si el deporte admite empates |
| material_necesario | TextField | `blank=True` | Material que hace falta para jugar |
| url_reglamento | URLField | `blank=True` | Enlace al reglamento oficial |
| activo | BooleanField | `default=True` | Si el deporte está disponible al crear torneos |

### 2. Ubicacion
Lugar donde se celebran los torneos (pabellón, polideportivo, campo...).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=100` | Nombre del lugar |
| direccion | CharField | `max_length=200` | Dirección |
| capacidad | IntegerField | `null=True`, `blank=True` | Aforo (opcional) |
| latitud | FloatField | `null=True`, `blank=True` | Coordenada geográfica (opcional) |
| deportes | ManyToManyField | `related_name='ubicaciones'` | Deportes que se pueden practicar allí |

### 3. Usuario
Persona registrada en la aplicación.

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=80` | Nombre del usuario |
| email | EmailField | `unique=True` | Correo electrónico, sin repetirse |
| fecha_nacimiento | DateField | `null=True`, `blank=True` | Fecha de nacimiento (opcional) |
| fecha_registro | DateTimeField | `auto_now_add=True` | Fecha y hora en que se registró (automática) |
| activo | BooleanField | `default=True` | Si la cuenta está activa |

### 4. PerfilUsuario
Datos adicionales de cada usuario (entidad débil, relación uno a uno).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| usuario | OneToOneField | `on_delete=models.CASCADE` | Usuario al que pertenece el perfil |
| telefono | CharField | `max_length=15`, `blank=True` | Teléfono (opcional) |
| biografia | TextField | `blank=True` | Texto de presentación |
| nivel | CharField | `max_length=20`, `choices=NIVELES`, `default='aficionado'` | Nivel de juego: aficionado, intermedio o competitivo |
| valoracion | FloatField | `default=0` | Valoración media del jugador |

### 5. Equipo
Equipo de jugadores que se inscribe en los torneos.

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=60` | Nombre del equipo |
| fecha_creacion | DateField | — | Fecha en que se creó el equipo |
| color | CharField | `max_length=20`, `blank=True` | Color de la equipación (opcional) |
| activo | BooleanField | `default=True` | Si el equipo sigue activo |
| capitan | ForeignKey | `on_delete=models.CASCADE`, `related_name='equipos_capitaneados'` | Usuario que es capitán |
| miembros | ManyToManyField | `related_name='equipos'` | Usuarios que forman el equipo |

### 6. Torneo
Competición deportiva, pública o privada.

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=100` | Nombre del torneo |
| descripcion | TextField | `blank=True` | Descripción |
| formato | CharField | `max_length=20`, `choices=FORMATOS`, `default='liga'` | Liga o eliminatoria |
| fecha_inicio | DateField | — | Día en que empieza |
| hora_partidos | TimeField | `null=True`, `blank=True` | Hora habitual de los partidos |
| max_participantes | IntegerField | `default=8` | Número máximo de equipos |
| es_publico | BooleanField | `default=True` | Público (visible para todos) o privado |
| codigo_invitacion | CharField | `max_length=10`, `unique=True`, `null=True`, `blank=True` | Código para entrar a un torneo privado |
| cuota_inscripcion | DecimalField | `max_digits=6`, `decimal_places=2`, `default=0` | Precio de inscripción en euros |
| deporte | ForeignKey | `on_delete=models.CASCADE` | Deporte del torneo |
| organizador | ForeignKey | `on_delete=models.CASCADE`, `related_name='torneos_organizados'` | Usuario administrador del torneo |
| sede | ForeignKey | `on_delete=models.CASCADE`, `related_name='torneos'` | Ubicación donde se juega |
| equipos | ManyToManyField | `through='Inscripcion'` | Equipos inscritos (a través de `Inscripcion`) |

### 7. ReglasTorneo
Reglas de puntuación de cada torneo (entidad débil, relación uno a uno).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| torneo | OneToOneField | `on_delete=models.CASCADE` | Torneo al que pertenecen las reglas |
| puntos_victoria | IntegerField | `default=3` | Puntos por ganar |
| puntos_empate | IntegerField | `default=1` | Puntos por empatar |
| puntos_derrota | IntegerField | `default=0` | Puntos por perder |
| normas | TextField | `blank=True` | Normas en texto libre |

### 8. Rol
Papel que tiene un usuario dentro de un torneo (administrador, participante...).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| nombre | CharField | `max_length=30`, `unique=True` | Nombre del rol, sin repetirse |
| descripcion | TextField | `blank=True` | Qué puede hacer quien tiene este rol |
| puede_gestionar_torneo | BooleanField | `default=False` | Si puede modificar el torneo y aprobar inscripciones |
| puede_registrar_resultados | BooleanField | `default=False` | Si puede registrar y validar resultados |

### 9. Inscripcion
Tabla intermedia entre `Torneo`, `Usuario` y `Equipo`, con atributos extra. Indica quién se apunta a qué torneo, con qué rol y, si procede, representando a qué equipo.

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| torneo | ForeignKey | `on_delete=models.CASCADE` | Torneo en el que se inscribe |
| usuario | ForeignKey | `on_delete=models.CASCADE` | Usuario que se inscribe |
| equipo | ForeignKey | `on_delete=models.CASCADE`, `null=True`, `blank=True` | Equipo con el que se inscribe (vacío si es individual) |
| rol | ForeignKey | `on_delete=models.CASCADE` | Rol del usuario en ese torneo |
| fecha_inscripcion | DateTimeField | `auto_now_add=True` | Fecha y hora de la inscripción (automática) |
| estado | CharField | `max_length=20`, `choices=ESTADOS`, `default='pendiente'` | Pendiente, aceptada o rechazada |
| pagada | BooleanField | `default=False` | Si se ha pagado la cuota |
| observaciones | TextField | `blank=True` | Comentarios del organizador |

### 10. Clasificacion
Clasificación de un torneo: una fila por equipo (entidad débil, identificada por torneo + equipo).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| torneo | ForeignKey | `on_delete=models.CASCADE`, `related_name='clasificacion'` | Torneo al que pertenece la clasificación |
| equipo | ForeignKey | `on_delete=models.CASCADE` | Equipo clasificado |
| posicion | IntegerField | `default=0` | Puesto en la tabla |
| partidos_jugados | IntegerField | `default=0` | Partidos disputados |
| ganados | IntegerField | `default=0` | Partidos ganados |
| empatados | IntegerField | `default=0` | Partidos empatados |
| perdidos | IntegerField | `default=0` | Partidos perdidos |
| puntos_favor | IntegerField | `default=0` | Puntos a favor |
| puntos_contra | IntegerField | `default=0` | Puntos en contra |
| puntos | IntegerField | `default=0` | Puntos totales según las reglas del torneo |

Además, `class Meta` con `unique_together = ('torneo', 'equipo')` impide que un equipo aparezca dos veces en la clasificación del mismo torneo.

### 11. Partido
Encuentro entre dos equipos dentro de un torneo.

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| torneo | ForeignKey | `on_delete=models.CASCADE` | Torneo al que pertenece |
| equipo_local | ForeignKey | `on_delete=models.CASCADE`, `related_name='partidos_local'` | Equipo local |
| equipo_visitante | ForeignKey | `on_delete=models.CASCADE`, `related_name='partidos_visitante'` | Equipo visitante |
| fecha_hora | DateTimeField | — | Fecha y hora del partido |
| jornada | IntegerField | `default=1` | Número de jornada o ronda |
| estado | CharField | `max_length=20`, `choices=ESTADOS`, `default='programado'` | Programado, jugado o suspendido |
| notas | TextField | `blank=True` | Notas adicionales |

### 12. Resultado
Marcador de un partido (entidad débil, relación uno a uno).

| Atributo | Tipo | Parámetros | Qué guarda |
|---|---|---|---|
| partido | OneToOneField | `on_delete=models.CASCADE` | Partido al que pertenece |
| puntos_local | IntegerField | `default=0` | Puntos del equipo local |
| puntos_visitante | IntegerField | `default=0` | Puntos del equipo visitante |
| validado | BooleanField | `default=False` | Si el administrador ha validado el resultado |
| comentarios | TextField | `blank=True` | Comentarios del resultado |

---

## Tipos de campo usados (sin contar relaciones)

| Tipo | Para qué sirve | Ejemplo |
|---|---|---|
| CharField | Texto corto con longitud máxima | `Deporte.nombre` |
| TextField | Texto largo | `Torneo.descripcion` |
| IntegerField | Número entero | `Torneo.max_participantes` |
| FloatField | Número decimal (coma flotante) | `PerfilUsuario.valoracion` |
| BooleanField | Verdadero o falso | `Usuario.activo` |
| DateField | Fecha | `Torneo.fecha_inicio` |
| DateTimeField | Fecha y hora | `Partido.fecha_hora` |
| TimeField | Hora | `Torneo.hora_partidos` |
| DecimalField | Número decimal exacto (dinero) | `Torneo.cuota_inscripcion` |
| EmailField | Texto que valida el formato de un email | `Usuario.email` |
| URLField | Texto que valida el formato de una dirección web | `Deporte.url_reglamento` |

## Parámetros usados

| Parámetro | Para qué sirve | Dónde se usa |
|---|---|---|
| `max_length` | Longitud máxima de un campo de texto | `Deporte.nombre`, `Usuario.nombre`... |
| `unique` | El valor no se puede repetir en la tabla | `Deporte.nombre`, `Usuario.email`, `Rol.nombre`, `Torneo.codigo_invitacion` |
| `null` | Permite guardar `NULL` en la base de datos | `Ubicacion.capacidad`, `Inscripcion.equipo` |
| `blank` | Permite dejar el campo vacío en formularios y en el admin | `Deporte.descripcion`, `Inscripcion.equipo` |
| `default` | Valor por defecto si no se indica ninguno | `Deporte.por_equipos`, `Clasificacion.puntos` |
| `choices` | Limita el valor a una lista de opciones | `PerfilUsuario.nivel`, `Torneo.formato`, `Inscripcion.estado` |
| `auto_now_add` | Guarda automáticamente la fecha y hora al crear el registro | `Usuario.fecha_registro`, `Inscripcion.fecha_inscripcion` |
| `max_digits` | Número total de dígitos de un `DecimalField` | `Torneo.cuota_inscripcion` |
| `decimal_places` | Número de decimales de un `DecimalField` | `Torneo.cuota_inscripcion` |
| `on_delete` | Qué hacer al borrar el registro relacionado (`CASCADE` borra también los dependientes) | Todas las `ForeignKey` y `OneToOneField` |
| `related_name` | Nombre de la relación inversa; evita conflictos entre relaciones al mismo modelo | `Equipo.capitan`, `Clasificacion.torneo` |
| `through` | Indica la tabla intermedia propia de una relación muchos a muchos | `Torneo.equipos` → `Inscripcion` |
| `unique_together` | (Dentro de `class Meta`) Impide repetir una misma combinación de campos | `Clasificacion`: `('torneo', 'equipo')` |

---

## Datos de prueba

Generar 10 registros aleatorios de cada modelo con Faker:

```bash
python manage.py generar_datos
```

Crear una copia de los datos (fixture):

```bash
python manage.py dumpdata torneos --indent 4 > torneos/fixtures/datos.json
```

Restaurar los datos en una base de datos nueva:

```bash
python manage.py migrate
python manage.py loaddata torneos/fixtures/datos.json
```

---

## Código no visto en clase

| Código | Explicación |
|---|---|
| `DecimalField(max_digits=6, decimal_places=2)` | Campo para números decimales exactos, como el dinero. `max_digits` es el total de dígitos y `decimal_places` cuántos son decimales. Con 6 y 2 se admiten valores hasta 9999.99 |
| `EmailField` | Igual que un `CharField`, pero comprueba que el texto tenga formato de correo electrónico |
| `URLField` | Igual que un `CharField`, pero comprueba que el texto tenga formato de dirección web |
| `auto_now_add=True` | Django rellena el campo con la fecha y hora actuales solo al crear el registro, y no se puede modificar después |
| `NIVELES = [('aficionado', 'Aficionado'), ...]` | Lista de tuplas para `choices`. El primer valor es el que se guarda en la base de datos y el segundo el que se muestra al usuario |
| `class Meta` con `unique_together = ('torneo', 'equipo')` | `Meta` es una clase interna con opciones del modelo. `unique_together` hace que la combinación de esos dos campos no pueda repetirse |
| `ForeignKey(..., null=True, blank=True)` | Relación opcional: la base de datos admite `NULL` y el formulario admite dejarla vacía (inscripción individual, sin equipo) |
| `ForeignKey('Rol', ...)` | Se puede indicar el modelo con su nombre entre comillas cuando la clase está definida más abajo en el archivo |
| `f"Perfil de {self.usuario.nombre}"` | Cadena con formato (f-string): lo que va entre llaves se sustituye por el valor de la variable |
| `admin.site.register([...])` | Registra varios modelos de una vez en el panel de administración pasando una lista |
| `BaseCommand` y `handle()` | Clase de Django para crear comandos propios. El código del comando va dentro del método `handle`, que se ejecuta con `python manage.py generar_datos` |
| `help = '...'` | Texto de ayuda del comando |
| `Faker('es_ES')` | Crea el generador de datos falsos con nombres, ciudades y direcciones de España |
| `fake.unique.email()` | `unique` garantiza que Faker no repite el valor generado (necesario con campos `unique`) |
| `fake.name()`, `fake.city()`, `fake.last_name()` | Generan un nombre completo, una ciudad y un apellido |
| `fake.paragraph(nb_sentences=2)`, `fake.sentence()` | Generan un párrafo con 2 frases y una frase suelta |
| `fake.address()` | Genera una dirección; `.replace('\n', ', ')` cambia los saltos de línea por comas |
| `fake.latitude()` | Genera una latitud; `float(...)` la convierte a número decimal |
| `fake.date_of_birth(minimum_age, maximum_age)` | Fecha de nacimiento de alguien con una edad entre esos límites |
| `fake.date_between(start_date, end_date)` | Fecha aleatoria entre dos fechas (`'-5y'` = hace 5 años, `'+6M'` = dentro de 6 meses) |
| `fake.date_time_between(...)` | Igual, pero con fecha y hora |
| `fake.time_object()` | Hora aleatoria |
| `fake.numerify('6########')` | Sustituye cada `#` por un dígito aleatorio (un teléfono que empieza por 6) |
| `fake.bothify(text='??####', letters=...)` | Sustituye `?` por una letra de la lista y `#` por un dígito |
| `fake.color_name()` | Nombre de un color |
| `random.choice(lista)` | Elige un elemento al azar de una lista |
| `random.randint(a, b)` | Entero aleatorio entre a y b, ambos incluidos |
| `random.uniform(a, b)` | Decimal aleatorio entre a y b |
| `random.sample(lista, n)` | Elige n elementos distintos de una lista |
| `round(numero, 1)` | Redondea a 1 decimal |
| `Modelo.objects.create(...)` | Crea y guarda un registro en la base de datos |
| `get_or_create(nombre=..., defaults={...})` | Busca el registro; si no existe, lo crea con los valores de `defaults` |