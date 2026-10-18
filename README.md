# Multi-Container Backend Architecture

A decoupled, microservices-based backend system where **each component runs in its own separate Docker container**, communicating securely over an isolated internal Docker bridge network.

---

## Architecture Overview

![System Architecture](./image.png)

> **Note on "Backend Container":** The outer boundary shown in the diagram represents the **shared Docker internal network (backend cluster)**. Inside this network, each service runs in a **dedicated, isolated container** with independent lifecycles, resource allocations, and scaling.

### Multi-Container Topology

```
+====================================================================================================+
|                              Docker Internal Network (Bridge / Mesh)                               |
|                                                                                                    |
|  +--------------------+         +--------------------+         +--------------------+              |
|  | [Container 1]      |         | [Container 2]      |         | [Container 3]      |              |
|  | Redis Cache/Broker | ------> | Django App Server  | ------> | PostgreSQL (Auth)  |              |
|  | redis_cache_ofdb   |         | web_app            |         | postgres_db_use    |              |
|  | :6379              |         | :8000              |         | :5432              |              |
|  +--------------------+         +--------------------+         +--------------------+              |
|                                           |                              |                         |
|                                           |                              | (Auth & Schema)         |
|                                           v                              v                         |
|                                    [REST API / Admin]          +--------------------+              |
|                                           |                    | [Container 4]      |              |
|                                           |                    | MongoDB Document DB|              |
|                                           |                    | mongodb_service    |              |
|                                           |                    | :27017             |              |
|                                           |                    +--------------------+              |
|                                           |                              |                         |
|                                           |                              v (Live Feed / Chat Data) |
|                                           |                    +--------------------+              |
|                                           |                    | [Container 5]      |              |
|                                           |                    | Node.js Real-time  |              |
|                                           |                    | node_ws_server     |              |
|                                           |                    | :8080              |              |
|                                           |                    +--------------------+              |
+===========================================|==============================|=========================+
                                            |                              |
                                            | (HTTP / REST)                | (WebSocket / ws://)
                                            v                              v
                                +------------------------------------------------------+
                                |                        Client                        |
                                |            (Web Browser / Mobile App)                |
                                +------------------------------------------------------+
```

---

## Separate Container Breakdown

Each service is encapsulated in its own purpose-built container:

| # | Container Name | Service | Technology | Internal Port | Host Port | Purpose |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `web_app` | Django Server | Python 3.12 / Django 6 / Gunicorn | `8000` | `8000` | REST API, Auth, Business Logic, Admin |
| **2** | `node_websocket_server` | Real-time Gateway | Node.js 20 Alpine / `ws` | `8080` | `8080` | High-concurrency WebSockets, live events |
| **3** | `postgres_db_use` | Shared Auth DB | PostgreSQL 17 | `5432` | *(Internal)* | Relational source of truth for users & orgs |
| **4** | `redis_cache_ofdb` | Cache & Pub/Sub | Redis 7 Alpine | `6379` | `6379` | Throttle counters, caching, inter-service pub/sub |
| **5** | `mongodb_service` | Document DB | MongoDB 7 | `27017` | `27017` | High-write throughput for chat & event logs |

---

## Inter-Container Communication

Containers communicate directly by their **Docker service names** using Docker's embedded DNS:

- **Django -> Postgres:** `postgresql://postgres:postgres123@db:5432/reddit_db`
- **Django -> Redis:** `redis://redis:6379/1`
- **Node.js -> Redis:** `redis://redis:6379`
- **Node.js -> MongoDB:** `mongodb://mongo:27017/chatapp`
- **Client -> Django:** `http://localhost:8000` (HTTP REST)
- **Client -> Node.js:** `ws://localhost:8080` (Persistent WebSocket)

---

## Unified Multi-Container `docker-compose.yml`

To run all 5 separate containers under a single unified compose configuration from the root directory:

```yaml
services:
  # Container 1: Django Web Application
  web:
    build: .
    container_name: web_app
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Container 2: Node.js WebSocket Server
  websocket:
    build: ./node-websocket-server
    container_name: node_websocket_server
    restart: always
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
      - MONGO_URL=mongodb://mongo:27017/chatapp
    depends_on:
      redis:
        condition: service_healthy
      mongo:
        condition: service_started

  # Container 3: PostgreSQL Database (Shared Auth)
  db:
    image: postgres:17
    container_name: postgres_db_use
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: reddit_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d reddit_db"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s

  # Container 4: Redis Cache & Message Broker
  redis:
    image: redis:7-alpine
    container_name: redis_cache_ofdb
    restart: always
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # Container 5: MongoDB (Chat & Real-Time Document Store)
  mongo:
    image: mongo:7
    container_name: mongodb_service
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  postgres_data:
  static_volume:
  media_volume:
  mongo_data:
```

---

## Container Lifecycle Commands

### Start All Containers
```bash
docker compose up -d
```

### Start Individual Containers
```bash
# Start only Django and its DB
docker compose up -d web db

# Start only the WebSocket server
docker compose up -d websocket redis mongo
```

### Monitor Container Status
```bash
docker compose ps
```

### Inspect Container Logs
```bash
# All containers
docker compose logs -f

# Specific container
docker compose logs -f web
docker compose logs -f websocket
```

### Restart a Specific Container
```bash
docker compose restart websocket
```

### Stop All Containers
```bash
docker compose down
```

---

## Why Separate Containers?

1. **Isolation:** A crash or memory leak in the WebSocket server does not crash the Django REST API or PostgreSQL.
2. **Independent Scaling:** Scale WebSocket containers horizontally (`docker compose up -d --scale websocket=3`) independently from Django workers.
3. **Optimized Runtimes:** Minimal, secure base images tailored for each stack (`python:3.12-slim` vs `node:20-alpine` vs `alpine`).
4. **Clean Decoupling:** Upgrading Node.js dependencies has zero impact on Python dependencies and vice-versa.
