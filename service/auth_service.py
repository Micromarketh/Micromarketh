# CAPA SERVICIO — autenticación y tokens JWT (HU-024)
# No importa nada de FastAPI.

import os
import uuid
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from domain.usuario import LoginRequest, CambioContrasenaRequest, TokenDatos, SesionValidada, EXPIRA_EN
from repository.usuario_repo import UsuarioRepository

SECRET_KEY = os.getenv("JWT_SECRET", "micromarket-clave-desarrollo")
ALGORITMO = "HS256"


class CredencialesInvalidas(Exception):
    """Usuario o contraseña incorrectos (401)."""


class CuentaBloqueada(Exception):
    """Cuenta bloqueada por intentos fallidos (423)."""


class TokenInvalido(Exception):
    """Token vencido, revocado o mal formado (401)."""


class ServicioNoDisponible(Exception):
    """La base de datos no responde (503)."""


class AuthService:

    def __init__(self, repo: UsuarioRepository):
        # Inyección de dependencia
        self.repo = repo

    # ── Ayudantes ─────────────────────────────────────────────
    def _repo(self, operacion, *args):
        try:
            return operacion(*args)
        except ConnectionError:
            raise ServicioNoDisponible("El servicio no está disponible en este momento. Intente más tarde")

    def _emitir_token(self, u) -> TokenDatos:
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": str(u.id), "usuario": u.usuario, "rol": u.rol, "sedes": u.sedes,
            "jti": uuid.uuid4().hex, "iat": ahora,
            "exp": ahora + timedelta(seconds=EXPIRA_EN),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)
        return TokenDatos(token=token, expiraEn=EXPIRA_EN, rol=u.rol, sedes=u.sedes)

    def validar_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        except jwt.ExpiredSignatureError:
            raise TokenInvalido("El token ha expirado")
        except jwt.InvalidTokenError:
            raise TokenInvalido("Token inválido")
        if self.repo.token_revocado(payload["jti"]):
            raise TokenInvalido("La sesión fue cerrada; inicie sesión de nuevo")
        return payload

    # ── FUN-81: Login ─────────────────────────────────────────
    def autenticar(self, datos: LoginRequest) -> TokenDatos:
        u = self._repo(self.repo.obtener_por_usuario, datos.usuario)
        if not u or not u.activo:
            raise CredencialesInvalidas("Usuario o contraseña incorrectos")
        if u.esta_bloqueado():
            raise CuentaBloqueada("La cuenta está bloqueada temporalmente")
        if not bcrypt.checkpw(datos.contrasena.encode(), u.contrasena_hash):
            u.registrar_intento_fallido()   # la regla está en el dominio
            raise CredencialesInvalidas("Usuario o contraseña incorrectos")
        u.reiniciar_intentos()
        return self._emitir_token(u)

    # ── FUN-82: Renovar token ─────────────────────────────────
    def renovar(self, token: str) -> TokenDatos:
        payload = self.validar_token(token)
        self.repo.revocar_token(payload["jti"])          # el token viejo deja de servir
        u = self._repo(self.repo.obtener_por_id, int(payload["sub"]))
        return self._emitir_token(u)

    # ── FUN-83: Logout ────────────────────────────────────────
    def cerrar_sesion(self, token: str) -> None:
        payload = self.validar_token(token)
        self.repo.revocar_token(payload["jti"])

    # ── FUN-84: Cambiar contraseña ────────────────────────────
    def cambiar_contrasena(self, token: str, datos: CambioContrasenaRequest) -> None:
        payload = self.validar_token(token)
        u = self._repo(self.repo.obtener_por_id, int(payload["sub"]))
        if not bcrypt.checkpw(datos.contrasena_actual.encode(), u.contrasena_hash):
            raise CredencialesInvalidas("La contraseña actual es incorrecta")
        if datos.contrasena_actual == datos.contrasena_nueva:
            raise ValueError("La nueva contraseña debe ser diferente a la actual")
        nuevo_hash = bcrypt.hashpw(datos.contrasena_nueva.encode(), bcrypt.gensalt())
        self._repo(self.repo.actualizar_contrasena, u.id, nuevo_hash)


    # ── HU-033: validar sesión para otros módulos (API interna) ──
    def validar_sesion(self, token: str) -> SesionValidada:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
        except jwt.ExpiredSignatureError:
            raise TokenInvalido("El token ha expirado")
        except jwt.InvalidTokenError:
            raise TokenInvalido("Token inválido")
        u = self._repo(self.repo.obtener_por_id, int(payload["sub"]))
        if self.repo.token_revocado(payload["jti"]):
            raise TokenInvalido("La sesión fue revocada")
        if not u or not u.activo:
            raise TokenInvalido("El usuario no está activo")
        return SesionValidada(
            usuarioId=f"USR-{u.id:04d}",
            rol=u.rol,
            sedeId=u.sedes[0],
            vigente=True,
        )