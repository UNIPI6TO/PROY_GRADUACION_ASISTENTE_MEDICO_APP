AGENTS.md
# Proyecto
Asistente de Orientación en Salud Pública sobre Dengue y Arbovirosis (Grupo 5)
## Comandos
- Instalar Backend: pip install -r requirements.txt
- Probar Backend: pytest -q
## Reglas
- Python 3.12; nada fuera de requirements.
- No modifiques las pruebas sin pedirlo.
- Claves solo en variables de entorno.
- Nunca datos personales reales.
- Usa principios SOLID enfocate en el de responsabilidad única.
- Respetar esta estructura para el proyecto 
```text
proyecto/
├── app/
│   ├── main.py               # FastAPI, rutas
│   ├── schemas.py            # modelos Pydantic
│   ├── services/
│   │   ├── llm.py            # cliente del modelo
│   │   ├── retriever.py      # consulta a la base vectorial
│   │   └── agent.py          # bucle del agente
│   ├── tools/                # una herramienta por archivo
│   └── prompts/              # system_v1.md, system_v2.md ...
├── frontend/                 # Streamlit o web
├── scripts/
│   └── ingest.py             # ingesta reproducible
├── config/                   # tarifas, umbrales, calendarios
├── data/
│   ├── raw/                  # fuentes originales (o enlaces)
│   └── processed/            # fragmentos, si se exportan
├── eval/
│   ├── preguntas.csv         # conjunto de referencia
│   ├── casos_calculo.csv     # si aplica
│   └── run_eval.py
├── tests/                    # pytest
├── docs/
│   ├── 01-propuesta.md ... 09-decisiones.md
│   └── evidencias/semana-1 ... semana-4
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md