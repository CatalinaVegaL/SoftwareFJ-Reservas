# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

Proyecto desarrollado para el curso **Programación (213023) – Fase 4 (Componente Práctico)** de la Universidad Nacional Abierta y a Distancia (**UNAD**).

## Descripción del Proyecto
Aplicación orientada a objetos desarrollada en **Python 3** sin uso de bases de datos (gestión en memoria mediante colecciones de objetos y persistencia de auditoría en archivo `.log`). Modela la operación de la empresa **Software FJ** para administrar clientes, servicios especializados y reservas bajo estrictos controles de validación y tolerancia a fallos.

## Arquitectura y Principios POO Aplicados
* **`excepciones.py`**: Jerarquía de excepciones personalizadas derivadas de `ErrorSistemaFJ` (`DatosInvalidosError`, `ParametroFaltanteError`, `ServicioNoDisponibleError`, `ReservaInvalidaError`, `OperacionNoPermitidaError`, `CalculoInconsistenteError`).
* **`modelos.py`**:
  * **Abstracción**: Clases abstractas `Entidad` y `Servicio` (`abc.ABC`).
  * **Encapsulación**: Atributos protegidos con propiedades (`@property`) y validaciones en *setters* dentro de `Cliente` y `Servicio`.
  * **Herencia y Polimorfismo**: Tres servicios especializados (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`) que sobrescriben `calcular_costo_base()` y `describir_servicio()`.
  * **Sobrecarga funcional**: Método `calcular_total()` con soporte opcional para impuestos, descuentos y recargos de urgencia.
* **`gestor.py`**: Controlador transaccional en memoria con registro estructurado (`logging`) en `sistema_fj.log`, implementando bloques `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones (`raise ... from ...`).
* **`main.py`**: Batería de **12 simulaciones completas** (escenarios válidos e inválidos) que demuestran la continuidad operativa del sistema ante errores críticos.

## Ejecución
1. Asegúrese de contar con **Python 3.10 o superior**.
2. Ejecute el archivo principal desde la terminal:
   ```bash
   python main.py