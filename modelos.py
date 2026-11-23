"""
Módulo: modelos.py
Descripción: Implementa la arquitectura Orientada a Objetos (clases abstractas,
herencia, polimorfismo, encapsulación y sobrecarga de métodos) sin uso de BD.
Empresa: Software FJ
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from excepciones import (
    DatosInvalidosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoInconsistenteError,
)


class Entidad(ABC):
    """Clase abstracta base que representa cualquier entidad identificable del sistema."""

    def __init__(self, id_entidad: str):
        if not id_entidad or not str(id_entidad).strip():
            raise ParametroFaltanteError("El identificador de la entidad no puede estar vacío.")
        self._id = str(id_entidad).strip()
        self._fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        """Retorna el identificador único encapsulado."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha y hora de creación de la entidad."""
        return self._fecha_creacion

    @abstractmethod
    def validar(self) -> bool:
        """Método abstracto que obliga a las subclases a validar su estado interno."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método abstracto para representar textualmente la entidad."""
        pass


class Cliente(Entidad):
    """Representa un cliente de Software FJ con encapsulación y validaciones estrictas."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.validar()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise DatosInvalidosError(f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise DatosInvalidosError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        limpio = str(valor).strip()
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatosInvalidosError(f"Teléfono inválido: '{valor}'. Debe contener al menos 7 dígitos numéricos.")
        self._telefono = limpio

    def validar(self) -> bool:
        return bool(self._id and self._nombre and self._correo and self._telefono)

    def obtener_resumen(self) -> str:
        return f"Cliente [{self._id}] - {self._nombre} | Email: {self._correo} | Tel: {self._telefono}"


class Servicio(Entidad, ABC):
    """Clase abstracta que modela los servicios ofrecidos por Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True):
        super().__init__(id_servicio)
        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if tarifa_base is None or tarifa_base <= 0:
            raise DatosInvalidosError(f"La tarifa base debe ser mayor a cero. Valor recibido: {tarifa_base}")

        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def calcular_costo_base(self, duracion_horas: int) -> float:
        """Método polimórfico que cada servicio especializado implementa según sus reglas."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Método polimórfico que describe las características técnicas del servicio."""
        pass

    def calcular_total(
        self,
        duracion_horas: int,
        porcentaje_impuesto: float = 0.19,
        descuento: float = 0.0,
        recargo_urgencia: Optional[float] = None,
    ) -> float:
        """
        Método sobrecargado funcionalmente mediante parámetros opcionales para calcular
        el costo final con impuestos (IVA 19% por defecto), descuentos y recargos opcionales.
        """
        if duracion_horas <= 0:
            raise ReservaInvalidaError("La duración en horas debe ser mayor a cero.")
        if porcentaje_impuesto < 0 or descuento < 0:
            raise CalculoInconsistenteError("Los impuestos y descuentos no pueden ser negativos.")

        subtotal = self.calcular_costo_base(duracion_horas)

        if recargo_urgencia is not None:
            if recargo_urgencia < 0:
                raise CalculoInconsistenteError("El recargo de urgencia no puede ser negativo.")
            subtotal += recargo_urgencia

        if descuento > subtotal:
            raise CalculoInconsistenteError(
                f"El descuento (${descuento:,.2f}) no puede superar el subtotal (${subtotal:,.2f})."
            )

        base_gravable = subtotal - descuento
        total = base_gravable * (1 + porcentaje_impuesto)

        if total < 0:
            raise CalculoInconsistenteError("El cálculo final arrojó un valor negativo inconsistente.")

        return round(total, 2)

    def validar(self) -> bool:
        return self._tarifa_base > 0 and bool(self._nombre)

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio [{self._id}] {self._nombre} (${self._tarifa_base:,.2f}/h) - {estado}"


class ReservaSala(Servicio):
    """Servicio especializado 1: Reserva de salas tecnológicas y de conferencias."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad: int, tiene_videoconferencia: bool = True, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if capacidad <= 0:
            raise DatosInvalidosError("La capacidad de la sala debe ser mayor a 0 personas.")
        self._capacidad = capacidad
        self._tiene_videoconferencia = tiene_videoconferencia

    def calcular_costo_base(self, duracion_horas: int) -> float:
        costo = self._tarifa_base * duracion_horas
        if self._tiene_videoconferencia:
            costo += 25000.0  # Cargo fijo por equipo audiovisual
        return costo

    def describir_servicio(self) -> str:
        av = "con equipo de videoconferencia" if self._tiene_videoconferencia else "estándar"
        return f"Sala '{self._nombre}' (Capacidad: {self._capacidad} personas, {av})"


class AlquilerEquipo(Servicio):
    """Servicio especializado 2: Alquiler de estaciones de trabajo y hardware especializado."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, cantidad_unidades: int, especificaciones: str, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if cantidad_unidades <= 0:
            raise DatosInvalidosError("Debe alquilar al menos 1 unidad de equipo.")
        if not especificaciones or not especificaciones.strip():
            raise ParametroFaltanteError("Debe especificar las características técnicas del equipo.")
        self._cantidad_unidades = cantidad_unidades
        self._especificaciones = especificaciones.strip()

    def calcular_costo_base(self, duracion_horas: int) -> float:
        # Incluye seguro técnico del 10% sobre el alquiler por unidad
        return (self._tarifa_base * duracion_horas * self._cantidad_unidades) * 1.10

    def describir_servicio(self) -> str:
        return f"Alquiler de {self._cantidad_unidades}x '{self._nombre}' [{self._especificaciones}]"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado 3: Consultoría en arquitectura de software y ciberseguridad."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, area_tecnica: str, nivel_senior: bool = True, disponible: bool = True):
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not area_tecnica or not area_tecnica.strip():
            raise ParametroFaltanteError("El área técnica de la asesoría es obligatoria.")
        self._area_tecnica = area_tecnica.strip()
        self._nivel_senior = nivel_senior

    def calcular_costo_base(self, duracion_horas: int) -> float:
        factor = 1.35 if self._nivel_senior else 1.0
        return self._tarifa_base * duracion_horas * factor

    def describir_servicio(self) -> str:
        nivel = "Consultor Senior" if self._nivel_senior else "Consultor Semi-Senior"
        return f"Asesoría en {self._area_tecnica} ({nivel}) - {self._nombre}"


class Reserva(Entidad):
    """Integra Cliente, Servicio, duración, estado y reglas de negocio de reserva."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento: float = 0.0,
        recargo_urgencia: Optional[float] = None,
    ):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere una instancia válida de Cliente para crear la reserva.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se requiere una instancia válida de Servicio para crear la reserva.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no se encuentra disponible actualmente.")
        if duracion_horas <= 0 or duracion_horas > 720:
            raise ReservaInvalidaError(f"Duración inválida ({duracion_horas}h). Debe estar entre 1 y 720 horas.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = int(duracion_horas)
        self._estado = "PENDIENTE"
        self._costo_total = self._servicio.calcular_total(
            duracion_horas=self._duracion_horas,
            descuento=descuento,
            recargo_urgencia=recargo_urgencia,
        )
        self.validar()

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    def confirmar(self) -> None:
        """Confirma una reserva pendiente y bloquea la disponibilidad del servicio."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado '{self._estado}'.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' ya fue ocupado por otra reserva.")
        self._estado = "CONFIRMADA"
        self._servicio.disponible = False

    def cancelar(self) -> None:
        """Cancela una reserva activa y libera el servicio asociado."""
        if self._estado == "PROCESADA":
            raise OperacionNoPermitidaError("No es posible cancelar una reserva que ya fue procesada/facturada.")
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
        self._estado = "CANCELADA"
        self._servicio.disponible = True

    def procesar(self) -> None:
        """Procesa y cierra una reserva previamente confirmada."""
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual: '{self._estado}'."
            )
        self._estado = "PROCESADA"
        self._servicio.disponible = True

    def validar(self) -> bool:
        return self._estado in self.ESTADOS_VALIDOS and self._costo_total >= 0

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self._id}] | Estado: {self._estado} | "
            f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.describir_servicio()} | "
            f"Duración: {self._duracion_horas}h | Total: ${self._costo_total:,.2f}"
        )