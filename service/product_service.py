from typing import List
from fastapi import HTTPException, status

from domain.models import Product, ProductCreate
from repository.product_repo import ProductRepository


class ProductService:

    def __init__(self, repo: ProductRepository):
        # Recibe el repositorio por inyección de dependencias
        self.repo = repo

    # FUN-12 · Consultar catálogo maestro
    def get_all_products(self) -> List[Product]:
        return self.repo.get_all()

    # FUN-12 · Obtener un producto por ID
    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)

        # ⬇ Regla de negocio: si no existe, lanza error 404
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {product_id} no encontrado"
            )
        return product

    # FUN-21 · Consultar precio por código de barras (HU-007)
    def get_by_codigo_barras(self, codigo: str) -> Product:
        product = self.repo.get_by_codigo_barras(codigo)
        if not product or product.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe un producto activo con el código indicado"
            )
        return product

    # FUN-11 · Registrar producto
    def create_product(self, data: ProductCreate) -> Product:
        # ⬇ Regla RN-08: el precio debe ser mayor que cero
        if data.precio <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio debe ser mayor que cero"
            )
        # ⬇ Regla RN-08: el código de barras es único en la cadena
        if self.repo.get_by_codigo_barras(data.codigo_barras):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El código de barras ya está asignado a otro producto"
            )
        return self.repo.create(data)

    # FUN-14 · Inactivar producto
    def inactivate_product(self, product_id: int) -> dict:
        inactivated = self.repo.inactivate(product_id)
        if not inactivated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {product_id} no encontrado"
            )
        return {"message": "Producto inactivado correctamente"}