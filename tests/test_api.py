"""Casos de prueba de las historias implementadas (ver la plantilla de cada HU)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_hu001_registrar_y_duplicado(client):
    datos = {"codigo": "BGA-04", "nombre": "Micromarket Cabecera", "direccion": "Calle 48 # 33-20", "ciudad": "Bucaramanga"}
    r = client.post("/api/v1/sedes/registrar-sede", json=datos)
    assert r.status_code == 201 and r.json()["datos"]["estado"] == "ACTIVA"
    r = client.post("/api/v1/sedes/registrar-sede", json=datos)
    assert r.status_code == 409 and r.json()["exito"] is False


def test_hu001_consultar_activas(client):
    r = client.get("/api/v1/sedes/consultar-sedes-activas")
    assert r.status_code == 200 and len(r.json()["datos"]) >= 1


def test_hu002_caja_y_validar_caja(client):
    r = client.post("/api/v1/sedes/registrar-caja-pos", json={"sede_id": 1, "codigo": "CAJA-01", "serial": "SN-1"})
    assert r.status_code == 201
    r = client.get("/internal/sedes/validar-caja", params={"cajaId": 1, "sedeId": 1})
    assert r.json()["datos"]["activa"] is True


def test_hu005_hu007_producto_precio(client):
    p = {"nombre": "Arroz Diana 500 g", "marca": "Diana", "categoria": "Granos", "codigo_barras": "7702511000014", "precio": 3200, "tasa_iva": 5}
    assert client.post("/api/v1/catalogo/registrar-producto", json=p).status_code == 201
    r = client.get("/api/v1/catalogo/consultar-precio-por-codigo-de-barras", params={"codigo": "7702511000014"})
    assert r.status_code == 200 and float(r.json()["datos"]["precio"]) == 3200
    r = client.put("/api/v1/catalogo/actualizar-tarifa-de-producto", json={"producto_id": 1, "precio": 0})
    assert r.status_code == 422 and r.json()["errores"][0]["regla"] == "RN-08"


def test_hu001_inactivar_sede(client):
    r = client.delete("/api/v1/sedes/inactivar-sede", params={"sede_id": 1})
    assert r.status_code == 200 and r.json()["datos"]["estado"] == "INACTIVA"
    r = client.post("/api/v1/sedes/registrar-caja-pos", json={"sede_id": 1, "codigo": "CAJA-02", "serial": "SN-2"})
    assert r.status_code == 422


def test_planificado_responde_501(client):
    r = client.post("/api/v1/ventas/abrir-turno-de-caja")
    assert r.status_code == 501 and r.json()["exito"] is False
