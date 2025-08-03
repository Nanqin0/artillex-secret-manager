# Secret Manager

A secure, production-ready secret management service built with FastAPI and MongoDB. Designed for Docker Swarm deployment with high availability and scalability.

---

## 🚀 Features

- AES-256-GCM encryption (96-bit random nonce)  
- RESTful API with FastAPI and OpenAPI docs  
- MongoDB-backed persistent storage  
- Audit logging (with TTL cleanup)  
- Docker Swarm deployment with replica scaling  
- Built-in input validation, UUID-based secret IDs  
- Load-tested and concurrency-safe  

---

## 🏗️ Architecture

### Application Structure

```
secret-manager/
├── app/
│   ├── main.py          # FastAPI application and API endpoints
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── crypto_utils.py  # AES-GCM encryption/decryption utilities
│   ├── db.py            # MongoDB operations and connection management
│   ├── config.py        # Environment configuration
│   └── audit.py         # Audit logging system
├── scripts/
│   ├── create_secret.sh # CLI to create secrets
│   └── fetch_secret.sh  # CLI to fetch secrets
├── tests/
│   ├── conftest.py      # Pytest setup
│   └── test_api.py      # API test suite
├── Dockerfile           # Image definition
├── stack.yml            # Swarm deployment
├── requirements.txt     # Dependencies
└── README.md            # This file
```

### Docker Swarm Cluster

```
┌─────────────────────────────────────────┐
│           Docker Swarm Cluster          │
├─────────────────────────────────────────┤
│  Manager Node          Worker Nodes     │
│  ┌─────────────┐     ┌─────────────┐   │
│  │  MongoDB    │     │Secret-Mgr 1 │   │
│  │   :27017    │◄────┤   :8000     │   │
│  └─────────────┘     └─────────────┘   │
│                      ┌─────────────┐   │
│                      │Secret-Mgr 2 │   │
│                      │   :8000     │   │
│                      └─────────────┘   │
└─────────────────────────────────────────┘
         │                    │
    overlay network      load balancing
     (encrypted)        (ingress routing)
```

---

## 🚀 Quick Start (Docker Swarm)

### 1. **Clone Repository**

```bash
git clone https://github.com/Nanqin0/artillex-secret-manager.git
cd artillex-secret-manager
```

### 2. **Configure Environment**

```bash
cp .env.example .env
```

Update `MASTER_KEY`:

```bash
# Generate a 32-byte random base64 key
sed -i "s/^MASTER_KEY=.*/MASTER_KEY=$(python3 -c 'import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())')/" .env
```

### 3. **Build Application Image**

```bash
# Build the Secret Manager image
docker build -t secret-manager:latest .
```

### 4. **Initialize Docker Swarm**

```bash
docker swarm init
```

### 5. **Deploy to Swarm**

```bash
# Deploy the stack
docker stack deploy -c stack.yml secret-manager

# Check deployment status
docker service ls
docker service ps secret-manager_api
```

### 6. **Test the Service**

Wait for ~30 seconds, then:

```bash
# Access API documentation
curl http://localhost:8000/docs
```

**Create a secret:**

```bash
SECRET=$(echo -n "my_secret" | base64)
curl -X POST http://localhost:8000/vault/secret/create/ \
  -H "Content-Type: application/json" \
  -d "{\"secret\":\"$SECRET\"}"
```

**Fetch a secret:**

```bash
curl -X POST http://localhost:8000/vault/secret/fetch \
  -H "Content-Type: application/json" \
  -d "{\"secret_id\":\"<YOUR_SECRET_ID>\"}"
```

---

### 🖥️ Using the Provided Scripts

**Create a secret:**

```bash
chmod +x scripts/create_secret.sh
./scripts/create_secret.sh "$(echo -n 'my_password' | base64)"
```

**Fetch a secret:**

```bash
chmod +x scripts/fetch_secret.sh
./scripts/fetch_secret.sh "550e8400-e29b-41d4-a716-446655440000"
```

---

## 📜 Audit Logs

If `AUDIT_ENABLED=true`, the system logs every `create` and `fetch` request to the `audit_logs` collection in MongoDB.

### Fields

| Field       | Description                    |
|-------------|--------------------------------|
| timestamp   | UTC timestamp of the operation |
| operation   | `"create"` or `"fetch"`        |
| secret_id   | UUID of the secret             |
| client_ip   | IP of the requester            |
| status      | `"success"` or `"failure"`     |

---

### 🧪 Example: Manual Log Fetch

```bash
docker exec -it $(docker ps -qf name=secret-manager_mongodb) mongosh vault
```

```js
db.audit_logs.find().sort({ timestamp: -1 }).limit(10).pretty()
```

---

### 🧼 Audit Log Retention (TTL)

```env
AUDIT_TTL_DAYS=90  # Delete logs older than 90 days (0 = keep forever)
```

Uses a MongoDB TTL index on `timestamp`.

---

## 🔒 Security Features

- Encrypted secrets (never stored in plaintext)  
- UUID-based access  
- Configurable log retention  
- Authenticated MongoDB supported  
- Docker Secrets support (optional)  

---

## ⚙️ Configuration

| Variable          | Description                              | Default                   | Required |
|-------------------|------------------------------------------|---------------------------|----------|
| `MASTER_KEY`      | 32-byte encryption key (base64 or raw)   | None                      | ✅ Yes   |
| `MONGO_URI`       | MongoDB URI                              | `mongodb://localhost:27017` | ❌ No  |
| `AUDIT_ENABLED`   | Toggle audit logging                     | `true`                    | ❌ No   |
| `AUDIT_TTL_DAYS`  | TTL (in days) for audit logs             | `0` (keep forever)        | ❌ No   |

### 🔐 Master Key Requirements

- Must be 32 bytes (256 bits)  
- Base64 or raw string  
- Should be cryptographically random  
- Must be kept secret and securely backed up  

---

## 🔧 Troubleshooting

### ❓ Secret not returned?

- Ensure secret is base64-encoded  
- Check logs:  
  ```bash
  docker service logs secret-manager_api -f
  ```

### ❗ MongoDB errors?

```bash
docker service logs secret-manager_mongodb
```

### 🌐 Can't connect?

- Visit: `curl localhost:8000/docs`  
- Ensure ports are published and open  

---

## ✅ Compliance

- **Audit Logs**: Configurable retention with MongoDB TTL  
- **Data Retention**: Automatic log cleanup  
- **Encryption**: AES-256-GCM (FIPS 140-2 compliant)  
- **Container Security**: Image updates & CVE scanning  
