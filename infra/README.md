# infra

Deployment outline-sage lewat docker compose, terpisah dari deployment Outline yang sudah ada di [docker-compose-collection/outline](https://github.com/SyahrulApr86/docker-compose-collection/tree/main/outline).

## Prasyarat

- Outline + Keycloak dari `docker-compose-collection/outline` sudah jalan.
- Realm Keycloak punya client OIDC baru untuk outline-sage: Client ID `outline-sage` (atau sesuaikan `SAGE_KEYCLOAK_CLIENT_ID`), Valid redirect URI `${SAGE_PUBLIC_URL}/api/auth/callback/keycloak`.
- Outline API token dengan scope baca dokumen dan collection.
- GPU host dengan driver NVIDIA untuk vLLM dan TEI.

## Setup

```bash
cp .env.example .env
```

Isi `.env`:
- `OUTLINE_API_URL`, `OUTLINE_API_TOKEN`, `OUTLINE_WEBHOOK_SECRET` — samakan `OUTLINE_WEBHOOK_SECRET` dengan konfigurasi webhook di Outline.
- `KEYCLOAK_ISSUER` — issuer realm Keycloak yang sama dengan Outline.
- `SAGE_KEYCLOAK_CLIENT_ID`, `SAGE_KEYCLOAK_CLIENT_SECRET` — dari client OIDC yang dibuat di realm itu.
- `SAGE_AUTH_SECRET` — `openssl rand -hex 32`.
- `SAGE_PUBLIC_URL` — alamat publik Web App.

Jalankan (build dari source):

```bash
docker compose up -d --build
```

Atau pakai image yang sudah di-build lewat CI ke GHCR (tidak perlu clone/build source sama sekali, tinggal `.env` dan dua file compose ini):

```bash
docker compose -f docker-compose.yml -f docker-compose.images.yml up -d
```

Image di-build otomatis oleh `.github/workflows/docker-publish.yml` tiap push ke `main`, tersedia di:
- `ghcr.io/syahrulapr86/outline-sage-api:main`
- `ghcr.io/syahrulapr86/outline-sage-web:main`

Daftarkan webhook Outline mengarah ke `http://<host>:8000/internal/webhooks/outline` setelah `outline-sage-api` sehat.

## Catatan

- Qdrant, Elasticsearch, dan Postgres metadata sage berbagi resource dengan bebas (tidak dibatasi eksplisit), volume disimpan di `./data/`.
- Redis outline-sage terpisah dari Redis Outline (instance sendiri), memakai `--notify-keyspace-events Ex` untuk debounce event-driven.
- Sync Worker (`outline-sage-sync-worker`) dan API Service (`outline-sage-api`) adalah container terpisah dari image yang sama, supaya restart salah satu tidak mengganggu yang lain.
- vLLM dan TEI (embedding, reranker) berbagi GPU yang sama (`device_ids: ["0"]`). Model dan quantization di `command:` masing-masing service bisa disesuaikan.
