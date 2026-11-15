import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from faker import Faker

from limpieza.models import (
    Limpiador,
    PerfilLimpiador,
    Centro,
    Aseo,
    Turno,
    Cuadrante,
    Fichaje,
    Producto,
    Inventario,
    Limpieza,
)


def elegir(opciones):
    """Devuelve un valor aleatorio de una lista de choices [(valor, etiqueta), ...]."""
    return random.choice([valor for valor, _ in opciones])


class Command(BaseCommand):
    # Texto que aparece con: python manage.py help generar_datos
    help = "Genera 10 registros aleatorios de cada modelo usando Faker"

    def handle(self, *args, **options):
        # 'es_ES' hace que los datos (nombres, textos...) salgan en español
        fake = Faker("es_ES")
        N = 10

        # 1) Limpiadores y sus perfiles (1:1)
        limpiadores = []
        for _ in range(N):
            limpiador = Limpiador.objects.create(
                nombre=fake.name(),
                dni=fake.unique.nif(),
                email=fake.unique.email(),
                telefono=fake.phone_number()[:20],
                fecha_alta=fake.date_between(start_date="-5y", end_date="today"),
                activo=random.choice([True, True, True, False]),
            )
            limpiadores.append(limpiador)
            PerfilLimpiador.objects.create(
                limpiador=limpiador,
                observaciones=fake.sentence(),
                anios_experiencia=random.randint(0, 25),
                talla_guantes=elegir(PerfilLimpiador.TALLAS),
                foto_url=fake.url(),
            )

        # 2) Centros comerciales. Los 5 primeros tienen jefe de equipo (1:1) y los demás no
        nombres_centros = ["Lagoh", "Torre Sevilla", "Nervión Plaza", "Los Arcos", "Plaza de Armas",
                           "Airesur", "Metromar", "Parque Corredor", "Centro Comercial Sur",
                           "Centro Comercial Norte"]
        centros = []
        for i in range(N):
            jefe = None
            if i < 5:
                jefe = limpiadores[i]
            centros.append(
                Centro.objects.create(
                    nombre=nombres_centros[i],
                    direccion=fake.street_address(),
                    ciudad="Sevilla",
                    superficie_m2=round(random.uniform(15000, 90000), 1),
                    fecha_apertura=fake.date_between(start_date="-20y", end_date="-1y"),
                    jefe_equipo=jefe,
                )
            )

        # 3) Aseos (N:1 con Centro). Los 6 primeros son del primer centro (Lagoh) y los 4
        #    primeros de esos 6 son uno de cada tipo. El resto se reparte entre los centros 2, 3 y 4
        aseos = []
        for i in range(N):
            if i < 6:
                centro = centros[0]
            else:
                # centros[1:4] es un trozo de la lista: desde la posición 1 hasta la 3
                centro = random.choice(centros[1:4])
            if i < 4:
                tipo = Aseo.TIPOS[i][0]
            else:
                tipo = elegir(Aseo.TIPOS)
            aseos.append(
                Aseo.objects.create(
                    codigo=f"A-{i + 1}",
                    planta=random.randint(-1, 3),
                    tipo=tipo,
                    accesible=random.choice([True, False]),
                    num_cabinas=random.randint(2, 12),
                    fecha_ultima_reforma=fake.date_between(start_date="-6y", end_date="today"),
                    centro=centro,
                )
            )

        # 4) Turnos (N:1 con Centro). Los 5 primeros son del primer centro. Cada tipo de turno
        #    tiene su horario. Todas las fechas son de noviembre de 2026
        horarios = {
            "MANANA": (time(7, 0), time(15, 0)),
            "TARDE": (time(15, 0), time(23, 0)),
            "NOCHE": (time(23, 0), time(7, 0)),
        }
        turnos = []
        for i in range(N):
            if i < 5:
                centro = centros[0]
            else:
                centro = random.choice(centros)
            tipo = elegir(Turno.TIPOS)
            turnos.append(
                Turno.objects.create(
                    tipo=tipo,
                    fecha=date(2026, 11, random.randint(1, 28)),
                    hora_inicio=horarios[tipo][0],
                    hora_fin=horarios[tipo][1],
                    notas=fake.sentence(),
                    centro=centro,
                )
            )

        # 5) Cuadrante (tabla intermedia Turno-Limpiador): 2 limpiadores en cada uno de los
        #    5 primeros turnos (10 filas). Solo se usan los 6 primeros limpiadores, así los
        #    otros 4 se quedan sin turnos
        cuadrantes = []
        for turno in turnos[:5]:
            for limpiador in random.sample(limpiadores[:6], 2):
                cuadrantes.append(
                    Cuadrante.objects.create(
                        limpiador=limpiador,
                        turno=turno,
                        confirmado=random.choice([True, False]),
                        horas_extra=random.choice([0, 0, 0.5, 1, 2]),
                        observaciones=fake.sentence(),
                    )
                )

        # 6) Fichajes (1:1 con Cuadrante): uno por cada entrada del cuadrante
        for cuadrante in cuadrantes:
            # datetime.combine junta una fecha y una hora en un solo datetime
            entrada = datetime.combine(cuadrante.turno.fecha, cuadrante.turno.hora_inicio)
            entrada += timedelta(minutes=random.randint(-5, 15))
            Fichaje.objects.create(
                cuadrante=cuadrante,
                hora_entrada=entrada,
                hora_salida=random.choice([None, entrada + timedelta(hours=8)]),
                metodo=elegir(Fichaje.METODOS),
                observaciones=fake.sentence(),
            )

        # 7) Productos
        datos_productos = [
            ("Papel higiénico", "PAPEL", "rollos", False),
            ("Papel secamanos", "PAPEL", "paquetes", False),
            ("Friegasuelos", "QUIMICO", "litros", True),
            ("Lejía", "QUIMICO", "litros", True),
            ("Limpiacristales", "QUIMICO", "litros", True),
            ("Jabón de manos", "JABON", "litros", False),
            ("Guantes de látex", "PROTECCION", "cajas", False),
            ("Bolsas de basura", "UTENSILIO", "rollos", False),
            ("Fregona", "UTENSILIO", "unidades", False),
            ("Ambientador", "QUIMICO", "unidades", True),
        ]
        productos = []
        for nombre, categoria, unidad, quimico in datos_productos:
            productos.append(
                Producto.objects.create(
                    nombre=nombre,
                    categoria=categoria,
                    unidad_medida=unidad,
                    # Decimal es el tipo de número que usa Django para los DecimalField
                    precio_unidad=Decimal(str(round(random.uniform(0.5, 25), 2))),
                    es_quimico=quimico,
                    stock_minimo=random.randint(3, 20),
                )
            )

        # 8) Inventario (tabla intermedia Centro-Producto): los 6 primeros productos están en
        #    el primer centro y los otros 4 en el segundo. Los productos en posición par
        #    tienen poco stock (hay que reponer) y los impares tienen de sobra
        for i, producto in enumerate(productos):
            if i < 6:
                centro = centros[0]
            else:
                centro = centros[1]
            if i % 2 == 0:
                cantidad = random.randint(0, producto.stock_minimo - 1)
            else:
                cantidad = producto.stock_minimo + random.randint(5, 40)
            Inventario.objects.create(
                centro=centro,
                producto=producto,
                cantidad_actual=cantidad,
                ubicacion=random.choice(["Almacén -1", "Almacén planta 0", "Cuarto de limpieza", "Almacén general"]),
                fecha_ultima_reposicion=fake.date_between(start_date="-3m", end_date="today"),
                necesita_reposicion=cantidad < producto.stock_minimo,
            )

        # 9) Limpiezas (quién limpia qué aseo): una por cada entrada del cuadrante. Los aseos
        #    son los 6 del primer centro, que es donde están todos los turnos del cuadrante.
        #    i % 6 y i % 4 van repitiendo las posiciones 0,1,2,3... para repartir aseos y estados
        for i, cuadrante in enumerate(cuadrantes):
            estado = Limpieza.ESTADOS[i % 4][0]
            inicio = datetime.combine(cuadrante.turno.fecha, cuadrante.turno.hora_inicio)
            inicio += timedelta(minutes=random.randint(10, 300))
            fin = None
            if estado in ("HECHA", "INCIDENCIA"):
                fin = inicio + timedelta(minutes=random.randint(10, 40))
            limpieza = Limpieza.objects.create(
                cuadrante=cuadrante,
                aseo=aseos[i % 6],
                hora_inicio=inicio,
                hora_fin=fin,
                estado=estado,
                observaciones=fake.sentence(),
            )
            limpieza.productos_usados.add(*random.sample(productos, 3))

        self.stdout.write(self.style.SUCCESS(f"Se han creado {N} registros de cada modelo."))
