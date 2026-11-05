# Veterinaria — FastAPI + SQLModel + PostgreSQL

Trabajo práctico de Programación III (UTN). Implementación integral de los **Ejercicios 1 a 6**: proyecto, ciclo de vida y conexión asincrónica; contratos y CRUD; modelos, restricciones y relaciones relacionales; altas con relaciones y composición; lecturas con carga anticipada sin N+1; y asincronía sin bloqueos con módulo de laboratorio.

## Requisitos

- Python 3.12 o superior.
- PostgreSQL 16.

## Levantar el proyecto desde cero

Los comandos siguientes se ejecutan desde la carpeta `veterinaria/` del repositorio.

### 1. Crear y activar el entorno virtual

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar la base de datos

Crear en PostgreSQL una base vacía llamada `veterinaria` (o elegir otro nombre) y copiar `env.example` como `.env`.

Windows (PowerShell):

```powershell
Copy-Item env.example .env
```

Linux / macOS:

```bash
cp env.example .env
```

Editar `.env` y completar `DATABASE_URL` con el usuario, contraseña, host, puerto y nombre de la base local. No subir el archivo `.env` a GitHub.

### 4. Crear el esquema y sembrar datos iniciales

```bash
python reiniciar.py
```

### 5. Arrancar el servidor

```bash
uvicorn app.main:app --reload
```

La documentación interactiva OpenAPI queda disponible en <http://127.0.0.1:8000/docs>.

---

## Índice de la clave foránea `turno_practica.turno_id`

> **Justificación requerida por la consigna:**  
> La clave foránea `turno_practica.turno_id` **no necesita un índice secundario propio** porque la tabla define como clave primaria la tupla compuesta `(turno_id, practica_id)`. En PostgreSQL, el índice B-tree generado automáticamente para la clave primaria indexa como primera columna líder a `turno_id`. Por lo tanto, cualquier búsqueda, filtro o comprobación de integridad referencial (`ON DELETE CASCADE`) por `turno_id` utiliza de manera directa y óptima el índice de la clave primaria existente, haciendo redundante crear un índice adicional.

---

## Pruebas

Los casos de prueba están organizados en `test/` según las consignas:

- `ej1_health.http`: pruebas de los endpoints de salud (`/health/live` y `/health/ready`).
- `ej2_crud.http`: pruebas HTTP del CRUD de dueños, fichas, mascotas y catálogo de prácticas (Casos C-01, C-02, C-03, C-04 parte mascota, C-05 parte dueño).
- `ej5_turnos.http`: pruebas de turnos, composición con prácticas, validaciones (C-04 parte turno, RN-05, RN-07), detalle con carga anticipada sin N+1 (Caso C-07), y borrado en cascada (Caso C-05 parte turno).
- `ej6_laboratorio.http`: pruebas del módulo de laboratorio ejecutando llamadas sincrónicas en hilos de trabajo sin bloquear el bucle de eventos (Caso C-09).
- `c08_precio_cero.sql`: prueba directa en PostgreSQL de la restricción `CHECK precio > 0` en la tabla `practica` (Caso C-08).

Los archivos `.http` se pueden ejecutar con la extensión REST Client de VS Code o con cualquier cliente HTTP compatible. Ejecutar `python reiniciar.py` antes de correr las pruebas.

---

## Decisiones de diseño documentadas

- **Motor y sesión (Ejercicio 1)**: el motor asincrónico y la fábrica de sesiones se crean en el `lifespan` y viven en `app.state`; el motor se cierra limpiamente al apagar. Cada petición recibe su sesión mediante `Depends(get_session)`, creada con `expire_on_commit=False`.
- **Reglas en la base (Ejercicio 2 y 3)**: unicidad (email, nombre de práctica y ficha por dueño), `CHECK` (precio de práctica > 0, precio unitario de turno_practica > 0, total de turno >= 0), `ON DELETE RESTRICT` (dueño con mascotas, mascota con turnos, práctica con turnos) y `ON DELETE CASCADE` (turno con turno_practica) se delegan al motor relacional de PostgreSQL. El servicio atrapa `IntegrityError`, hace `rollback` y responde 409 con mensaje propio.
- **Ficha (Uno a uno)**: la clave foránea está en `ficha_duenio.duenio_id` con restricción `UNIQUE`, para que cada dueño tenga como máximo una ficha.
- **Turnos y Prácticas (Muchos a muchos con datos / Composición)**: la tabla intermedia `turno_practica` vive en el módulo `turnos` (según consigna) y almacena el `precio_unitario` congelado al momento del alta (RN-06). El total del turno se calcula en el servidor como la suma de los precios unitarios.
- **Borrado en cascada sin interferencia del ORM**: `Turno.practicas` y `Turno.turno_practicas` configuran `passive_deletes=True`. Al borrar un turno con `session.delete(turno)`, PostgreSQL ejecuta el `ON DELETE CASCADE` en la base sin que SQLAlchemy intente emitir borrados o actualizaciones individuales innecesarias.
- **Carga anticipada sin N+1 (Ejercicio 5)**: en `GET /turnos/{id}`, el detalle se recupera con número fijo de consultas (3 consultas fijas: `SELECT turno` con `joinedload(Turno.mascota)`, `SELECT turno_practica` con `selectinload`, y `SELECT practica` con `selectinload`), independientemente de cuántas prácticas tenga el turno (Caso C-07). Ninguna lectura depende de carga perezosa (`lazy load`), previniendo errores de `MissingGreenlet` en contexto asincrónico.
- **Asincronía sin bloqueos (Ejercicio 6)**: la función bloqueante `consultar_stock` de la biblioteca externa sincrónica (`time.sleep(1)`) se ejecuta fuera del bucle de eventos mediante `asyncio.to_thread`, permitiendo que el servidor siga atendiendo otras solicitudes concurrentes (como `GET /health/live`) de manera inmediata (Caso C-09).
