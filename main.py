"""
Módulo: main.py
Descripción: Punto de entrada principal del sistema Software FJ.
Ejecuta 12 simulaciones completas (casos válidos e inválidos) demostrando
estabilidad, polimorfismo, sobrecarga y manejo robusto de excepciones.
Autora: Lida Catalina Vega Lara
Curso: Programación (213023) - UNAD
"""

from excepciones import ErrorSistemaFJ
from modelos import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestor import GestorSoftwareFJ


def ejecutar_simulaciones():
    """Ejecuta las 12 operaciones simuladas requeridas por la guía."""
    sistema = GestorSoftwareFJ(archivo_log="sistema_fj.log")

    print("\n--- INICIANDO 12 SIMULACIONES DE OPERACIÓN EN SOFTWARE FJ ---\n")

    # SIMULACIÓN 1: Registro válido de cliente corporativo
    sistema.registrar_cliente("CLI-01", "TechServe Solutions S.A.S.", "contacto@techserve.com", "3104567890")

    # SIMULACIÓN 2: Registro válido de segundo cliente
    sistema.registrar_cliente("CLI-02", "Innovación Andina Ltda.", "gerencia@innovandina.co", "3209876543")

    # SIMULACIÓN 3: Registro inválido de cliente (correo sin dominio válido y teléfono corto)
    sistema.registrar_cliente("CLI-03", "Usuario Erróneo", "correo_sin_arroba", "123")

    # SIMULACIÓN 4: Registro inválido de cliente duplicado (mismo ID CLI-01)
    sistema.registrar_cliente("CLI-01", "Empresa Duplicada", "duplicado@empresa.com", "3001112233")

    # SIMULACIÓN 5: Creación válida de los 3 servicios especializados (Polimorfismo)
    sala_juntas = ReservaSala("SRV-01", "Sala Ejecutiva Orion", tarifa_base=80000, capacidad=12, tiene_videoconferencia=True)
    servidores_rack = AlquilerEquipo("SRV-02", "Workstation GPU Xeon", tarifa_base=45000, cantidad_unidades=3, especificaciones="64GB RAM, RTX 4090")
    asesoria_sec = AsesoriaEspecializada("SRV-03", "Auditoría Hardening Linux", tarifa_base=120000, area_tecnica="Ciberseguridad", nivel_senior=True)

    sistema.registrar_servicio(sala_juntas)
    sistema.registrar_servicio(servidores_rack)
    sistema.registrar_servicio(asesoria_sec)

    # SIMULACIÓN 6: Creación inválida de servicio (tarifa negativa controlada mediante try/except)
    try:
        servicio_invalido = ReservaSala("SRV-99", "Sala Fantasma", tarifa_base=-50000, capacidad=5)
        sistema.registrar_servicio(servicio_invalido)
    except ErrorSistemaFJ as err:
        sistema._logger.error(f"SIMULACION 6 - Creación de servicio bloqueada correctamente: {err}")

    # SIMULACIÓN 7: Reserva válida confirmada automáticamente (Sala Ejecutiva por 4 horas con descuento)
    sistema.crear_reserva(
        id_reserva="RES-101",
        id_cliente="CLI-01",
        id_servicio="SRV-01",
        duracion_horas=4,
        descuento=30000.0,
        confirmar_automaticamente=True,
    )

    # SIMULACIÓN 8: Reserva fallida por servicio no disponible (SRV-01 ya está ocupado por RES-101)
    sistema.crear_reserva(
        id_reserva="RES-102",
        id_cliente="CLI-02",
        id_servicio="SRV-01",
        duracion_horas=2,
        confirmar_automaticamente=True,
    )

    # SIMULACIÓN 9: Reserva fallida por cliente inexistente (prueba encadenamiento raise ... from ...)
    sistema.crear_reserva(
        id_reserva="RES-103",
        id_cliente="CLI-999",
        id_servicio="SRV-02",
        duracion_horas=5,
    )

    # SIMULACIÓN 10: Reserva válida con recargo de urgencia (sobrecarga de cálculo) y procesamiento completo
    sistema.crear_reserva(
        id_reserva="RES-104",
        id_cliente="CLI-02",
        id_servicio="SRV-03",
        duracion_horas=6,
        recargo_urgencia=75000.0,
        confirmar_automaticamente=True,
    )
    sistema.cambiar_estado_reserva("RES-104", "PROCESAR")

    # SIMULACIÓN 11: Operación no permitida (intentar cancelar una reserva que ya fue PROCESADA)
    sistema.cambiar_estado_reserva("RES-104", "CANCELAR")

    # SIMULACIÓN 12: Cálculo inconsistente (descuento superior al subtotal del servicio)
    sistema.crear_reserva(
        id_reserva="RES-105",
        id_cliente="CLI-01",
        id_servicio="SRV-02",
        duracion_horas=2,
        descuento=9999999.0,
    )

    # Mostrar resumen consolidado en consola
    sistema.generar_reporte_consola()


if __name__ == "__main__":
    ejecutar_simulaciones()