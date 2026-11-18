from fastapi import FastAPI
from api.router import router as product_router

app = FastAPI(
    title="Micromarket Web Service",
    version="1.0.0",
    description="Servicio web de la cadena de micromercados: catálogo, sedes, inventario y ventas. Arquitectura de cuatro capas (domain, repository, service, api).",
)

app.include_router(product_router)


@app.get("/", summary="Inicio")
def inicio():
    return {"message": "¡API Micromarket funcionando! 🚀"}


@app.get("/health", summary="Health")
def health():
    return {"status": "ok"}
