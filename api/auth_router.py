# CAPA API — endpoints de seguridad (HU-024)
# Solo llama al servicio y arma la respuesta con el contrato estándar.

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from domain.usuario import LoginRequest, CambioContrasenaRequest, TokenDatos
from repository.usuario_repo import usuario_repository
from service.auth_service import (AuthService, CredencialesInvalidas, CuentaBloqueada,
                                  TokenInvalido, ServicioNoDisponible)

T = TypeVar("T")


class Respuesta(BaseModel, Generic[T]):
    exito: bool = True
    codigo: int = 200
    mensaje: str
    datos: Optional[T] = None
    errores: list[dict] = []


# Cada error del servicio con su código HTTP
ERRORES = {
    CredencialesInvalidas: 401,
    TokenInvalido: 401,
    CuentaBloqueada: 423,
    ServicioNoDisponible: 503,
    ValueError: 400,
}


def error(codigo: int, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=codigo, content={
        "exito": False, "codigo": codigo, "mensaje": mensaje,
        "datos": None, "errores": [{"detalle": mensaje}],
    })


router = APIRouter(prefix="/api/v1/seguridad", tags=["Seguridad"])
service = AuthService(repo=usuario_repository)
bearer = HTTPBearer(auto_error=False)


def obtener_token(cred: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> Optional[str]:
    return cred.credentials if cred else None


@router.post("/autenticar-usuario-login", response_model=Respuesta[TokenDatos],
             summary="Autenticar usuario (login)")
def login(datos: LoginRequest):
    try:
        return Respuesta(mensaje="Autenticación exitosa", datos=service.autenticar(datos))
    except tuple(ERRORES) as e:
        return error(ERRORES[type(e)], str(e))


@router.post("/renovar-token-jwt", response_model=Respuesta[TokenDatos],
             summary="Renovar token JWT")
def renovar(token: Optional[str] = Depends(obtener_token)):
    if not token:
        return error(401, "Debe enviar el token")
    try:
        return Respuesta(mensaje="Token renovado correctamente", datos=service.renovar(token))
    except tuple(ERRORES) as e:
        return error(ERRORES[type(e)], str(e))


@router.delete("/cerrar-sesion-logout", response_model=Respuesta[None],
               summary="Cerrar sesión (logout)")
def logout(token: Optional[str] = Depends(obtener_token)):
    if not token:
        return error(401, "Debe enviar el token")
    try:
        service.cerrar_sesion(token)
        return Respuesta(mensaje="Sesión cerrada correctamente")
    except tuple(ERRORES) as e:
        return error(ERRORES[type(e)], str(e))


@router.put("/cambiar-contrasena", response_model=Respuesta[None],
            summary="Cambiar contraseña")
def cambiar_contrasena(datos: CambioContrasenaRequest,
                       token: Optional[str] = Depends(obtener_token)):
    if not token:
        return error(401, "Debe enviar el token")
    try:
        service.cambiar_contrasena(token, datos)
        return Respuesta(mensaje="Contraseña actualizada correctamente")
    except tuple(ERRORES) as e:
        return error(ERRORES[type(e)], str(e))