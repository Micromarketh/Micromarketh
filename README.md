# Micromarket – Web Service POS y Control de Inventario

Proyecto de la asignatura **Web Services** – Unidades Tecnológicas de Santander.
Autora: Elizabeth Riaño Calderón · Docente: Edward Alfonso Villamizar Vallejo.

## Descripción

Web Service backend, con arquitectura en capas y servicios REST en formato JSON, para una cadena de micromercados con varias sedes. Centraliza el catálogo, los precios y las promociones; controla el inventario por lote y fecha de vencimiento bajo la política FEFO; registra ventas, arqueos y facturación electrónica; y gestiona traslados entre sedes, compras a proveedores, seguridad con JWT y reportes gerenciales.

## Estructura funcional

| Módulo | Nombre |
|---|---|
| MOD-01 | Gestión de Sedes y Organización |
| MOD-02 | Gestión de Catálogo Central |
| MOD-03 | Ventas y Facturación POS |
| MOD-04 | Control de Inventario y Traslados |
| MOD-05 | Abastecimiento y Proveedores |
| MOD-06 | Seguridad y Control de Acceso |
| MOD-07 | Reportes y Analítica |

- 27 submódulos y 100 funcionalidades (FUN-01 a FUN-100).
- 30 APIs externas (103 endpoints) y 30 APIs internas entre módulos.
- 60 historias de usuario (HU-001 a HU-060), registradas como *issues* en el tablero de GitHub Projects.

## Stack tecnológico

FastAPI · SQLAlchemy · Pydantic v2 · Uvicorn · SQLite (desarrollo) / PostgreSQL · Python ≥ 3.10

## Arquitectura en capas

```
app/
├── api/           ← routers, schemas, dependencias (capa API)
├── services/      ← casos de uso y lógica de aplicación (capa Service)
├── domain/        ← entidades, reglas de negocio y excepciones (capa Domain)
├── repositories/  ← acceso a datos (capa Repository)
└── core/          ← configuración, base de datos y respuesta JSON estándar
```

## Cómo ejecutar

```bash
python -m venv venv
venv\Scripts\Activate.ps1          # Windows PowerShell  (macOS/Linux: source venv/bin/activate)
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env             # macOS/Linux: cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
- Pruebas: `pytest`

## Estado del proyecto

En Swagger UI los endpoints están agrupados por historia de usuario. ✅ = implementada (HU-001, HU-002, HU-005, HU-007 y las APIs internas HU-034, HU-037, HU-038, HU-043, HU-044, HU-054); 🕓 = planificada (responde 501 hasta su sprint).

## Planificación

Tablero de GitHub Projects: https://github.com/orgs/Micromarketh/projects/1
