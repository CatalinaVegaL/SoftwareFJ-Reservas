"""
Módulo: excepciones.py
Descripción: Define la jerarquía de excepciones personalizadas para el Sistema
Integral de Gestión de Clientes, Servicios y Reservas de Software FJ.
Curso: Programación (213023) - UNAD
"""


class ErrorSistemaFJ(Exception):
    """Excepción base para todos los errores controlados de Software FJ."""

    def __init__(self, mensaje: str, codigo_error: str = "ERR-000"):
        self.codigo_error = codigo_error
        self.mensaje = mensaje
        super().__init__(f"[{self.codigo_error}] {self.mensaje}")


class DatosInvalidosError(ErrorSistemaFJ):
    """Se lanza cuando los datos ingresados por un cliente o servicio no cumplen validación."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-101")


class ParametroFaltanteError(ErrorSistemaFJ):
    """Se lanza cuando falta un parámetro obligatorio en una operación."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-102")


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Se lanza cuando se intenta reservar un servicio inactivo o sin cupo/stock."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-201")


class ReservaInvalidaError(ErrorSistemaFJ):
    """Se lanza cuando una reserva tiene duración inválida, cliente nulo o conflicto."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-301")


class OperacionNoPermitidaError(ErrorSistemaFJ):
    """Se lanza al intentar cambiar de estado una reserva de forma ilegal (ej. cancelar una finalizada)."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-302")


class CalculoInconsistenteError(ErrorSistemaFJ):
    """Se lanza si el cálculo de costos, impuestos o descuentos arroja valores negativos o incoherentes."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo_error="ERR-401")