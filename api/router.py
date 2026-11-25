# CAPA API — rutas HTTP. Solo llama al servicio y convierte errores en HTTP.
# Todas las respuestas exitosas usan el formato { "mensaje": ..., "datos": ... }
# definido en las historias de usuario.

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
from domain.models import ProductoCreate, ProductoResponse, CatalogoPaginado
from repository.product_repo import producto_repository
from service.product_service import ProductoService, ProductoNoEncontrado, ProductoEnConflicto

T = TypeVar("T")


class Respuesta(BaseModel, Generic[T]):
    mensaje: str
    datos: Optional[T] = None


router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])

# Inyección del repositorio en el servicio
service = ProductoService(repo=producto_repository)


@router.get("/", response_model=Respuesta[CatalogoPaginado], summary="Consultar catálogo paginado")
def listar_productos(pagina: int = Query(1, ge=1, description="Número de página"),
                     tamano: int = Query(10, ge=1, le=100, description="Productos por página")):
    return Respuesta(mensaje="Catálogo consultado correctamente",
                     datos=service.listar(pagina, tamano))


@router.get("/{id}", response_model=Respuesta[ProductoResponse], summary="Consultar producto")
def obtener_producto(id: int):
    try:
        return Respuesta(mensaje="Producto consultado correctamente",
                         datos=service.obtener(id))
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=Respuesta[ProductoResponse],
             status_code=status.HTTP_201_CREATED, summary="Crear producto")
def crear_producto(datos: ProductoCreate):
    try:
        return Respuesta(mensaje="Producto registrado correctamente",
                         datos=service.crear(datos))
    except ProductoEnConflicto as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put("/{id}", response_model=Respuesta[ProductoResponse], summary="Actualizar producto")
def actualizar_producto(id: int, datos: ProductoCreate):
    try:
        return Respuesta(mensaje="Producto actualizado correctamente",
                         datos=service.actualizar(id, datos))
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductoEnConflicto as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", response_model=Respuesta[ProductoResponse], summary="Inactivar producto")
def inactivar_producto(id: int):
    try:
        resultado = service.inactivar(id)
        return Respuesta(mensaje=resultado["mensaje"], datos=service.obtener(id))
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductoEnConflicto as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))