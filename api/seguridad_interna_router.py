# CAPA API — endpoint INTERNO de seguridad (HU-033)
# Lo consumen otros módulos (Ventas POS), no las aplicaciones cliente.

from typing import Optional
from fastapi import APIRouter, Depends
from domain.usuario import SesionValidada
from api.auth_router import Respuesta, ERRORES, error, obtener_token, service

router = APIRouter(prefix="/internal/seguridad", tags=["Interno · Seguridad"])


@router.get("/validar-token", response_model=Respuesta[SesionValidada],
            summary="Validar la sesión y el rol del cajero",
            description="API interna MOD-03 → MOD-06. Verifica firma, expiración y "
                        "revocación del token, y devuelve usuario, rol y sede.")
def validar_token(token: Optional[str] = Depends(obtener_token)):
    if not token:
        return error(401, "Debe enviar el token")
    try:
        return Respuesta(mensaje="Token válido", datos=service.validar_sesion(token))
    except tuple(ERRORES) as e:
        return error(ERRORES[type(e)], str(e))