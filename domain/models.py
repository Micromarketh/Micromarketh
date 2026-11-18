# CAPA DOMINIO — entidad Producto y reglas de negocio del micromercado
# No importa nada de FastAPI ni de base de datos.

from pydantic import BaseModel, Field, field_validator


# ── Schema de ENTRADA ─────────────────────────────────────────
class ProductoCreate(BaseModel):
    nombre:        str   = Field(..., min_length=2, description="Nombre del producto")
    marca:         str   = Field(..., min_length=2)
    categoria:     str   = Field(..., min_length=2)
    codigo_barras: str   = Field(..., min_length=8, max_length=14, description="8 a 14 dígitos")
    precio:        float = Field(..., gt=0, description="Precio mayor a 0")
    tasa_iva:      int   = Field(19, description="IVA: 0, 5 o 19")

    # REGLA: el código de barras solo tiene números
    @field_validator("codigo_barras")
    @classmethod
    def codigo_solo_numeros(cls, v):
        if not v.isdigit():
            raise ValueError("El código de barras solo puede tener números")
        return v

    # REGLA: tarifas de IVA válidas en Colombia
    @field_validator("tasa_iva")
    @classmethod
    def iva_valido(cls, v):
        if v not in (0, 5, 19):
            raise ValueError("La tasa de IVA debe ser 0, 5 o 19")
        return v

    # REGLA: precio con dos decimales máximo
    @field_validator("precio")
    @classmethod
    def precio_valido(cls, v):
        return round(v, 2)

    @field_validator("nombre", "marca", "categoria")
    @classmethod
    def limpiar_texto(cls, v):
        return v.strip().title()


# ── Schema de SALIDA ──────────────────────────────────────────
class ProductoResponse(BaseModel):
    id:             int
    nombre:         str
    marca:          str
    categoria:      str
    codigo_barras:  str
    precio:         float
    tasa_iva:       int
    precio_con_iva: float   # calculado
    estado:         str

    class Config:
        from_attributes = True


# ── Entidad del dominio ───────────────────────────────────────
class Producto:
    def __init__(self, id: int, nombre: str, marca: str, categoria: str,
                 codigo_barras: str, precio: float, tasa_iva: int,
                 estado: str = "ACTIVO"):
        self.id            = id
        self.nombre        = nombre
        self.marca         = marca
        self.categoria     = categoria
        self.codigo_barras = codigo_barras
        self.precio        = precio
        self.tasa_iva      = tasa_iva
        self.estado        = estado

    # REGLA: ¿el producto se puede vender?
    def esta_activo(self) -> bool:
        return self.estado == "ACTIVO"

    # REGLA: precio final con IVA
    def precio_con_iva(self) -> float:
        return round(self.precio * (1 + self.tasa_iva / 100), 2)

    # REGLA: no se inactiva dos veces
    def inactivar(self):
        if not self.esta_activo():
            raise ValueError("El producto ya está inactivo")
        self.estado = "INACTIVO"

    def to_response(self) -> dict:
        return {
            "id":             self.id,
            "nombre":         self.nombre,
            "marca":          self.marca,
            "categoria":      self.categoria,
            "codigo_barras":  self.codigo_barras,
            "precio":         self.precio,
            "tasa_iva":       self.tasa_iva,
            "precio_con_iva": self.precio_con_iva(),
            "estado":         self.estado,
        }
    