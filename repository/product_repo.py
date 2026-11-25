# CAPA REPOSITORIO — única responsabilidad: guardar y recuperar productos
# Sin lógica de negocio ni FastAPI.

from typing import Optional
from domain.models import Producto


class ProductoRepository:

    def __init__(self):
        # Almacén en memoria
        self._datos: list[Producto] = []
        self._siguiente_id: int = 1
        self._seed()

    def _seed(self):
        """Productos de ejemplo del micromercado."""
        self._datos = [
            Producto(1, "Arroz Diana 500 g", "Diana", "Granos", "7702511000014", 3200, 0),
            Producto(2, "Leche Entera 1 L", "Alquería", "Lácteos", "7702177000028", 4500, 0),
            # La gaseosa simula un traslado en curso (para probar el 409)
            Producto(3, "Gaseosa 1.5 L", "Postobón", "Bebidas", "7702090000035", 5200, 19,
                     movimientos_en_curso=True),
        ]
        self._siguiente_id = 4

    # ── CRUD ──────────────────────────────────────────────────
    def obtener_todos(self) -> list[Producto]:
        return self._datos.copy()

    def obtener_por_id(self, id: int) -> Optional[Producto]:
        return next((p for p in self._datos if p.id == id), None)

    def obtener_por_codigo_barras(self, codigo: str) -> Optional[Producto]:
        return next((p for p in self._datos if p.codigo_barras == codigo), None)

    def crear(self, nombre: str, marca: str, categoria: str,
              codigo_barras: str, precio: float, tasa_iva: int) -> Producto:
        nuevo = Producto(self._siguiente_id, nombre, marca, categoria,
                         codigo_barras, precio, tasa_iva)
        self._datos.append(nuevo)
        self._siguiente_id += 1
        return nuevo

    def actualizar(self, id: int, nombre: str, marca: str, categoria: str,
                   codigo_barras: str, precio: float, tasa_iva: int) -> Optional[Producto]:
        p = self.obtener_por_id(id)
        if not p:
            return None
        p.nombre        = nombre
        p.marca         = marca
        p.categoria     = categoria
        p.codigo_barras = codigo_barras
        p.precio        = precio
        p.tasa_iva      = tasa_iva
        return p


# Instancia única compartida
producto_repository = ProductoRepository()