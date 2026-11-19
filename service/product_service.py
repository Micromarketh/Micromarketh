# CAPA SERVICIO — orquesta dominio + repositorio
# No importa nada de FastAPI.

import math
from domain.models import ProductoCreate, ProductoResponse, CatalogoPaginado
from repository.product_repo import ProductoRepository


class ProductoNoEncontrado(Exception):
    """El producto no existe (la API lo convierte en 404)."""


class ProductoEnConflicto(Exception):
    """Choca con una regla del negocio (la API lo convierte en 409)."""


class ProductoService:

    def __init__(self, repo: ProductoRepository):
        # Inyección de dependencia
        self.repo = repo

    def _buscar(self, id: int):
        p = self.repo.obtener_por_id(id)
        if not p:
            raise ProductoNoEncontrado(f"Producto {id} no encontrado")
        return p

    def listar(self, pagina: int = 1, tamano: int = 10) -> CatalogoPaginado:
        # Catálogo paginado: solo productos activos
        activos = [p for p in self.repo.obtener_todos() if p.esta_activo()]
        total = len(activos)
        inicio = (pagina - 1) * tamano
        items = activos[inicio:inicio + tamano]
        return CatalogoPaginado(
            pagina=pagina,
            tamano=tamano,
            total=total,
            total_paginas=math.ceil(total / tamano) if total else 0,
            productos=[ProductoResponse(**p.to_response()) for p in items],
        )

    def obtener(self, id: int) -> ProductoResponse:
        return ProductoResponse(**self._buscar(id).to_response())

    def crear(self, datos: ProductoCreate) -> ProductoResponse:
        # RN-08: el código de barras no se puede repetir
        if self.repo.obtener_por_codigo_barras(datos.codigo_barras):
            raise ProductoEnConflicto("El código de barras ya está asignado a otro producto")
        p = self.repo.crear(**datos.model_dump())
        return ProductoResponse(**p.to_response())

    def actualizar(self, id: int, datos: ProductoCreate) -> ProductoResponse:
        p = self._buscar(id)
        if not p.esta_activo():
            raise ValueError("No se puede actualizar un producto inactivo")
        otro = self.repo.obtener_por_codigo_barras(datos.codigo_barras)
        if otro and otro.id != id:
            raise ProductoEnConflicto("El código de barras ya está asignado a otro producto")
        p = self.repo.actualizar(id, **datos.model_dump())
        return ProductoResponse(**p.to_response())

    def inactivar(self, id: int) -> dict:
        p = self._buscar(id)
        # No se inactiva con movimientos de inventario en curso
        if not p.puede_inactivarse():
            raise ProductoEnConflicto("El producto tiene movimientos de inventario en curso")
        p.inactivar()   # la regla está en el dominio
        return {"mensaje": f"Producto {id} inactivado correctamente"}