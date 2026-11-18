# CAPA API — rutas HTTP. Solo llama al servicio y convierte errores en HTTP.
# Aquí NO hay lógica de negocio.

from fastapi import APIRouter, HTTPException, status
from domain.models import ProductoCreate, ProductoResponse
from repository.product_repo import producto_repository
from service.product_service import ProductoService, ProductoNoEncontrado

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])

# Inyección del repositorio en el servicio
service = ProductoService(repo=producto_repository)


@router.get("/", response_model=list[ProductoResponse], summary="Listar productos")
def listar_productos():
    return service.listar()


@router.get("/{id}", response_model=ProductoResponse, summary="Consultar producto")
def obtener_producto(id: int):
    try:
        return service.obtener(id)
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=ProductoResponse,
             status_code=status.HTTP_201_CREATED, summary="Crear producto")
def crear_producto(datos: ProductoCreate):
    try:
        return service.crear(datos)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}", response_model=ProductoResponse, summary="Actualizar producto")
def actualizar_producto(id: int, datos: ProductoCreate):
    try:
        return service.actualizar(id, datos)
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", summary="Inactivar producto")
def inactivar_producto(id: int):
    try:
        return service.inactivar(id)
    except ProductoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    