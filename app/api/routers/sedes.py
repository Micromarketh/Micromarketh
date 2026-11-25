"""Capa API: MOD-01 Gestión de Sedes y Organización (HU-001 API Sedes, HU-002 API Cajas POS)."""
from fastapi import APIRouter, Depends, Query

from app.api.dependencies import caja_service, sede_service
from app.api.historias import tag
from app.api.schemas import CajaCrear, CajaSalida, SedeActualizar, SedeCrear, SedeSalida
from app.core.respuesta import respuesta
from app.services.sede_service import CajaService, SedeService

router = APIRouter(prefix="/api/v1/sedes")
HU001, HU002 = tag("HU-001"), tag("HU-002")


@router.post("/registrar-sede", tags=[HU001], summary="FUN-01 · Registrar Sede", status_code=201)
def registrar_sede(datos: SedeCrear, svc: SedeService = Depends(sede_service)):
    sede = svc.registrar(datos.model_dump())
    return respuesta(201, "Sede registrada correctamente", SedeSalida.model_validate(sede))


@router.get("/consultar-sedes-activas", tags=[HU001], summary="FUN-02 · Consultar Sedes Activas")
def consultar_sedes_activas(ciudad: str | None = None, svc: SedeService = Depends(sede_service)):
    sedes = [SedeSalida.model_validate(s) for s in svc.consultar_activas(ciudad)]
    return respuesta(200, f"{len(sedes)} sedes activas", sedes)


@router.put("/actualizar-datos-de-sede", tags=[HU001], summary="FUN-03 · Actualizar Datos de Sede")
def actualizar_sede(datos: SedeActualizar, sede_id: int = Query(...), svc: SedeService = Depends(sede_service)):
    sede = svc.actualizar(sede_id, datos.model_dump(exclude_none=True))
    return respuesta(200, "Sede actualizada correctamente", SedeSalida.model_validate(sede))


@router.delete("/inactivar-sede", tags=[HU001], summary="FUN-04 · Inactivar Sede")
def inactivar_sede(sede_id: int = Query(...), svc: SedeService = Depends(sede_service)):
    sede = svc.inactivar(sede_id)
    return respuesta(200, "Sede inactivada correctamente", SedeSalida.model_validate(sede))


@router.post("/registrar-caja-pos", tags=[HU002], summary="FUN-05 · Registrar Caja POS", status_code=201)
def registrar_caja(datos: CajaCrear, svc: CajaService = Depends(caja_service)):
    caja = svc.registrar(datos.sede_id, datos.codigo, datos.serial)
    return respuesta(201, "Caja registrada correctamente", CajaSalida.model_validate(caja))


@router.get("/consultar-cajas-por-sede", tags=[HU002], summary="FUN-06 · Consultar Cajas por Sede")
def consultar_cajas(codigo_sede: str = Query(..., examples=["BGA-04"]), svc: CajaService = Depends(caja_service)):
    cajas = [CajaSalida.model_validate(c) for c in svc.consultar_por_sede(codigo_sede)]
    return respuesta(200, f"{len(cajas)} cajas en la sede", cajas)


@router.delete("/inactivar-caja-pos", tags=[HU002], summary="FUN-07 · Inactivar Caja POS")
def inactivar_caja(caja_id: int = Query(...), svc: CajaService = Depends(caja_service)):
    caja = svc.inactivar(caja_id)
    return respuesta(200, "Caja inactivada correctamente", CajaSalida.model_validate(caja))
