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

- Qdrant, Elasticsearch, dan Postgres metadata sage berbagi resource dengan bebas (tidak dibatasi eksplisit), volume disimpan di `./data/`. Elasticsearch butuh direktori data dimiliki uid 1000 (`docker run --rm -v ./data/elasticsearch:/data alpine chown -R 1000:1000 /data`), bukan root, kalau tidak ES gagal start dengan error node lock.
- Redis outline-sage terpisah dari Redis Outline (instance sendiri), memakai `--notify-keyspace-events Ex` untuk debounce event-driven.
- Sync Worker (`outline-sage-sync-worker`) dan API Service (`outline-sage-api`) adalah container terpisah dari image yang sama, supaya restart salah satu tidak mengganggu yang lain.
- vLLM dan TEI (embedding, reranker) berbagi GPU yang sama (`device_ids: ["0"]`). Model dan quantization di `command:` masing-masing service bisa disesuaikan.
- vLLM `--quantization awq` butuh checkpoint yang sudah di-AWQ-quantize sebelumnya (bukan checkpoint biasa). Dipakai `--quantization bitsandbytes --load-format bitsandbytes` supaya bisa kuantisasi on-the-fly dari checkpoint biasa seperti `Qwen/Qwen3-14B`.
- Image TEI resmi (`ghcr.io/huggingface/text-embeddings-inference`) belum mendukung GPU Blackwell (compute capability 120, contoh RTX 5090 dan RTX PRO 4000 Blackwell) per pertengahan 2026 ([issue #640](https://github.com/huggingface/text-embeddings-inference/issues/640)). Kalau GPU host pakai arsitektur Blackwell, build image sendiri dari source:
  ```bash
  git clone --depth 1 https://github.com/huggingface/text-embeddings-inference.git
  cd text-embeddings-inference
  docker build -f Dockerfile-cuda --build-arg CUDA_COMPUTE_CAP=120 -t outline-sage-tei-blackwell:latest .
  ```
  lalu ganti `image:` di `outline-sage-tei-embed` dan `outline-sage-tei-rerank` ke `outline-sage-tei-blackwell:latest`. Build ini murni lokal (compile Rust + CUDA), makan waktu cukup lama, dan tidak di-push ke registry mana pun oleh workflow CI di repo ini.
