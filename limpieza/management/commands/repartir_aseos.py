from django.core.management.base import BaseCommand

from limpieza.models import Turno, Limpieza


class Command(BaseCommand):
    help = "Reparte los aseos de cada centro entre los limpiadores que trabajan en cada turno"

    def handle(self, *args, **options):
        creadas = 0
        for turno in Turno.objects.all():
            cuadrantes = list(turno.cuadrantes_turno.all())   # limpiadores de ese turno
            aseos = list(turno.centro.aseos.all())            # aseos del centro del turno
            if not cuadrantes or not aseos:
                continue
            # enumerate da el número de vuelta (i) y el aseo. El resto de dividir (i % n)
            # va rotando entre los limpiadores: con 2 limpiadores le toca la mitad a cada
            # uno, con 3 un tercio, y así sucesivamente.
            for i, aseo in enumerate(aseos):
                cuadrante = cuadrantes[i % len(cuadrantes)]
                # get_or_create no duplica la limpieza si ya existía
                _, nueva = Limpieza.objects.get_or_create(cuadrante=cuadrante, aseo=aseo)
                creadas += nueva
        self.stdout.write(self.style.SUCCESS(f"Aseos repartidos: {creadas} limpiezas nuevas."))
