from pydantic import BaseModel
from typing import Optional


# ── Modelo base: campos comunes ──────────────────
class ProductBase(BaseModel):
    nombre: str
    marca: str
    categoria: str
    codigo_barras: str
    precio: float
    tasa_iva: int = 19


# ── Para CREAR un producto (sin ID) ─────────────
class ProductCreate(ProductBase):
    pass


# ── Respuesta completa (con ID) ──────────────────
class Product(ProductBase):
    id: int
    estado: str = "ACTIVO"

    class Config:
        # Permite leer datos desde atributos de objeto
        from_attributes = True
        