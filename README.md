# flyrankAI-internship

Monorepo con todos los proyectos de la internship en flyrankAI.

## Proyectos

| Carpeta | Descripción |
| --- | --- |
| [`W5A9-politeScraper`](./W5A9-politeScraper) | Scraper "educado" (respeta robots.txt, rate limiting, backoff). |
| [`W7A17-aiAPI`](./W7A17-aiAPI) | Task API en FastAPI (CRUD + auth Supabase) con un endpoint LLM: `POST /tasks/triage` devuelve JSON validado contra un schema, con timeout, retries, cost log y kill switch. |
