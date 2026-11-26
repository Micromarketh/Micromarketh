from fastapi import FastAPI
from api.router import router as product_router
from api.auth_router import router as auth_router
from api.seguridad_interna_router import router as seguridad_interna_router

app = FastAPI(
    title="Micromarket Web Service",
    version="1.0.0",
    description="Servicio web de la cadena de micromercados: catálogo, sedes, inventario y ventas. Arquitectura de cuatro capas (domain, repository, service, api).",
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(seguridad_interna_router)


@app.get("/", summary="Inicio")
def inicio():
    return {"message": "¡API Micromarket funcionando! 🚀"}


@app.get("/health", summary="Health")
def health():
    return {"status": "ok"}