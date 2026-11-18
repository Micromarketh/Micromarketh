from typing import Optional, List
from domain.models import Product, ProductCreate


class ProductRepository:
    """Simulamos una base de datos con un dict."""

    def __init__(self):
        # "Base de datos" en memoria
        self._db: dict[int, Product] = {}
        self._next_id: int = 1

    def get_all(self) -> List[Product]:
        # Devuelve solo los productos activos
        return [p for p in self._db.values() if p.estado == "ACTIVO"]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        # Busca por ID. None si no existe
        return self._db.get(product_id)

    def get_by_codigo_barras(self, codigo: str) -> Optional[Product]:
        # Busca por código de barras. None si no existe
        for p in self._db.values():
            if p.codigo_barras == codigo:
                return p
        return None

    def create(self, data: ProductCreate) -> Product:
        # Asigna ID, guarda y retorna el producto
        product = Product(
            id=self._next_id,
            **data.model_dump()
        )
        self._db[self._next_id] = product
        self._next_id += 1
        return product

    def inactivate(self, product_id: int) -> bool:
        # True si existía y se inactivó (no se borra: se conserva el historial)
        product = self._db.get(product_id)
        if product:
            product.estado = "INACTIVO"
            return True
        return False