"""Capa API: MOD-02 Gestión de Catálogo Central (HU-005 API Productos, HU-007 API Precios y Códigos de Barras)."""
from fastapi import APIRouter, Depends, Query

from app.api.dependencies import producto_service
from app.api.historias import tag
from app.api.schemas import CodigoAsignar, ProductoActualizar, ProductoCrear, ProductoSalida, TarifaActualizar
from app.core.respuesta import respuesta
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/api/v1/catalogo")
HU005, HU007 = tag("HU-005"), tag("HU-007")


@router.post("/registrar-producto", tags=[HU005], summary="FUN-11 · Registrar Producto", status_code=201)
def registrar_producto(datos: ProductoCrear, svc: ProductoService = Depends(producto_service)):
    p = svc.registrar(datos.model_dump())
    return respuesta(201, "Producto registrado correctamente", ProductoSalida.model_validate(p))


@router.get("/consultar-catalogo-maestro", tags=[HU005], summary="FUN-12 · Consultar Catálogo Maestro")
def consultar_catalogo(texto: str | None = None, pagina: int = Query(1, ge=1), tamano: int = Query(20, ge=1, le=100),
                       svc: ProductoService = Depends(producto_service)):
    productos, total = svc.catalogo(texto, pagina, tamano)
    datos = {"productos": [ProductoSalida.model_validate(p) for p in productos],
             "pagina": pagina, "tamano": tamano, "total": total}
    return respuesta(200, "Consulta del catálogo exitosa", datos)


@router.put("/actualizar-producto", tags=[HU005], summary="FUN-13 · Actualizar Producto")
def actualizar_producto(datos: ProductoActualizar, producto_id: int = Query(...), svc: ProductoService = Depends(producto_service)):
    p = svc.actualizar(producto_id, datos.model_dump(exclude_none=True))
    return respuesta(200, "Producto actualizado correctamente", ProductoSalida.model_validate(p))


@router.delete("/inactivar-producto", tags=[HU005], summary="FUN-14 · Inactivar Producto")
def inactivar_producto(producto_id: int = Query(...), svc: ProductoService = Depends(producto_service)):
    p = svc.inactivar(producto_id)
    return respuesta(200, "Producto inactivado correctamente", ProductoSalida.model_validate(p))


@router.get("/consultar-precio-por-codigo-de-barras", tags=[HU007], summary="FUN-21 · Consultar Precio por Código de Barras")
def consultar_precio(codigo: str = Query(..., examples=["7702511000014"]), svc: ProductoService = Depends(producto_service)):
    p = svc.precio_por_codigo(codigo)
    return respuesta(200, "Consulta de precio exitosa",
                     {"productoId": p.id, "nombre": p.nombre, "precio": p.precio, "tasaIva": p.tasa_iva})


@router.put("/actualizar-tarifa-de-producto", tags=[HU007], summary="FUN-22 · Actualizar Tarifa de Producto")
def actualizar_tarifa(datos: TarifaActualizar, svc: ProductoService = Depends(producto_service)):
    p = svc.actualizar_tarifa(datos.producto_id, datos.precio)
    return respuesta(200, "Tarifa actualizada correctamente", ProductoSalida.model_validate(p))


@router.post("/asignar-codigo-de-barras", tags=[HU007], summary="FUN-23 · Asignar Código de Barras", status_code=201)
def asignar_codigo(datos: CodigoAsignar, svc: ProductoService = Depends(producto_service)):
    p = svc.asignar_codigo(datos.producto_id, datos.codigo_barras)
    return respuesta(201, "Código de barras asignado correctamente", ProductoSalida.model_validate(p))
