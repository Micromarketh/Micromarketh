from typing import List
from fastapi import APIRouter
from domain.models import Product, ProductCreate
from repository.product_repo import ProductRepository
from service.product_service import ProductService

repo = ProductRepository()
service = ProductService(repo)

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])


@router.get("/", response_model=List[Product], summary="Listar productos")
def listar_productos():
    return service.get_all_products()


@router.get("/{product_id}", response_model=Product, summary="Consultar producto")
def consultar_producto(product_id: int):
    return service.get_product(product_id)


@router.post("/", response_model=Product, status_code=201, summary="Crear producto")
def crear_producto(data: ProductCreate):
    return service.create_product(data)


@router.delete("/{product_id}", summary="Inactivar producto")
def inactivar_producto(product_id: int):
    return service.inactivate_product(product_id)
