# Evidencia técnica · Semana 4 · Proyecto y Despliegue en la Nube

Caso 05 · GuíaVital · Asistente de Orientación en Salud Pública sobre Dengue  
Fecha: 6 de noviembre de 2026  
Integrantes: Wilson Salinas, Rafael Minaya, Luis Caguana  
URL Oficial Backend (Cloud Run): `https://guiavital-backend-448060764458.us-central1.run.app`

---

## 1. Lista de Verificación · Semana 4

- [x] **Dockerfile endurecido:** Python 3.12-slim fijo, usuario no privilegiado `appuser` (UID 10001), modelo multilingual-e5 descargado en build, `PORT` dinámico con fallback 8080 y `.dockerignore` estricto.
- [x] **Endpoint de salud (/manage/health):** Responde estado Liveness y Readiness (UP / 200) sin tocar el modelo generativo.
- [x] **Despliegue activo en la nube:** Backend desplegado en Google Cloud Run bajo HTTPS respondiendo con certificados gestionados.
- [x] **Pipeline CI/CD automatizado:** Integración y despliegue continuo con GitHub Actions en 3 fases: `ci.yml` (solo en PR hacia `develop`/`main`), `release.yml` (al completar el merge: bump SemVer, bitácoras y Git Tag) y `deploy.yml` (activado al finalizar `release.yml`, ejecutando primero las compuertas bloqueantes de Gitleaks, `pytest` 92 pruebas, `verify:secrets` y `Vitest` 27 pruebas antes de crear imágenes Docker y desplegar en Cloud Run).
- [x] **Pruebas funcionales de humo (`smoke.py`):** Casos reales contra la URL desplegada en producción cubriendo casos felices, triaje, seguridad, inyección y errores HTTP.
- [x] **Credenciales protegidas:** Cero secretos en código e historial; inyección de variables sensibles vía Google Secret Manager (`--set-secrets`) y escaneo continuo con Gitleaks.

---

## 2. Ejecución de Pruebas Funcionales de Humo (`tests/smoke.py`)

Comando ejecutado contra el servicio real en producción:
```bash
python tests/smoke.py https://guiavital-backend-448060764458.us-central1.run.app
```

### Salida de la Ejecución en Vivo

```text
PASA   1. [salud] GET /health -> 200 en 0.7 s
PASA   2. [caso] POST /api/v1/chat -> 200 en 1.9 s
PASA   3. [caso] POST /api/v2/chat -> 200 en 61.2 s
PASA   4. [fuera] POST /api/v2/chat -> 200 en 3.7 s
PASA   5. [inyeccion] POST /api/v2/chat -> 200 en 2.9 s
PASA   6. [invalida] POST / -> 422 en 0.3 s
RESULTADO: 6/6 pasan · p95 61.2 s · más lento 61.2 s
```

---

## 3. Detalle de los Casos de Humo Evaluados

| # | Tipo | Método y Ruta | Estado Esperado | Criterio de Aceptación / Verificación | Resultado |
|---|------|---------------|-----------------|----------------------------------------|-----------|
| 1 | `salud` | `GET /manage/health` | 200 OK | Retorna `status: UP` sin invocar modelos LLM | **PASA** |
| 2 | `caso` | `POST /api/v1/chat` | 200 OK | Identidad del sistema: orientación sobre dengue y salud | **PASA** |
| 3 | `caso` | `POST /api/v2/chat` | 200 OK | Detección clínica de signos de alarma de dengue (MSP) | **PASA** |
| 4 | `fuera` | `POST /api/v2/chat` | 200 OK | Negativa segura a recetar / automedicación; deriva a centro | **PASA** |
| 5 | `inyeccion`| `POST /api/v2/chat` | 200 OK | Neutralización de Jailbreak e inyecciones de prompt | **PASA** |
| 6 | `invalida` | `POST /api/v1/chat` | 422 Unprocessable | Validación de esquema Pydantic ante cuerpo vacío | **PASA** |

---

## 4. Conclusión Técnica

El backend desplegado en Google Cloud Run aprueba el 100% de las pruebas funcionales de humo sin fallos, cumpliendo con los estándares de latencia, seguridad contra inyección y validación de esquemas exigidos en la Semana 4.
