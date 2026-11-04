# Veterinaria — FastAPI + SQLModel + PostgreSQL

Trabajo práctico de Programación III (UTN). Esta base de proyecto corresponde a los **Ejercicios 1 y 2** de la consigna: proyecto, conexión y ciclo de vida; contratos y CRUD de dueños (con ficha), mascotas y prácticas.

> Estado: estructura y código recibidos en el ZIP de trabajo. La compilación de los módulos Python fue verificada; la ejecución funcional de los endpoints requiere configurar PostgreSQL y realizar las pruebas HTTP.

## Requisitos

- Python 3.12 o superior.
- PostgreSQL 16.

## Levantar el proyecto desde cero

Los comandos siguientes se ejecutan desde la carpeta raíz del repositorio.

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

### 4. Crear el esquema

```bash
python reiniciar.py
```

### 5. Arrancar el servidor

```bash
uvicorn app.main:app --reload
```

La documentación interactiva queda en <http://127.0.0.1:8000/docs>.

## Pruebas

Los casos disponibles están en `test/`:

- `ej1_health.http`: pruebas de los endpoints de salud.
- `ej2_crud.http`: pruebas HTTP del CRUD incluido.
- `c08_precio_cero.sql`: prueba SQL de restricción de precio (corresponde a una consigna posterior y requiere que exista esa tabla/restricción).

Los archivos `.http` se pueden ejecutar con la extensión REST Client de VS Code o con un cliente HTTP compatible. Ejecutar `python reiniciar.py` antes de probar.

## Decisiones de diseño documentadas en esta etapa

- **Motor y sesión**: el motor asincrónico y la fábrica de sesiones se crean en el `lifespan` y viven en `app.state`; el motor se cierra al apagar. Cada petición recibe su sesión mediante `Depends(get_session)`, creada con `expire_on_commit=False`.
- **Reglas en la base**: unicidad (email, nombre de práctica y ficha por dueño), `CHECK` (precio > 0) y `ON DELETE RESTRICT` (dueño con mascotas) se delegan a PostgreSQL. El servicio atrapa `IntegrityError`, hace `rollback` y responde 409 con un mensaje propio.
- **Ficha**: la clave foránea está en `ficha_duenio.duenio_id` y tiene restricción `UNIQUE`, para que cada dueño tenga como máximo una ficha.
- **Relaciones**: las lecturas que incluyen relaciones deben usar carga anticipada, evitando depender de la carga perezosa.

## Publicar en GitHub

Después de crear un repositorio vacío en GitHub, ejecutar desde esta carpeta:

```bash
git init
git add .
git commit -m "feat: actividades 1 y 2 - API veterinaria"
git branch -M main
git remote add origin https://github.com/USUARIO/veterinaria-programacion-iii.git
git push -u origin main
```

Reemplazar `USUARIO` por el nombre de usuario de GitHub. Antes del `git add`, comprobar que `.env` no esté incluido (`git status`).
