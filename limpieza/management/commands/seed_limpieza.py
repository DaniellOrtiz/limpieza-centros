import random

from django.core.management.base import BaseCommand
from django_seed import Seed
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
    """Devuelve una función que elige al azar un valor de las choices de un campo."""
    return lambda inserted: random.choice([valor for valor, _ in opciones])


class Command(BaseCommand):
    # Seeder propio con django-seed. El comando "seed limpieza" normal falla con las
    # tablas intermedias (Cuadrante e Inventario), así que lo hacemos a mano, modelo por modelo.
    help = "Rellena todas las tablas con django-seed"

    def add_arguments(self, parser):
        # Opción --number: cuántos registros crear de cada modelo (por defecto 15)
        parser.add_argument("--number", type=int, default=15)

    def handle(self, *args, **options):
        n = options["number"]
        seeder = Seed.seeder()
        # Faker en español, solo para generar DNI válidos (con letra)
        fake = Faker("es_ES")

        # El orden importa: primero los modelos de los que dependen los demás.
        # El tercer parámetro es un diccionario para decidir cómo se rellena un campo
        # (aquí, para que los DNI sean válidos y las opciones de los choices salgan variadas).
        seeder.add_entity(Limpiador, n, {"dni": lambda x: fake.unique.nif()})
        seeder.add_entity(PerfilLimpiador, n, {"talla_guantes": elegir(PerfilLimpiador.TALLAS)})
        seeder.add_entity(Centro, n)
        seeder.add_entity(Aseo, n, {"tipo": elegir(Aseo.TIPOS)})
        seeder.add_entity(Turno, n, {"tipo": elegir(Turno.TIPOS)})
        seeder.add_entity(Cuadrante, n)
        seeder.add_entity(Fichaje, n, {"metodo": elegir(Fichaje.METODOS)})
        seeder.add_entity(Producto, n, {"categoria": elegir(Producto.CATEGORIAS)})
        seeder.add_entity(Inventario, n)
        seeder.add_entity(Limpieza, n, {"estado": elegir(Limpieza.ESTADOS)})

        # django-seed no sabe rellenar las relaciones ManyToMany que usan una tabla
        # intermedia (Cuadrante e Inventario ya se rellenan arriba), así que las quitamos
        for orden in seeder.orders:
            if orden["klass"] == Turno:
                orden["entity"].many_relations.pop("limpiadores", None)
            if orden["klass"] == Centro:
                orden["entity"].many_relations.pop("productos", None)

        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"Seeder terminado: {n} registros de cada modelo."))
