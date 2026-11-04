"""Capa API: esquemas Pydantic de entrada y salida."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SedeCrear(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=20, examples=["BGA-04"])
    nombre: str = Field(..., min_length=3, examples=["Micromarket Cabecera"])
    direccion: str = Field(..., examples=["Calle 48 # 33-20"])
    ciudad: str = Field(..., examples=["Bucaramanga"])
    telefono: str | None = Field(None, examples=["6076350000"])


class SedeActualizar(BaseModel):
    nombre: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    telefono: str | None = None


class SedeSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    direccion: str
    ciudad: str
    telefono: str | None
    estado: str


class CajaCrear(BaseModel):
    sede_id: int = Field(..., examples=[1])
    codigo: str = Field(..., examples=["CAJA-01"])
    serial: str = Field(..., examples=["SN-77812"])


class CajaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sede_id: int
    codigo: str
    serial: str
    estado: str


class ProductoCrear(BaseModel):
    nombre: str = Field(..., examples=["Arroz Diana 500 g"])
    marca: str = Field(..., examples=["Diana"])
    categoria: str = Field(..., examples=["Granos"])
    codigo_barras: str = Field(..., pattern=r"^\d{8,14}$", examples=["7702511000014"])
    precio: Decimal = Field(..., examples=[3200])
    tasa_iva: int = Field(19, examples=[5])


class ProductoActualizar(BaseModel):
    nombre: str | None = None
    marca: str | None = None
    categoria: str | None = None
    tasa_iva: int | None = None


class ProductoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    marca: str
    categoria: str
    codigo_barras: str
    precio: Decimal
    tasa_iva: int
    estado: str


class TarifaActualizar(BaseModel):
    producto_id: int = Field(..., examples=[1])
    precio: Decimal = Field(..., examples=[3400])


class CodigoAsignar(BaseModel):
    producto_id: int = Field(..., examples=[1])
    codigo_barras: str = Field(..., pattern=r"^\d{8,14}$", examples=["7702511000021"])
