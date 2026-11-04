"""Capa Repository: acceso a datos del catálogo."""
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.models import HistorialPrecio, Producto


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def por_id(self, producto_id: int) -> Producto | None:
        return self.db.get(Producto, producto_id)

    def por_codigo_barras(self, codigo: str) -> Producto | None:
        return self.db.scalar(select(Producto).where(Producto.codigo_barras == codigo))

    def catalogo(self, texto: str | None, pagina: int, tamano: int) -> tuple[list[Producto], int]:
        consulta = select(Producto).where(Producto.estado == "ACTIVO")
        if texto:
            patron = f"%{texto}%"
            consulta = consulta.where(or_(Producto.nombre.ilike(patron), Producto.marca.ilike(patron)))
        total = self.db.scalar(select(func.count()).select_from(consulta.subquery()))
        filas = self.db.scalars(consulta.order_by(Producto.nombre).offset((pagina - 1) * tamano).limit(tamano))
        return list(filas), total or 0

    def historial(self, producto_id: int) -> list[HistorialPrecio]:
        return list(self.db.scalars(
            select(HistorialPrecio).where(HistorialPrecio.producto_id == producto_id).order_by(HistorialPrecio.fecha)))

    def guardar(self, *objetos) -> None:
        self.db.add_all(objetos)
        self.db.commit()
        for o in objetos:
            self.db.refresh(o)
