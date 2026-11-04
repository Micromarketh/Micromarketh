"""Capa API: APIs internas entre módulos ya implementadas (HU-034, HU-037, HU-038, HU-054)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import caja_service, producto_service
from app.api.historias import tag
from app.core.database import get_db
from app.core.respuesta import respuesta
from app.repositories.sede_repository import SedeRepository
from app.services.producto_service import ProductoService
from app.services.sede_service import CajaService

router = APIRouter(prefix="/internal")


@router.get("/sedes/validar-caja", tags=[tag("HU-034")], summary="Validar que la caja esté activa en la sede (MOD-03 → MOD-01)")
def validar_caja(cajaId: int, sedeId: int, svc: CajaService = Depends(caja_service)):
    return respuesta(200, "Validación de caja realizada", svc.validar_caja(cajaId, sedeId))


@router.get("/catalogo/validar-producto", tags=[tag("HU-037"), tag("HU-043")],
            summary="Validar que el producto exista y esté activo (MOD-04/MOD-05 → MOD-02)")
def validar_producto(productoId: int, svc: ProductoService = Depends(producto_service)):
    return respuesta(200, "Validación de producto realizada", svc.validar_producto(productoId))


@router.get("/sedes/validar-sede-activa", tags=[tag("HU-038"), tag("HU-044")],
            summary="Validar sedes de origen y destino o sede receptora (MOD-04/MOD-05 → MOD-01)")
def validar_sede_activa(sedeOrigenId: int, sedeDestinoId: int | None = Query(None), db: Session = Depends(get_db)):
    repo = SedeRepository(db)

    def activa(i):
        s = repo.por_id(i)
        return bool(s and s.esta_activa())

    datos = {"sedeOrigenId": sedeOrigenId, "origenActiva": activa(sedeOrigenId)}
    if sedeDestinoId is not None:
        if sedeDestinoId == sedeOrigenId:
            return respuesta(400, "La sede de origen y la de destino deben ser distintas",
                             errores=[{"campo": "sedeDestinoId", "detalle": "Debe ser distinta de la sede de origen"}])
        datos |= {"sedeDestinoId": sedeDestinoId, "destinoActiva": activa(sedeDestinoId)}
    return respuesta(200, "Validación de sedes realizada", datos)


@router.get("/sedes/validar-sede-usuario", tags=[tag("HU-054")], summary="Validar la sede antes de asignarla a un usuario (MOD-06 → MOD-01)")
def validar_sede_usuario(sedeId: int, db: Session = Depends(get_db)):
    s = SedeRepository(db).por_id(sedeId)
    return respuesta(200, "Validación de sede realizada",
                     {"sedeId": sedeId, "existe": s is not None, "activa": bool(s and s.esta_activa())})
