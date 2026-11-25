"""Capa API: endpoints del Inventario de APIs que aún no están implementados.
Se registran para que Swagger UI muestre el alcance completo del proyecto organizado por historias
de usuario. Responden 501 (Not Implemented) hasta que se desarrollen en su sprint."""
import re

from fastapi import APIRouter

from app.api.historias import HISTORIAS, tag
from app.api.routers.planificadas_data import ENDPOINTS
from app.core.respuesta import respuesta

router = APIRouter()
_sprint = {h["hu"]: h["sprint"] for h in HISTORIAS}


def _registrar(ep: dict) -> None:
    hu = ep["hus"][0]

    def no_implementado():
        return respuesta(501, f"Endpoint planificado ({_sprint[hu]}); aún no está implementado.",
                         errores=[{"detalle": f"Se implementará con la historia {hu}."}])

    router.add_api_route(
        ep["ruta"], no_implementado, methods=[ep["metodo"]],
        tags=[tag(h) for h in ep["hus"]],
        summary=f"{ep['funcionalidad']}  [planificado]",
        description=(f"**Propósito:** {ep['proposito']}\n\n**Entrada:** {ep['entrada']}\n\n"
                     f"**Respuesta esperada:** {ep['salida']}\n\n**Estado:** planificado · {_sprint[hu]} · {ep['id_api']}"),
        operation_id=re.sub(r"\W+", "_", f"{ep['metodo']}_{ep['ruta']}").strip("_").lower(),
    )


def incluir_planificadas(implementadas: set[tuple[str, str]]) -> APIRouter:
    for ep in ENDPOINTS:
        if (ep["metodo"], ep["ruta"]) not in implementadas:
            _registrar(ep)
    return router
