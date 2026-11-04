"""Entidades del dominio (MOD-01 Sedes y MOD-02 Catálogo) y sus reglas de negocio."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.exceptions import ReglaNegocio


class Sede(Base):
    __tablename__ = "sedes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    direccion: Mapped[str] = mapped_column(String(150))
    ciudad: Mapped[str] = mapped_column(String(60))
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tope_efectivo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("1500000"))
    estado: Mapped[str] = mapped_column(String(10), default="ACTIVA")
    cajas: Mapped[list["Caja"]] = relationship(back_populates="sede")

    def esta_activa(self) -> bool:
        return self.estado == "ACTIVA"


class Caja(Base):
    __tablename__ = "cajas"
    __table_args__ = (UniqueConstraint("sede_id", "codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    sede_id: Mapped[int] = mapped_column(ForeignKey("sedes.id"))
    codigo: Mapped[str] = mapped_column(String(20))
    serial: Mapped[str] = mapped_column(String(50))
    estado: Mapped[str] = mapped_column(String(10), default="ACTIVA")  # ACTIVA, BLOQUEADA, INACTIVA
    # Simulado hasta HU-013 (Turnos de caja, Sprint 3)
    turno_abierto: Mapped[bool] = mapped_column(Boolean, default=False)
    sede: Mapped[Sede] = relationship(back_populates="cajas")


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    marca: Mapped[str] = mapped_column(String(60))
    categoria: Mapped[str] = mapped_column(String(60))
    codigo_barras: Mapped[str] = mapped_column(String(14), unique=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    tasa_iva: Mapped[int] = mapped_column(Integer, default=19)
    estado: Mapped[str] = mapped_column(String(10), default="ACTIVO")
    # Simulado hasta MOD-04 (Inventario, Sprint 2)
    tiene_movimientos: Mapped[bool] = mapped_column(Boolean, default=False)

    def cambiar_precio(self, nuevo: Decimal) -> Decimal:
        """RN-08: todo precio debe ser mayor que cero; devuelve el precio anterior."""
        if nuevo <= 0:
            raise ReglaNegocio("El precio debe ser mayor que cero", regla="RN-08", campo="precio")
        anterior = self.precio
        self.precio = nuevo
        return anterior


class HistorialPrecio(Base):
    __tablename__ = "historial_precios"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    precio_anterior: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    precio_nuevo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
