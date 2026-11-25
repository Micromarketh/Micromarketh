"""Capa Service: casos de uso de MOD-02 Gestión de Catálogo Central (HU-005, HU-007)."""
from decimal import Decimal

from app.domain.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.domain.models import HistorialPrecio, Producto
from app.repositories.producto_repository import ProductoRepository


class ProductoService:
    def __init__(self, productos: ProductoRepository):
        self.productos = productos

    def obtener(self, producto_id: int) -> Producto:
        producto = self.productos.por_id(producto_id)
        if not producto:
            raise NoEncontrado("El producto no existe", campo="producto_id")
        return producto

    def _validar_codigo_unico(self, codigo: str, excepto_id: int | None = None) -> None:
        existente = self.productos.por_codigo_barras(codigo)
        if existente and existente.id != excepto_id:
            raise Conflicto("El código de barras ya está asignado a otro producto", regla="RN-08", campo="codigo_barras")

    # FUN-11
    def registrar(self, datos: dict) -> Producto:
        self._validar_codigo_unico(datos["codigo_barras"])
        if datos["precio"] <= 0:
            raise ReglaNegocio("El precio debe ser mayor que cero", regla="RN-08", campo="precio")
        producto = Producto(**datos)
        self.productos.guardar(producto)
        self.productos.guardar(HistorialPrecio(producto_id=producto.id, precio_anterior=0, precio_nuevo=producto.precio))
        return producto

    # FUN-12
    def catalogo(self, texto: str | None, pagina: int, tamano: int):
        return self.productos.catalogo(texto, pagina, tamano)

    # FUN-13
    def actualizar(self, producto_id: int, cambios: dict) -> Producto:
        producto = self.obtener(producto_id)
        for campo, valor in cambios.items():
            setattr(producto, campo, valor)
        self.productos.guardar(producto)
        return producto

    # FUN-14
    def inactivar(self, producto_id: int) -> Producto:
        producto = self.obtener(producto_id)
        if producto.tiene_movimientos:
            raise Conflicto("El producto tiene movimientos de inventario en curso")
        producto.estado = "INACTIVO"
        self.productos.guardar(producto)
        return producto

    # FUN-21
    def precio_por_codigo(self, codigo: str) -> Producto:
        producto = self.productos.por_codigo_barras(codigo)
        if not producto or producto.estado != "ACTIVO":
            raise NoEncontrado("No existe un producto activo con el código indicado", campo="codigo")
        return producto

    # FUN-22
    def actualizar_tarifa(self, producto_id: int, nuevo_precio: Decimal) -> Producto:
        producto = self.obtener(producto_id)
        anterior = producto.cambiar_precio(nuevo_precio)  # regla RN-08 en el dominio
        self.productos.guardar(producto, HistorialPrecio(producto_id=producto.id, precio_anterior=anterior, precio_nuevo=nuevo_precio))
        return producto

    # FUN-23
    def asignar_codigo(self, producto_id: int, codigo: str) -> Producto:
        producto = self.obtener(producto_id)
        self._validar_codigo_unico(codigo, excepto_id=producto.id)
        producto.codigo_barras = codigo
        self.productos.guardar(producto)
        return producto

    # API interna HU-037
    def validar_producto(self, producto_id: int) -> dict:
        p = self.productos.por_id(producto_id)
        if not p:
            return {"productoId": producto_id, "existe": False, "activo": False, "nombre": None, "categoria": None}
        return {"productoId": p.id, "existe": True, "activo": p.estado == "ACTIVO", "nombre": p.nombre, "categoria": p.categoria}
