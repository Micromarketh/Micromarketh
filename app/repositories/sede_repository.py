"""Capa Repository: acceso a datos de sedes y cajas."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import Caja, Sede


class SedeRepository:
    def __init__(self, db: Session):
        self.db = db

    def por_id(self, sede_id: int) -> Sede | None:
        return self.db.get(Sede, sede_id)

    def por_codigo(self, codigo: str) -> Sede | None:
        return self.db.scalar(select(Sede).where(Sede.codigo == codigo))

    def activas(self, ciudad: str | None = None) -> list[Sede]:
        consulta = select(Sede).where(Sede.estado == "ACTIVA")
        if ciudad:
            consulta = consulta.where(Sede.ciudad.ilike(ciudad))
        return list(self.db.scalars(consulta.order_by(Sede.codigo)))

    def guardar(self, sede: Sede) -> Sede:
        self.db.add(sede)
        self.db.commit()
        self.db.refresh(sede)
        return sede


class CajaRepository:
    def __init__(self, db: Session):
        self.db = db

    def por_id(self, caja_id: int) -> Caja | None:
        return self.db.get(Caja, caja_id)

    def por_sede_y_codigo(self, sede_id: int, codigo: str) -> Caja | None:
        return self.db.scalar(select(Caja).where(Caja.sede_id == sede_id, Caja.codigo == codigo))

    def por_sede(self, sede_id: int) -> list[Caja]:
        return list(self.db.scalars(select(Caja).where(Caja.sede_id == sede_id).order_by(Caja.codigo)))

    def guardar(self, caja: Caja) -> Caja:
        self.db.add(caja)
        self.db.commit()
        self.db.refresh(caja)
        return caja
