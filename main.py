"""Micromarket – Web Service POS y Control de Inventario (FastAPI, arquitectura en capas).

Ejecutar:  uvicorn main:app --reload --host 127.0.0.1 --port 8000
Swagger:   http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from api.router import router as product_router  # ← Guía: router de productos (HU-005)
from app.api.historias import tags_openapi
from app.api.routers import catalogo, internas, sedes
from app.api.routers.planificadas import incluir_planificadas
from app.core.config import settings
from app.core.database import Base, engine
from app.core.respuesta import respuesta
from app.domain import models  # noqa: F401  (registra las entidades)
from app.domain.exceptions import ErrorDominio

Base.metadata.create_all(bind=engine)

# Crea la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Web Service REST de la cadena **Micromarket** (UTS · Web Services).\n\n"
        "Los endpoints están agrupados por **historia de usuario** (HU-001 a HU-060). "
        "✅ = implementada en este incremento · 🕓 = planificada (responde 501 hasta su sprint).\n\n"
        "Arquitectura en capas: API → Service → Domain → Repository."
    ),
    openapi_tags=tags_openapi(),
)


@app.exception_handler(ErrorDominio)
def manejar_error_dominio(_: Request, exc: ErrorDominio):
    return respuesta(exc.codigo, exc.mensaje,
                     errores=[{"campo": exc.campo, "regla": exc.regla, "detalle": exc.mensaje}])


@app.exception_handler(RequestValidationError)
def manejar_validacion(_: Request, exc: RequestValidationError):
    errores = [{"campo": ".".join(str(p) for p in e["loc"][1:]), "detalle": e["msg"]} for e in exc.errors()]
    return respuesta(400, "Datos de entrada no válidos", errores=errores)


# Endpoint raíz de bienvenida  ← Guía
@app.get("/", tags=["Sistema"])
def root():
    return {"message": "¡API Micromarket funcionando! 🚀"}


@app.get("/health", tags=["Sistema"], summary="Health check")
def health():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.APP_ENV}


# Registra los routers  ← Guía: include_router(router)
app.include_router(product_router)
for r in (sedes.router, catalogo.router, internas.router):
    app.include_router(r)

_esquema = app.openapi()
_implementadas = {(m.upper(), ruta) for ruta, ops in _esquema["paths"].items() for m in ops}
app.openapi_schema = None
app.include_router(incluir_planificadas(_implementadas))