"""Capa API: construcción de servicios con sus repositorios (inyección de dependencias)."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.producto_repository import ProductoRepository
from app.repositories.sede_repository import CajaRepository, SedeRepository
from app.services.producto_service import ProductoService
from app.services.sede_service import CajaService, SedeService


def sede_service(db: Session = Depends(get_db)) -> SedeService:
    return SedeService(SedeRepository(db), CajaRepository(db))


def caja_service(db: Session = Depends(get_db)) -> CajaService:
    return CajaService(SedeRepository(db), CajaRepository(db))


def producto_service(db: Session = Depends(get_db)) -> ProductoService:
    return ProductoService(ProductoRepository(db))
