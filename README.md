# outline-sage

RAG assistant untuk Outline wiki self-hosted. Model embedding, reranker, dan chat berjalan lokal (tidak ada API pihak ketiga). Retrieval hybrid dense (Qdrant) + sparse (Elasticsearch).

Dokumen produk dan teknis ada di `docs/`:

| Dokumen | Lokasi |
|---|---|
| PRD | `docs/business/PRD-001_outline-sage.md` |
| HLD | `docs/hld/` |
| TSD | `docs/tsd/` |
| FSD | `docs/fsd/` |

## Struktur

```
apps/
  api/   # Backend Python (FastAPI): sync worker, hybrid retrieval, chat
  web/   # Frontend Next.js: chat UI, citation panel
infra/   # docker-compose, deployment config
docs/    # PRD, HLD, TSD, FSD
```

Referensi arsitektur: [molyleaf/outline-rag](https://github.com/molyleaf/outline-rag) (Business Source License 1.1, tidak di-fork langsung). Deployment Outline yang jadi target integrasi: [docker-compose-collection/outline](https://github.com/SyahrulApr86/docker-compose-collection/tree/main/outline).
