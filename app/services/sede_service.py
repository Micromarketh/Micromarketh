"""Capa Service: casos de uso de MOD-01 Gestión de Sedes y Organización (HU-001, HU-002)."""
from app.domain.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.domain.models import Caja, Sede
from app.repositories.sede_repository import CajaRepository, SedeRepository


def traslados_pendientes(sede_id: int) -> int:
    """API interna /internal/inventario/verificar-traslados-pendientes (MOD-04).
    Simulada hasta que exista el módulo de Inventario (Sprint 2)."""
    return 0


class SedeService:
    def __init__(self, sedes: SedeRepository, cajas: CajaRepository):
        self.sedes = sedes
        self.cajas = cajas

    def obtener(self, sede_id: int) -> Sede:
        sede = self.sedes.por_id(sede_id)
        if not sede:
            raise NoEncontrado("La sede no existe", campo="sede_id")
        return sede

    # FUN-01
    def registrar(self, datos: dict) -> Sede:
        if self.sedes.por_codigo(datos["codigo"]):
            raise Conflicto("Ya existe una sede con el código indicado", campo="codigo")
        return self.sedes.guardar(Sede(**datos))

    # FUN-02
    def consultar_activas(self, ciudad: str | None) -> list[Sede]:
        return self.sedes.activas(ciudad)

    # FUN-03
    def actualizar(self, sede_id: int, cambios: dict) -> Sede:
        sede = self.obtener(sede_id)
        if not sede.esta_activa():
            raise ReglaNegocio("Solo se pueden actualizar sedes activas")
        for campo, valor in cambios.items():
            setattr(sede, campo, valor)
        return self.sedes.guardar(sede)

    # FUN-04
    def inactivar(self, sede_id: int) -> Sede:
        sede = self.obtener(sede_id)
        if any(c.turno_abierto for c in sede.cajas):
            raise Conflicto("La sede tiene cajas con turno abierto y no puede inactivarse")
        if traslados_pendientes(sede.id) > 0:
            raise Conflicto("La sede tiene traslados pendientes y no puede inactivarse")
        sede.estado = "INACTIVA"
        return self.sedes.guardar(sede)


class CajaService:
    def __init__(self, sedes: SedeRepository, cajas: CajaRepository):
        self.sedes = sedes
        self.cajas = cajas

    # FUN-05
    def registrar(self, sede_id: int, codigo: str, serial: str) -> Caja:
        sede = self.sedes.por_id(sede_id)
        if not sede:
            raise NoEncontrado("La sede no existe", campo="sede_id")
        if not sede.esta_activa():
            raise ReglaNegocio("No se pueden registrar cajas en una sede inactiva")
        if self.cajas.por_sede_y_codigo(sede_id, codigo):
            raise Conflicto("Ya existe una caja con ese código en la sede", campo="codigo")
        return self.cajas.guardar(Caja(sede_id=sede_id, codigo=codigo, serial=serial))

    # FUN-06
    def consultar_por_sede(self, codigo_sede: str) -> list[Caja]:
        sede = self.sedes.por_codigo(codigo_sede)
        if not sede:
            raise NoEncontrado("La sede no existe", campo="codigo_sede")
        return self.cajas.por_sede(sede.id)

    # FUN-07
    def inactivar(self, caja_id: int) -> Caja:
        caja = self.cajas.por_id(caja_id)
        if not caja:
            raise NoEncontrado("La caja no existe", campo="caja_id")
        if caja.turno_abierto:
            raise Conflicto("La caja tiene un turno abierto y no puede inactivarse")
        caja.estado = "INACTIVA"
        return self.cajas.guardar(caja)

    # API interna HU-034
    def validar_caja(self, caja_id: int, sede_id: int) -> dict:
        caja = self.cajas.por_id(caja_id)
        if not caja:
            raise NoEncontrado("La caja no existe", campo="cajaId")
        activa = caja.estado == "ACTIVA" and caja.sede_id == sede_id and caja.sede.esta_activa()
        return {"cajaId": caja.id, "sedeId": sede_id, "activa": activa, "topeEfectivo": caja.sede.tope_efectivo}
