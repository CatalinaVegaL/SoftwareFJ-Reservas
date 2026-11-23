"""
Módulo: gestor.py
Descripción: Administra las listas internas de clientes, servicios y reservas
sin uso de bases de datos. Implementa el sistema de logging y el manejo
avanzado de excepciones (try/except, else, finally y encadenamiento).
Empresa: Software FJ - UNAD (213023)
"""

import logging
from typing import List, Optional
from excepciones import (
    ErrorSistemaFJ,
    DatosInvalidosError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
)
from modelos import Cliente, Servicio, Reserva


def configurar_logger(nombre_archivo: str = "sistema_fj.log") -> logging.Logger:
    """Configura el registro de eventos y errores en archivo y consola."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita duplicar manejadores si se llama varias veces
    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Manejador de archivo para persistir todos los eventos y errores
        manejador_archivo = logging.FileHandler(nombre_archivo, mode="w", encoding="utf-8")
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

        # Manejador de consola para seguimiento en tiempo real
        manejador_consola = logging.StreamHandler()
        manejador_consola.setFormatter(formato)
        logger.addHandler(manejador_consola)

    return logger


class GestorSoftwareFJ:
    """Controlador principal en memoria para clientes, servicios y reservas."""

    def __init__(self, archivo_log: str = "sistema_fj.log"):
        # Estructuras en memoria (sin base de datos)
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._logger = configurar_logger(archivo_log)
        self._logger.info("=== INICIO DEL SISTEMA INTEGRAL SOFTWARE FJ (MODO EN MEMORIA) ===")

    @property
    def clientes(self) -> List[Cliente]:
        return list(self._clientes)

    @property
    def servicios(self) -> List[Servicio]:
        return list(self._servicios)

    @property
    def reservas(self) -> List[Reserva]:
        return list(self._reservas)

    def registrar_cliente(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> Optional[Cliente]:
        """
        Registra un nuevo cliente validando duplicados y formato.
        Implementa bloques try / except / else / finally.
        """
        nuevo_cliente = None
        try:
            # Verificar que no exista un cliente con el mismo ID
            if any(c.id == str(id_cliente).strip() for c in self._clientes):
                raise DatosInvalidosError(f"Ya existe un cliente registrado con el ID '{id_cliente}'.")

            nuevo_cliente = Cliente(id_cliente, nombre, correo, telefono)

        except ErrorSistemaFJ as err:
            # Captura errores de validación propios del dominio
            self._logger.error(f"Fallo al registrar cliente '{id_cliente}': {err}")
            return None
        except Exception as err_inesperado:
            # Encadenamiento de excepción ante cualquier fallo no previsto
            error_encadenado = DatosInvalidosError(f"Error inesperado procesando datos del cliente '{id_cliente}'.")
            self._logger.critical(f"Excepción encadenada en cliente: {error_encadenado} | Causa: {err_inesperado}")
            return None
        else:
            # Se ejecuta únicamente si el bloque try no lanzó excepciones
            self._clientes.append(nuevo_cliente)
            self._logger.info(f"EXITO - Cliente registrado: {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente
        finally:
            # Se ejecuta siempre para dejar traza de auditoría de cierre de operación
            self._logger.info(f"AUDITORIA - Finalizó intento de registro para cliente ID='{id_cliente}'.")

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """
        Agrega un servicio especializado al catálogo en memoria.
        Implementa try / except / else.
        """
        try:
            if not isinstance(servicio, Servicio):
                raise DatosInvalidosError("El objeto proporcionado no es una subclase válida de Servicio.")
            if any(s.id == servicio.id for s in self._servicios):
                raise DatosInvalidosError(f"El servicio con ID '{servicio.id}' ya se encuentra catalogado.")
            servicio.validar()
        except ErrorSistemaFJ as err:
            self._logger.error(f"Fallo al catalogar servicio: {err}")
            return False
        else:
            self._servicios.append(servicio)
            self._logger.info(f"EXITO - Servicio catalogado: {servicio.obtener_resumen()}")
            return True

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        """Busca un cliente por ID o lanza excepción personalizada."""
        for cliente in self._clientes:
            if cliente.id == id_cliente:
                return cliente
        raise DatosInvalidosError(f"No se encontró ningún cliente con ID '{id_cliente}'.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        """Busca un servicio por ID o lanza excepción personalizada."""
        for servicio in self._servicios:
            if servicio.id == id_servicio:
                return servicio
        raise ServicioNoDisponibleError(f"No existe ningún servicio con ID '{id_servicio}' en el catálogo.")

    def _crear_reserva_interna(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion_horas: int,
        descuento: float,
        recargo_urgencia: Optional[float],
    ) -> Reserva:
        """Método interno que demuestra encadenamiento explícito de excepciones (raise ... from ...)."""
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            return Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion_horas=duracion_horas,
                descuento=descuento,
                recargo_urgencia=recargo_urgencia,
            )
        except ErrorSistemaFJ as causa_original:
            # Encadena la excepción original dentro de ReservaInvalidaError conservando la traza
            raise ReservaInvalidaError(
                f"Imposible construir la reserva '{id_reserva}' para cliente '{id_cliente}' y servicio '{id_servicio}'."
            ) from causa_original

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion_horas: int,
        descuento: float = 0.0,
        recargo_urgencia: Optional[float] = None,
        confirmar_automaticamente: bool = False,
    ) -> Optional[Reserva]:
        """
        Gestiona la creación y opcionalmente la confirmación de una reserva.
        Implementa try / except / else / finally y captura excepciones encadenadas.
        """
        reserva_creada = None
        try:
            if any(r.id == str(id_reserva).strip() for r in self._reservas):
                raise ReservaInvalidaError(f"El código de reserva '{id_reserva}' ya existe en el sistema.")

            reserva_creada = self._crear_reserva_interna(
                id_reserva, id_cliente, id_servicio, duracion_horas, descuento, recargo_urgencia
            )

            if confirmar_automaticamente:
                reserva_creada.confirmar()

        except ReservaInvalidaError as err:
            causa = f" | Causa raíz: {err.__cause__}" if err.__cause__ else ""
            self._logger.error(f"Fallo en reserva '{id_reserva}': {err}{causa}")
            return None
        except ErrorSistemaFJ as err:
            self._logger.error(f"Error de negocio en reserva '{id_reserva}': {err}")
            return None
        else:
            self._reservas.append(reserva_creada)
            self._logger.info(f"EXITO - Reserva registrada: {reserva_creada.obtener_resumen()}")
            return reserva_creada
        finally:
            self._logger.info(f"AUDITORIA - Transacción de reserva '{id_reserva}' concluida sin interrupciones.")

    def cambiar_estado_reserva(self, id_reserva: str, accion: str) -> bool:
        """
        Ejecuta confirmar, cancelar o procesar sobre una reserva existente.
        Implementa try / except / else / finally.
        """
        try:
            reserva = next((r for r in self._reservas if r.id == id_reserva), None)
            if reserva is None:
                raise ReservaInvalidaError(f"La reserva '{id_reserva}' no existe.")

            accion_norm = accion.strip().upper()
            if accion_norm == "CONFIRMAR":
                reserva.confirmar()
            elif accion_norm == "CANCELAR":
                reserva.cancelar()
            elif accion_norm == "PROCESAR":
                reserva.procesar()
            else:
                raise OperacionNoPermitidaError(f"Acción desconocida sobre reserva: '{accion}'.")

        except ErrorSistemaFJ as err:
            self._logger.error(f"Fallo al ejecutar '{accion}' en reserva '{id_reserva}': {err}")
            return False
        else:
            self._logger.info(f"EXITO - Reserva '{id_reserva}' actualizada mediante acción '{accion.upper()}'.")
            return True
        finally:
            self._logger.info(f"AUDITORIA - Revisión de estado finalizada para reserva '{id_reserva}'.")

    def generar_reporte_consola(self) -> None:
        """Imprime el estado consolidado en memoria al finalizar las simulaciones."""
        print("\n" + "=" * 75)
        print("REPORTE FINAL EN MEMORIA - SOFTWARE FJ (SIN BASE DE DATOS)")
        print("=" * 75)
        print(f"Total Clientes activos : {len(self._clientes)}")
        for c in self._clientes:
            print(f"  - {c.obtener_resumen()}")

        print(f"\nTotal Servicios        : {len(self._servicios)}")
        for s in self._servicios:
            print(f"  - {s.obtener_resumen()}")

        print(f"\nTotal Reservas         : {len(self._reservas)}")
        for r in self._reservas:
            print(f"  - {r.obtener_resumen()}")
        print("=" * 75 + "\n")