# Evidencia técnica · Semana 2

Caso 05 · GuíaVital · Revisión 2: viernes 23 de octubre de 2026

## Lista de verificación

- [x] Arquitectura y decisiones documentadas (docs/03-arquitectura.md y docs/09-decisiones.md (ADR-001 a 003))
- [x] La clave fuera del código desde el primer commit (.env en .gitignore, .env.example sin valores, historial limpio)
- [ ] Un servicio que encapsula al modelo (app/services/llm.py: cambiar de proveedor no toca los endpoints)
- [ ] Endpoint principal con entrada validada (POST /chat, /analizar, /clasificar o /planificar con Pydantic)
- [ ] System prompt en archivo y tres versiones comparadas (app/prompts/system_v1.md … v3 y docs/05-prompts.md)
- [ ] Errores del proveedor bajo control (429 con reintentos y espera creciente, tiempo agotado, respuesta vacía)
- [ ] Registro por solicitud (tokens consumidos y tiempo de respuesta en cada llamada)
- [ ] Pruebas automatizadas con un doble del modelo (tests/ con pytest; corren sin internet y sin gastar API)
- [ ] Frontend propio del producto (chat, formulario con informe, tablero, calendario o mapa)
- [ ] README que permite ejecutar el proyecto (instalación, variables de entorno y cómo correr backend y frontend)
- [ ] Evidencia técnica de la semana (docs/evidencias/semana-2/: capturas, prompts, decisiones y problemas)

## Bitácora diaria

| Día | Qué funciona (captura) | Problema encontrado | Cómo lo resolvimos | Quién |
|---|---|---|---|---|
| Lun 19 | | | | |
| Mar 20 | | | | |
| Mié 21 | | | | |
| Jue 22 | | | | |
| Vie 23 | | | | |

## Capturas

Guarden las imágenes en esta misma carpeta y enlácenlas aquí.

## Respuestas preparadas para la revisión

1. ¿Dónde está la clave del modelo? _…_
2. ¿Qué pasa si el proveedor devuelve 429? _(cómo lo demostramos)_
3. ¿Por qué esa temperatura y ese límite de tokens? _…_
4. ¿Qué aprendimos al comparar los tres prompts? _…_
