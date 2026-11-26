# CAPA DOMINIO — Usuario y reglas de autenticación (HU-024)
# No importa nada de FastAPI ni de base de datos.

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

MAX_INTENTOS = 5          # RN: tras 5 intentos fallidos se bloquea
MINUTOS_BLOQUEO = 15      # bloqueo temporal
EXPIRA_EN = 3600          # segundos de vida del token


# ── Schemas de ENTRADA ────────────────────────────────────────
class LoginRequest(BaseModel):
    usuario:    str = Field(..., min_length=3, examples=["jperez"])
    contrasena: str = Field(..., min_length=4, examples=["Cajero123*"])


class CambioContrasenaRequest(BaseModel):
    contrasena_actual: str = Field(..., min_length=4)
    contrasena_nueva:  str = Field(..., min_length=8, description="Mínimo 8 caracteres")


# ── Schema de SALIDA ──────────────────────────────────────────
class TokenDatos(BaseModel):
    token:    str
    expiraEn: int
    rol:      str
    sedes:    list[str]


# ── Entidad del dominio ───────────────────────────────────────
class Usuario:
    def __init__(self, id: int, usuario: str, contrasena_hash: bytes,
                 rol: str, sedes: list[str], activo: bool = True):
        self.id = id
        self.usuario = usuario
        self.contrasena_hash = contrasena_hash   # cifrada con BCrypt
        self.rol = rol
        self.sedes = sedes
        self.activo = activo
        self.intentos_fallidos = 0
        self.bloqueado_hasta: Optional[datetime] = None

    # REGLA: ¿la cuenta está bloqueada temporalmente?
    def esta_bloqueado(self) -> bool:
        return self.bloqueado_hasta is not None and datetime.now() < self.bloqueado_hasta

    # REGLA: al quinto intento fallido se bloquea
    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= MAX_INTENTOS:
            self.bloqueado_hasta = datetime.now() + timedelta(minutes=MINUTOS_BLOQUEO)

    # REGLA: un login correcto reinicia el contador
    def reiniciar_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None



# ── Schema de SALIDA de la validación interna (HU-033) ────────
class SesionValidada(BaseModel):
    usuarioId: str
    rol:       str
    sedeId:    str
    vigente:   bool
    