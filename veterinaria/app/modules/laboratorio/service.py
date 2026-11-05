import asyncio

from app.modules.laboratorio.cliente import consultar_stock


async def obtener_stock(vacuna: str) -> int:
    """Consulta el stock en la biblioteca del laboratorio sin bloquear el bucle de eventos.

    La biblioteca del laboratorio (`cliente.consultar_stock`) es sincrónica y bloqueante
    (ejecuta `time.sleep(1)`). Usamos `asyncio.to_thread` para delegar su ejecución a un
    hilo secundario del thread pool, permitiendo que el bucle de eventos siga atendiendo
    otras peticiones (como `GET /health/live`) de manera inmediata (Ejercicio 6 / Caso C-09).
    """
    return await asyncio.to_thread(consultar_stock, vacuna)
