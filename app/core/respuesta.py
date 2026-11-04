"""Respuesta JSON estándar del proyecto: exito, codigo, mensaje, datos, errores, metadatos."""
import uuid
from datetime import datetime, timezone

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def respuesta(codigo: int, mensaje: str, datos=None, errores=None) -> JSONResponse:
    exito = codigo < 400
    cuerpo = {
        "exito": exito,
        "codigo": codigo,
        "mensaje": mensaje,
        "datos": datos if exito else None,
        "errores": errores or [],
        "metadatos": {
            "fechaHora": datetime.now(timezone.utc).isoformat(),
            "idSolicitud": uuid.uuid4().hex[:8],
        },
    }
    return JSONResponse(status_code=codigo, content=jsonable_encoder(cuerpo))
