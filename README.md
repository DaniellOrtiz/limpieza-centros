Limpieza de aseos en centros comerciales
Autor: Daniel Ortiz Caraballo

DESCRIPCIÓN

Aplicación para las limpiadoras de los aseos de centros comerciales grandes (como Lagoh en Sevilla). Sirve para fichar, consultar el cuadrante de turnos, llevar el inventario de productos de limpieza (papel higiénico, friegasuelos, lejía, limpiacristales, jabón de manos, guantes...), repartir los aseos entre los limpiadores que trabajan a la vez (la mitad si son dos, un tercio si son tres...) y saber en todo momento quién ha limpiado cada aseo.

ESQUEMA ENTIDAD-RELACIÓN

El esquema está en la imagen esquema_er.png

Relaciones:
- OneToOne: PerfilLimpiador-Limpiador, Centro-Limpiador (jefe de equipo), Fichaje-Cuadrante
- ManyToOne: Aseo-Centro, Turno-Centro, Cuadrante-Limpiador, Cuadrante-Turno, Inventario-Centro, Inventario-Producto, Limpieza-Cuadrante, Limpieza-Aseo
- ManyToMany: Turno-Limpiador (tabla intermedia Cuadrante, con atributos extra), Centro-Producto (tabla intermedia Inventario, con atributos extra), Limpieza-Producto

MODELOS

1. Limpiador: trabajador o trabajadora de la limpieza.
- nombre: CharField (max_length, verbose_name)
- dni: CharField (max_length, unique)
- email: EmailField (unique, help_text)
- telefono: CharField (max_length, blank, db_column)
- fecha_alta: DateField (default)
- activo: BooleanField (default)

2. PerfilLimpiador: datos extra del limpiador.
- limpiador: OneToOneField a Limpiador (on_delete, related_name)
- observaciones: TextField (blank)
- anios_experiencia: PositiveIntegerField (default, verbose_name)
- talla_guantes: CharField (max_length, choices, default)
- foto_url: URLField (null, blank)

3. Centro: centro comercial.
- nombre: CharField (max_length, unique)
- direccion: CharField (max_length, verbose_name)
- ciudad: CharField (max_length, default)
- superficie_m2: FloatField (help_text)
- fecha_apertura: DateField
- jefe_equipo: OneToOneField a Limpiador (on_delete, null, blank, related_name)
- productos: ManyToManyField a Producto (through, related_name)

4. Aseo: baño del centro comercial.
- codigo: CharField (max_length)
- planta: IntegerField (help_text)
- tipo: CharField (max_length, choices, default)
- accesible: BooleanField (default)
- num_cabinas: PositiveIntegerField (default, verbose_name)
- fecha_ultima_reforma: DateField (null, blank)
- centro: ForeignKey a Centro (on_delete, related_name)

5. Turno: franja de trabajo de un centro.
- tipo: CharField (max_length, choices, default)
- fecha: DateField
- hora_inicio: TimeField
- hora_fin: TimeField
- notas: TextField (blank)
- centro: ForeignKey a Centro (on_delete, related_name)
- limpiadores: ManyToManyField a Limpiador (through, related_name)

6. Cuadrante: tabla intermedia entre Turno y Limpiador. Dice quién trabaja en cada turno.
- limpiador: ForeignKey a Limpiador (on_delete, related_name)
- turno: ForeignKey a Turno (on_delete, related_name)
- confirmado: BooleanField (default)
- horas_extra: FloatField (default)
- fecha_asignacion: DateTimeField (auto_now_add)
- observaciones: TextField (blank)

7. Fichaje: entrada y salida de un limpiador en su turno.
- cuadrante: OneToOneField a Cuadrante (on_delete, related_name)
- hora_entrada: DateTimeField
- hora_salida: DateTimeField (null, blank)
- metodo: CharField (max_length, choices, default)
- observaciones: TextField (null, blank)

8. Producto: producto de limpieza.
- nombre: CharField (max_length, unique)
- categoria: CharField (max_length, choices)
- unidad_medida: CharField (max_length, default)
- precio_unidad: DecimalField (max_digits, decimal_places)
- es_quimico: BooleanField (default)
- stock_minimo: PositiveIntegerField (default, help_text)

9. Inventario: tabla intermedia entre Centro y Producto. Dice cuánto hay de cada producto en cada centro.
- centro: ForeignKey a Centro (on_delete, related_name)
- producto: ForeignKey a Producto (on_delete, related_name)
- cantidad_actual: PositiveIntegerField (default)
- ubicacion: CharField (max_length, blank, help_text)
- fecha_ultima_reposicion: DateField (null, blank)
- necesita_reposicion: BooleanField (default)

10. Limpieza: registro de quién limpia qué aseo.
- cuadrante: ForeignKey a Cuadrante (on_delete, related_name)
- aseo: ForeignKey a Aseo (on_delete, related_name)
- hora_inicio: DateTimeField (null, blank)
- hora_fin: DateTimeField (null, blank)
- estado: CharField (max_length, choices, default)
- observaciones: TextField (blank)
- productos_usados: ManyToManyField a Producto (blank, related_name)

PARÁMETROS USADOS

- max_length: tamaño máximo de un campo de texto
- null: permite guardar el valor como nulo en la base de datos
- blank: permite dejar el campo vacío
- choices: el valor se elige de una lista de opciones
- unique: el valor no se puede repetir
- default: valor por defecto
- db_column: nombre de la columna en la base de datos
- verbose_name: nombre legible del campo
- help_text: texto de ayuda del campo
- auto_now_add: pone la fecha automáticamente al crear el registro
- max_digits: número total de dígitos de un DecimalField
- decimal_places: cuántos de esos dígitos son decimales
- on_delete: qué pasa si se borra el registro relacionado (CASCADE lo borra también, SET_NULL lo deja vacío)
- related_name: nombre para acceder a la relación desde el otro modelo
- through: indica la tabla intermedia de una relación ManyToMany

CÓDIGO QUE NO SE VIO EN CLASE

En generar_datos.py, seed_limpieza.py y repartir_aseos.py (carpeta limpieza/management/commands):
- BaseCommand y handle(): clase de Django para crear comandos propios; handle() es lo que se ejecuta al lanzar el comando
- add_arguments: crea la opción --number del comando seed_limpieza
- Faker("es_ES"): crea datos falsos en español; fake.unique evita que se repitan
- random.choice: elige un elemento al azar de una lista
- random.sample(lista, n): elige n elementos distintos de una lista
- .add(): añade registros a una relación ManyToMany
- Decimal: tipo de número que usa Django en los DecimalField
- timedelta: sirve para sumar tiempo a una fecha u hora
- datetime.combine: junta una fecha y una hora en un solo datetime
- Seed.seeder() y add_entity(Modelo, n): preparan en django-seed la creación de n registros de un modelo
- seeder.orders: lista de pedidos del seeder; la uso para quitar las relaciones ManyToMany con tabla intermedia, que django-seed no sabe rellenar
- enumerate: recorre una lista dando también el número de cada elemento
- i % n (módulo): resto de dividir i entre n; sirve para repartir los aseos rotando entre los limpiadores
- get_or_create: busca el registro y, si no existe, lo crea

COMANDOS

- seed_limpieza: rellena las tablas con el seeder
- generar_datos: crea 10 datos de cada modelo con Faker (con una estructura fija para que todas las URLs de la tarea 2 den resultados)
- repartir_aseos: reparte los aseos de cada turno entre los limpiadores del cuadrante

TAREA 2: URLS, VIEWS Y QUERYSETS

Cómo probarlo después de descargarlo de git:
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py loaddata limpieza/fixtures/datos.json
- python manage.py runserver
- Abrir http://127.0.0.1:8000/ . El índice tiene enlaces a todas las URLs y a las páginas de error.

Modo producción:
- En mysite/settings.py está DEBUG = False y ALLOWED_HOSTS = ['127.0.0.1', 'localhost'].
- En producción las páginas de error personalizadas solo se ven con DEBUG = False.
- Con DEBUG = False Django no sirve los archivos estáticos con runserver, por eso el CSS está escrito dentro de principal.html y no en un archivo css. Por lo mismo, el panel /admin se ve sin estilos (no se usa en esta tarea).

Plantillas (carpeta limpieza/templates):
- principal.html: plantilla base con {% block contenido %}. Todas las páginas la heredan con {% extends %}.
- partes/: plantillas pequeñas que se reutilizan con {% include %} para mostrar todos los campos de un modelo (limpiador, perfil, centro, aseo, turno, producto). Así en todas las páginas se muestra siempre toda la información de los modelos relacionados.
- centro/, aseo/, registro/, turno/, limpiador/, producto/, inventario/: una plantilla por cada URL.
- errores/: 400.html, 403.html, 404.html y 500.html.

URLS (todas en limpieza/urls.py, vistas en limpieza/views.py)

URL 1: centros/listar (name lista_centros, vista lista_centros, plantilla centro/lista.html)
- Muestra todos los centros comerciales con su jefe de equipo, sus aseos, sus turnos y sus productos.
- QuerySet: Centro.objects.select_related("jefe_equipo").prefetch_related("aseos", "turnos_del_centro", "productos").all()
- Datos entre tablas: OneToOne (jefe_equipo), ManyToOne inversa con related_name (aseos, turnos_del_centro) y ManyToMany con tabla intermedia (productos).

URL 2: centros/<int:id_centro>/ (name dame_centro, vista dame_centro, plantilla centro/centro.html)
- Muestra un centro concreto con toda su información relacionada.
- QuerySet: select_related("jefe_equipo") y prefetch_related(Prefetch("aseos"), Prefetch("turnos_del_centro"), "productos") y get(id=id_centro)
- Cumple: parámetro entero, get, relación reversa con Prefetch y related_name.

URL 3: centros/<int:id_centro>/aseos/<str:tipo_aseo>/ (name dame_aseos_centro_tipo, vista dame_aseos_centro_tipo, plantilla aseo/lista.html)
- Muestra los aseos de un centro de un tipo concreto (MUJERES, HOMBRES, ADAPTADO o FAMILIA), de la planta más alta a la más baja, con su centro y sus limpiezas.
- QuerySet: filter(centro=id_centro).filter(tipo=tipo_aseo).order_by("-planta")
- Cumple: URL con dos parámetros (uno entero y uno de texto), filtros con AND encadenados, order_by descendente, ManyToOne y relación reversa (limpiezas_aseo).

URL 4: limpiezas/estado/<str:estado>/ (name dame_limpiezas_estado, vista dame_limpiezas_estado, plantilla registro/lista.html)
- Es el registro de quién ha limpiado qué aseo. Muestra las limpiezas que estén en el estado indicado o con incidencia, de la más reciente a la más antigua.
- QuerySet: filter(Q(estado=estado) | Q(estado="INCIDENCIA")).order_by("-hora_inicio")
- Muestra el aseo y su centro, el cuadrante con su limpiador y su turno, el fichaje y los productos usados.
- Cumple: filtro con OR (Q), order_by, ManyToOne, OneToOne (fichaje) y ManyToMany (productos_usados).

URL 5: turnos/<int:anyo>/<int:mes>/ (name dame_turnos_fecha, vista dame_turnos_fecha, plantilla turno/lista.html)
- Es el cuadrante de un mes: muestra los turnos de un año y un mes con su centro y los limpiadores que trabajan en cada uno.
- QuerySet: filter(fecha__year=anyo, fecha__month=mes).order_by("fecha", "hora_inicio")
- Cumple: URL con dos parámetros enteros, filtro con AND (con coma), ManyToOne y ManyToMany con tabla intermedia (Cuadrante, con sus datos extra).

URL 6: limpiadores/<int:id_limpiador>/ (name dame_limpiador, vista dame_limpiador, plantilla limpiador/limpiador.html)
- Muestra un limpiador con su perfil, el centro del que es jefe de equipo y los turnos en los que trabaja.
- QuerySet: select_related("perfil", "centro_a_cargo").prefetch_related("turnos_asignados").get(id=id_limpiador)
- Cumple: OneToOne y OneToOne inversa (related_name), ManyToMany.

URL 7: aseos/<int:id_aseo>/ultimo-limpiador/ (name ultimo_limpiador_aseo, vista dame_ultimo_limpiador_aseo, plantillas limpiador/ultimo.html)
- Muestra el último limpiador que limpió un aseo.
- QuerySet: filter(cuadrantes_limpiador__limpiezas_cuadrante__aseo=id_aseo).order_by("-cuadrantes_limpiador__limpiezas_cuadrante__hora_inicio")[:1].get()
- Cumple: tablas intermedias, relación reversa, order_by, límite con [:1] y get().

URL 8: limpiadores-sin-turnos/ (name limpiadores_sin_turnos, vista limpiadores_sin_turnos, plantilla limpiador/lista.html)
- Muestra los limpiadores que nunca han tenido un turno.
- QuerySet: filter(cuadrantes_limpiador=None)
- Cumple: re_path con expresión regular (r'^limpiadores-sin-turnos/$') y filtro con None en una tabla intermedia (Cuadrante).

URL 9: productos/precios/ (name dame_precios_productos, vista dame_precios_productos, plantilla producto/precios.html)
- Muestra la media, el máximo y el mínimo del precio de los productos y la lista de productos ordenada por precio.
- QuerySet: Producto.objects.aggregate(Avg("precio_unidad"), Max("precio_unidad"), Min("precio_unidad"))
- Cumple: aggregate y order_by.

URL 10: centros/<int:id_centro>/inventario/ (name dame_inventario_centro, vista dame_inventario_centro, plantilla inventario/inventario.html)
- Muestra el inventario de un centro con la cantidad de cada producto y tres totales: unidades, número de productos y productos que hay que reponer.
- QuerySet: Inventario.objects.filter(centro=id_centro).aggregate(total_unidades=Sum("cantidad_actual"), total_productos=Count("id"), productos_a_reponer=Count("id", filter=Q(necesita_reposicion=True)))
- Cumple: URL con un filtro dentro de un aggregate (parte de investigación, explicada más abajo), tabla intermedia Inventario, ManyToOne y OneToOne (jefe del centro).

Index: la URL raíz (name index) abre index.html con los enlaces a las 10 URLs y a las pruebas de las páginas de error.

PÁGINAS DE ERROR

- Hay una plantilla y una vista para cada error: 400 (petición mal formada), 403 (permiso denegado), 404 (página no encontrada) y 500 (error interno).
- Las vistas son mi_error_400, mi_error_403, mi_error_404 y mi_error_500 en views.py y se asocian a handler400, handler403, handler404 y handler500 en mysite/urls.py.
- Cómo probarlas: 404 escribiendo una URL que no existe; 500 con /centros/999/ (el centro no existe, get() da error); 400 con un Host no permitido (por ejemplo, una petición a otro dominio distinto de localhost y 127.0.0.1). Además, en el índice hay enlaces directos a /prueba-error/400/, /prueba-error/403/, /prueba-error/404/ y /prueba-error/500/ que llevan a esas mismas vistas.

REQUISITOS DE LA TAREA 2 Y DÓNDE SE CUMPLEN

- 10 URLs con sus vistas, QuerySet y plantillas: URL 1 a URL 10.
- Una rama por cada URL fusionada con la rama de la tarea: ramas url_01 a url_10, fusionadas en Tarea_URLs_Views, y esta fusionada con main.
- Datos entre tablas ManyToMany, OneToOne y ManyToOne: URLs 1, 2, 4, 5 y 6 (ver cada URL).
- Comentario en cada vista: está en limpieza/views.py, encima de cada función.
- Todas las URLs detalladas en este README: ver apartado URLS.
- Página de error personalizada para los 4 errores: ver PÁGINAS DE ERROR.
- Las URLs funcionan y muestran resultados: comprobado con los datos del fixture; todos los enlaces del índice devuelven datos.
- Se muestra toda la información de los modelos relacionados: con las plantillas de la carpeta partes/.
- Querys optimizadas: select_related para OneToOne y ManyToOne, prefetch_related para ManyToMany y relaciones inversas. Cada URL hace entre 1 y 4 consultas a la base de datos, aunque muestre muchos datos.
- SQL comentada en cada QuerySet: está en el comentario de cada vista.
- re_path: URL 8. Dos parámetros: URL 3 y URL 5. Parámetro entero: URLs 2, 3, 5, 6, 7 y 10. Parámetro de texto: URLs 3 y 4.
- Filtros con AND: URLs 3 y 5. Filtro con OR: URL 4. aggregate: URLs 9 y 10. Relación reversa: URLs 1, 2, 3, 5 y 7. order_by: URLs 3, 4, 5, 7, 9 y 10. Límite: URL 7. Filtro con None en una tabla intermedia: URL 8.
- URL con filtro de aggregate: URL 10.
- Index desde el que se accede a todas las URLs: URL raíz.
- Archivos que no se suben a git: .gitignore (db.sqlite3, venv, __pycache__...).
- Fixture con los datos para las pruebas: limpieza/fixtures/datos.json
- Proyecto en modo producción: DEBUG = False.
- Funciona al descargarlo de git: probado en una carpeta nueva con migrate, loaddata y runserver.

CÓDIGO NUEVO QUE NO SE VIO EN CLASE (TAREA 2)

- ALLOWED_HOSTS (settings.py): lista de direcciones desde las que Django acepta peticiones. Con DEBUG = False es obligatorio rellenarla, si no Django rechaza todas las peticiones con un error 400. Se ponen 127.0.0.1 y localhost.
- Doble barra baja dentro de select_related y prefetch_related (por ejemplo "aseo__centro" o "cuadrantes_turno__limpiador"): sirve para seguir una relación dentro de otra, igual que en los filter (prestamo__libro). Así se traen de golpe los datos de varios modelos encadenados y se evita hacer una consulta por cada elemento.
- Sum y Count (django.db.models): igual que Avg, Max y Min pero para sumar y para contar filas. Se usan dentro de aggregate.
- Nombre dentro de aggregate (total_unidades=Sum(...)): permite poner nosotros el nombre de la clave en el diccionario resultado, en vez del nombre automático (cantidad_actual__sum). Es necesario cuando hay dos Count sobre el mismo campo.
- Count("id", filter=Q(necesita_reposicion=True)): el parámetro filter hace que Count solo cuente las filas que cumplen la condición. En SQL sería COUNT(CASE WHEN necesita_reposicion = 1 THEN id END). Es la parte de investigación del aggregate con filtro.
- order_by("fecha", "hora_inicio"): ordena por varios campos; si dos filas tienen la misma fecha, desempata por la hora.
- round(valor, 2): función de Python que redondea a 2 decimales.
- {% include 'partes/aseo.html' with aseo=limpieza.aseo %}: el with permite darle a la plantilla incluida una variable con el nombre que espera (aseo) a partir de otra (limpieza.aseo).
- Archivos del comando generar_datos.py: date(2026, 11, 5) crea una fecha; las listas con corchetes y dos puntos (limpiadores[:6], centros[1:4]) cogen un trozo de la lista; el if y el else normales de Python; i % 6 es el resto de dividir i entre 6; enumerate da el número de vuelta junto a cada elemento; "HECHA" in ("HECHA", "INCIDENCIA") comprueba si un valor está en la lista.
- El CSS dentro de la etiqueta style de principal.html es HTML normal.

BACKUP

La base de datos (db.sqlite3) está en el .gitignore. La copia de seguridad, con los datos para probar todas las URLs, está en limpieza/fixtures/datos.json
