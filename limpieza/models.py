from datetime import date

from django.db import models


class Limpiador(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    dni = models.CharField(max_length=9, unique=True)
    email = models.EmailField(unique=True, help_text="Correo del trabajador")
    telefono = models.CharField(max_length=20, blank=True, db_column="telefono_contacto")
    fecha_alta = models.DateField(default=date.today)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class PerfilLimpiador(models.Model):
    TALLAS = [
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
    ]

    # Relación 1:1 -> cada limpiador tiene un único perfil y cada perfil es de un limpiador
    limpiador = models.OneToOneField(Limpiador, on_delete=models.CASCADE, related_name="perfil")
    observaciones = models.TextField(blank=True)
    anios_experiencia = models.PositiveIntegerField(default=0, verbose_name="Años de experiencia")
    talla_guantes = models.CharField(max_length=2, choices=TALLAS, default="M")
    foto_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.limpiador.nombre}"


class Centro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    ciudad = models.CharField(max_length=60, default="Sevilla")
    superficie_m2 = models.FloatField(help_text="Superficie total en metros cuadrados")
    fecha_apertura = models.DateField()
    # Relación 1:1 -> un limpiador es jefe de equipo de como mucho un centro
    jefe_equipo = models.OneToOneField(
        Limpiador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="centro_a_cargo",
    )
    # Relación N:M con tabla intermedia con atributos extra (modelo Inventario)
    productos = models.ManyToManyField("Producto", through="Inventario", related_name="centros")

    def __str__(self):
        return self.nombre


class Aseo(models.Model):
    TIPOS = [
        ("MUJERES", "Mujeres"),
        ("HOMBRES", "Hombres"),
        ("ADAPTADO", "Adaptado"),
        ("FAMILIA", "Familia"),
    ]

    codigo = models.CharField(max_length=10)
    planta = models.IntegerField(help_text="0 = planta baja, número negativo = sótano")
    tipo = models.CharField(max_length=10, choices=TIPOS, default="MUJERES")
    accesible = models.BooleanField(default=False)
    num_cabinas = models.PositiveIntegerField(default=1, verbose_name="Número de cabinas")
    fecha_ultima_reforma = models.DateField(null=True, blank=True)
    # Relación N:1 -> un centro tiene muchos aseos
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name="aseos")

    def __str__(self):
        return f"Aseo {self.codigo} ({self.centro.nombre})"


class Turno(models.Model):
    TIPOS = [
        ("MANANA", "Mañana"),
        ("TARDE", "Tarde"),
        ("NOCHE", "Noche"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPOS, default="MANANA")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    notas = models.TextField(blank=True)
    # Relación N:1 -> un centro tiene muchos turnos
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name="turnos_del_centro")
    # Relación N:M con tabla intermedia con atributos extra (modelo Cuadrante)
    limpiadores = models.ManyToManyField(Limpiador, through="Cuadrante", related_name="turnos_asignados")

    def __str__(self):
        return f"Turno de {self.get_tipo_display()} del {self.fecha} en {self.centro.nombre}"


class Cuadrante(models.Model):
    """Tabla intermedia entre Turno y Limpiador: quién trabaja en cada turno."""

    limpiador = models.ForeignKey(Limpiador, on_delete=models.CASCADE, related_name="cuadrantes_limpiador")
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE, related_name="cuadrantes_turno")
    confirmado = models.BooleanField(default=False)
    horas_extra = models.FloatField(default=0)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.limpiador.nombre} - {self.turno}"


class Fichaje(models.Model):
    METODOS = [
        ("APP", "Aplicación"),
        ("TARJETA", "Tarjeta"),
        ("MANUAL", "Manual"),
    ]

    # Relación 1:1 -> cada entrada del cuadrante tiene como mucho un fichaje
    cuadrante = models.OneToOneField(Cuadrante, on_delete=models.CASCADE, related_name="fichaje")
    hora_entrada = models.DateTimeField()
    hora_salida = models.DateTimeField(null=True, blank=True)
    metodo = models.CharField(max_length=10, choices=METODOS, default="APP")
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Fichaje de {self.cuadrante.limpiador.nombre} ({self.hora_entrada})"


class Producto(models.Model):
    CATEGORIAS = [
        ("PAPEL", "Papel"),
        ("QUIMICO", "Producto químico"),
        ("JABON", "Jabón"),
        ("PROTECCION", "Protección"),
        ("UTENSILIO", "Utensilio"),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=12, choices=CATEGORIAS)
    unidad_medida = models.CharField(max_length=20, default="unidades")
    precio_unidad = models.DecimalField(max_digits=6, decimal_places=2)
    es_quimico = models.BooleanField(default=False)
    stock_minimo = models.PositiveIntegerField(default=5, help_text="Por debajo de esto hay que reponer")

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    """Tabla intermedia entre Centro y Producto: cuánto hay de cada producto en cada centro."""

    centro = models.ForeignKey(Centro, on_delete=models.CASCADE, related_name="inventarios_centro")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="inventarios_producto")
    cantidad_actual = models.PositiveIntegerField(default=0)
    ubicacion = models.CharField(max_length=60, blank=True, help_text="Dónde se guarda, por ejemplo Almacén -1")
    fecha_ultima_reposicion = models.DateField(null=True, blank=True)
    necesita_reposicion = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.producto.nombre} en {self.centro.nombre}: {self.cantidad_actual}"


class Limpieza(models.Model):
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("EN_CURSO", "En curso"),
        ("HECHA", "Hecha"),
        ("INCIDENCIA", "Con incidencia"),
    ]

    # Quién (y en qué turno) limpia qué aseo
    cuadrante = models.ForeignKey(Cuadrante, on_delete=models.CASCADE, related_name="limpiezas_cuadrante")
    aseo = models.ForeignKey(Aseo, on_delete=models.CASCADE, related_name="limpiezas_aseo")
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default="PENDIENTE")
    observaciones = models.TextField(blank=True)
    # Relación N:M simple -> productos gastados en esa limpieza
    productos_usados = models.ManyToManyField(Producto, blank=True, related_name="limpiezas")

    def __str__(self):
        return f"{self.aseo} - {self.cuadrante.limpiador.nombre} ({self.get_estado_display()})"
