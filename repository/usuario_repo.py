# CAPA REPOSITORIO — guardar y recuperar usuarios y tokens revocados
# Sin lógica de negocio ni FastAPI.

import os
from typing import Optional
import bcrypt
from domain.usuario import Usuario


def _hash(contrasena: str) -> bytes:
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt())


class UsuarioRepository:

    def __init__(self):
        self._datos: list[Usuario] = []
        self._tokens_revocados: set[str] = set()
        self._seed()

    def _seed(self):
        """Usuarios de ejemplo (contraseñas cifradas con BCrypt)."""
        self._datos = [
            Usuario(1, "jperez", _hash("Cajero123*"), "CAJERO", ["SED-01"]),
            Usuario(2, "admin", _hash("Admin123*"), "ADMINISTRADOR", ["SED-01", "SED-02"]),
            Usuario(3, "mgomez", _hash("Bodega123*"), "BODEGUERO", ["SED-02"]),
        ]

    def _verificar_conexion(self):
        # Simula la caída de la base de datos (caso de prueba 5)
        if os.getenv("SIMULAR_FALLA_BD") == "1":
            raise ConnectionError("Base de datos no disponible")

    # ── Usuarios ──────────────────────────────────────────────
    def obtener_por_usuario(self, usuario: str) -> Optional[Usuario]:
        self._verificar_conexion()
        return next((u for u in self._datos if u.usuario == usuario), None)

    def obtener_por_id(self, id: int) -> Optional[Usuario]:
        self._verificar_conexion()
        return next((u for u in self._datos if u.id == id), None)

    def actualizar_contrasena(self, id: int, nuevo_hash: bytes) -> None:
        self._verificar_conexion()
        u = self.obtener_por_id(id)
        if u:
            u.contrasena_hash = nuevo_hash

    # ── Tokens revocados (logout) ─────────────────────────────
    def revocar_token(self, jti: str) -> None:
        self._tokens_revocados.add(jti)

    def token_revocado(self, jti: str) -> bool:
        return jti in self._tokens_revocados


# Instancia única compartida
usuario_repository = UsuarioRepository()
