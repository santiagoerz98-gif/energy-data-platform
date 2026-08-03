# Guia de Setup e Instalacion

## 1. Objetivo

Esta guia describe como preparar un entorno local para ejecutar el pipeline de Energy Data Platform.

## 2. Requisitos previos

- Windows, Linux o macOS
- Python 3.11 o superior
- PostgreSQL disponible
- API key de ESIOS

## 3. Crear y activar entorno virtual

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 5. Configurar variables de entorno

Crear un archivo `.env` en la raiz del proyecto:

```env
ESIOS_API_KEY=tu_api_key
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/energy_dw
```

## 6. Inicializar base de datos

Ejecutar scripts SQL en este orden:

1. `database/schema.sql`
2. `database/create_dim_time.sql`

Opcional para poblar hechos/dimensiones desde staging:

3. `database/populate_dw.sql`

## 7. Verificacion rapida

Probar una ejecucion corta:

```bash
python -m pipeline.run_pipeline 1293 --start-date 2026-08-01 --end-date 2026-08-01
```

Si finaliza correctamente, deberias ver:

- archivo raw en `data/raw/esios/...`
- reporte de calidad en `data/raw/processed/reports/`
- registros en `staging.demand`

## 8. Problemas frecuentes

- Error de autenticacion ESIOS:
  - revisar `ESIOS_API_KEY`.
- Error de conexion a PostgreSQL:
  - revisar `DATABASE_URL` y estado del servidor.
- Dependencias no instaladas:
  - confirmar que el entorno virtual este activo.
