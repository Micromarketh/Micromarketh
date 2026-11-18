from typing import List
from fastapi import APIRouter, status

from domain.models import Product, ProductCreate
from service.product_service import ProductService
from repository.product_repo import ProductRepository


# Instancias (en producción usarías DI de FastAPI)
repo = ProductRepository()
service = ProductService(repo)

# Router: agrupa endpoints bajo un prefijo
router = APIRouter(
    prefix="/api/v1/productos",
    tags=["HU-005 · Gestionar el catálogo maestro de productos"]
)


@router.get("/", response_model=List[Product])
def list_products():
    """FUN-12 · Devuelve todos los productos activos."""
    return service.get_all_products()


@router.get("/codigo-barras/{codigo}", response_model=Product,
            tags=["HU-007 · Consultar precio e IVA por código de barras"])
def get_by_codigo_barras(codigo: str):
    """FUN-21 · Devuelve el producto, su precio y su IVA por código de barras."""
    return service.get_by_codigo_barras(codigo)


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    """FUN-12 · Devuelve un producto por su ID."""
    return service.get_product(product_id)


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED
)
def create_product(data: ProductCreate):
    """FUN-11 · Registra un nuevo producto."""
    return service.create_product(data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def inactivate_product(product_id: int):
    """FUN-14 · Inactiva un producto por su ID."""
    return service.inactivate_product(product_id)