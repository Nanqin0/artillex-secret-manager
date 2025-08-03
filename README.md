# Secret Manager

A secure, production-ready secret management service built with FastAPI and MongoDB. Designed for Docker Swarm deployment with high availability and scalability.

## 🚀 Features

- **🔐 Advanced Encryption**: AES-256-GCM encryption with random 96-bit nonces for each secret
- **🌐 RESTful API**: FastAPI-based REST API with automatic OpenAPI documentation
- **📊 MongoDB Storage**: Persistent storage with MongoDB and connection pooling
- **📝 Audit Logging**: Comprehensive audit trail for all operations with configurable retention
- **🔍 Input Validation**: Strict Base64 validation and error handling
- **🆔 UUID-based Access**: Cryptographically secure secret identifiers
- **⚡ High Performance**: Async request handling with built-in concurrency support
- **🐳 Docker Swarm Ready**: Optimized for container orchestration and scaling
- **🔄 High Availability**: Multi-replica deployment with automatic failover

## 🏗️ Architecture

### Application Structure
```
secret-manager/
├── app/
│   ├── main.py          # FastAPI application and API endpoints
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── crypto_utils.py  # AES-GCM encryption/decryption utilities
│   ├── db.py           # MongoDB database operations and connection management
│   ├── config.py       # Environment configuration management
│   └── audit.py        # Comprehensive audit logging system
├── scripts/
│   ├── create_secret.sh # Shell script to create secrets via API
│   └── fetch_secret.sh  # Shell script to fetch secrets via API
├── tests/
│   ├── conftest.py     # Pytest configuration and fixtures
│   └── test_api.py     # Comprehensive API test suite
├── Dockerfile          # Container image definition
├── stack.yml           # Docker Swarm deployment configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Docker Swarm Deployment
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

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.111.0
- **Database**: MongoDB 7.0 with PyMongo 4.7.2
- **Encryption**: Cryptography 42.0.7 (AES-256-GCM)
- **Container Runtime**: Docker with Swarm orchestration
- **WSGI Server**: Gunicorn 22.0.0 with Uvicorn workers
- **Configuration**: python-dotenv 1.0.1
- **Testing**: pytest with MongoDB fixtures

## 📋 Prerequisites

- **Docker**: 20.10+ with Swarm mode enabled
- **Docker Compose**: 2.0+ (for local development)
- **Operating System**: Linux, macOS, or Windows with Docker Desktop
- **Memory**: Minimum 2GB RAM for cluster
- **Storage**: At least 5GB available space

## 🚀 Quick Start (Docker Swarm)

### 1. **Clone Repository**
```bash
git clone <repository-url>
cd secret_manager
```

### 2. **Initialize Docker Swarm**
```bash
# Initialize Swarm (if not already done)
docker swarm init

# Check swarm status
docker info | grep Swarm
```

### 3. **Build Application Image**
```bash
# Build the Secret Manager image
docker build -t secret-manager:latest .
```

### 4. **Configure Environment**
```bash
# Generate a secure master key
export MASTER_KEY=$(python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())")

# Set optional configurations
export AUDIT_ENABLED=true
export AUDIT_TTL_DAYS=90
```

### 5. **Deploy to Swarm**
```bash
# Deploy the stack
docker stack deploy -c stack.yml secret-manager

# Check deployment status
docker service ls
docker service ps secret-manager_secret-manager
```

### 6. **Verify Deployment**
```bash
# Wait for services to be ready
sleep 30

# Access API documentation
curl http://localhost:8000/docs

# Test the API
curl -X POST http://localhost:8000/vault/secret/create/ \
  -H "Content-Type: application/json" \
  -d '{"secret":"'$(echo -n "test_secret" | base64)'"}'
```

**Service Endpoints:**
- 📖 **API Documentation**: http://localhost:8000/docs
- 🔗 **API Endpoint**: http://localhost:8000
- 🗄️ **MongoDB**: localhost:27017 (internal)

## 📚 API Reference

### Create Secret
**Endpoint:** `POST /vault/secret/create/`

Creates a new encrypted secret and returns a unique identifier.

**Request:**
```json
{
  "secret": "cGFzc3dvcmQxMjM="  // Base64 encoded plaintext
}
```

**Response:**
```json
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000"  // UUID v4
}
```

**Status Codes:**
- `200`: Secret created successfully
- `400`: Invalid Base64 input
- `500`: Server error (encryption/database failure)

### Fetch Secret
**Endpoint:** `POST /vault/secret/fetch`

Retrieves and decrypts a secret by its ID.

**Request:**
```json
{
  "secret_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "secret": "cGFzc3dvcmQxMjM="  // Base64 encoded plaintext
}
```

**Status Codes:**
- `200`: Secret retrieved successfully
- `404`: Secret not found
- `500`: Server error (decryption/database failure)

## 💡 Usage Examples

### Using cURL

**Create a secret:**
```bash
# Encode your secret to base64
SECRET_B64=$(echo -n "my_secret_password" | base64)

# Create the secret
curl -X POST http://localhost:8000/vault/secret/create/ \
  -H "Content-Type: application/json" \
  -d "{\"secret\":\"${SECRET_B64}\"}"

# Response: {"secret_id":"550e8400-e29b-41d4-a716-446655440000"}
```

**Fetch a secret:**
```bash
SECRET_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8000/vault/secret/fetch \
  -H "Content-Type: application/json" \
  -d "{\"secret_id\":\"${SECRET_ID}\"}"

# Response: {"secret":"bXlfc2VjcmV0X3Bhc3N3b3Jk"}
```

### Using the Provided Scripts

**Create a secret:**
```bash
chmod +x scripts/create_secret.sh
# Note: Replace localhost with any swarm node IP for remote access
./scripts/create_secret.sh "$(echo -n 'my_password' | base64)"
```

**Fetch a secret:**
```bash
chmod +x scripts/fetch_secret.sh
./scripts/fetch_secret.sh "550e8400-e29b-41d4-a716-446655440000"
```

### Using Python

```python
import requests
import base64
import json

BASE_URL = "http://localhost:8000"

# Encode your secret
plaintext = "my_secret_password"
secret_b64 = base64.b64encode(plaintext.encode()).decode()

# Create secret
create_response = requests.post(
    f"{BASE_URL}/vault/secret/create/",
    json={"secret": secret_b64}
)
secret_id = create_response.json()["secret_id"]
print(f"Secret created with ID: {secret_id}")

# Fetch secret
fetch_response = requests.post(
    f"{BASE_URL}/vault/secret/fetch",
    json={"secret_id": secret_id}
)
retrieved_secret = base64.b64decode(
    fetch_response.json()["secret"]
).decode()
print(f"Retrieved secret: {retrieved_secret}")
```

## 🔒 Security Features

### Encryption
- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256-bit master key
- **Nonce**: 96-bit random nonce per encryption
- **Authentication**: Built-in authentication tag prevents tampering
- **Key Management**: Master key stored as environment variable

### Data Protection
- **Encryption at Rest**: All secrets encrypted before database storage
- **No Plaintext Storage**: Plaintext never persists to disk
- **Secure Random**: Cryptographically secure random number generation
- **Input Validation**: Strict Base64 format validation
- **Error Handling**: No sensitive data leaked in error messages

### Audit & Monitoring
- **Operation Logging**: All create/fetch operations logged
- **IP Tracking**: Client IP addresses recorded
- **Timestamps**: UTC timestamps for all operations
- **Status Tracking**: Success/failure status for each operation
- **Configurable Retention**: TTL-based automatic log cleanup

## ⚙️ Configuration

| Environment Variable | Description | Default | Required |
|---------------------|-------------|---------|----------|
| `MASTER_KEY` | 32-byte master encryption key (base64 or raw) | None | **Yes** |
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017` | No |
| `AUDIT_ENABLED` | Enable/disable audit logging | `true` | No |
| `AUDIT_TTL_DAYS` | Audit log retention in days (0=forever) | `0` | No |

### Master Key Requirements
- Must be exactly 32 bytes (256 bits)
- Can be provided as base64-encoded string or raw 32-character string
- Should be cryptographically random
- Must be kept secret and backed up securely

## 🧪 Testing

### Swarm Deployment Testing
```bash
# 1. Test service health
docker service ls
docker service ps secret-manager_secret-manager

# 2. Test API availability across nodes
curl http://localhost:8000/docs
curl http://NODE_IP:8000/docs  # Replace NODE_IP with actual node IP

# 3. Run automated tests
python -c "
import requests
import base64
import time

# Test against the Swarm deployment
base_url = 'http://localhost:8000'

print('Testing Secret Manager Swarm deployment...')

# Test 1: Valid secret creation and retrieval
secret = base64.b64encode(b'swarm_test_secret').decode()
resp = requests.post(f'{base_url}/vault/secret/create/', json={'secret': secret})
print(f'Create Response: {resp.status_code} - {resp.json()}')

if resp.status_code == 200:
    secret_id = resp.json()['secret_id']
    resp = requests.post(f'{base_url}/vault/secret/fetch', json={'secret_id': secret_id})
    print(f'Fetch Response: {resp.status_code} - {resp.json()}')
    
    if resp.status_code == 200 and resp.json()['secret'] == secret:
        print('✅ Secret roundtrip test PASSED')
    else:
        print('❌ Secret roundtrip test FAILED')

# Test 2: Invalid base64
resp = requests.post(f'{base_url}/vault/secret/create/', json={'secret': 'invalid!'})
print(f'Invalid B64 Response: {resp.status_code}')
if resp.status_code == 400:
    print('✅ Input validation test PASSED')
else:
    print('❌ Input validation test FAILED')
"
```

### Load Testing
```bash
# Test with multiple concurrent requests
python -c "
import requests
import base64
import concurrent.futures
import time

def create_secret(i):
    secret = base64.b64encode(f'load_test_secret_{i}'.encode()).decode()
    resp = requests.post('http://localhost:8000/vault/secret/create/', 
                        json={'secret': secret}, timeout=10)
    return resp.status_code == 200

# Test with 20 concurrent requests
print('Running load test with 20 concurrent requests...')
start_time = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(create_secret, i) for i in range(20)]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

duration = time.time() - start_time
success_rate = sum(results) / len(results) * 100

print(f'Load test completed in {duration:.2f}s')
print(f'Success rate: {success_rate:.1f}%')
print(f'Requests per second: {len(results)/duration:.1f}')
"
```

## 🚀 Production Deployment

### Swarm Operations

**Scaling Services:**
```bash
# Scale API service to 5 replicas
docker service scale secret-manager_secret-manager=5

# Check scaling progress
docker service ps secret-manager_secret-manager
```

**Service Updates:**
```bash
# Update to new image version
docker service update --image secret-manager:v2.0 secret-manager_secret-manager

# Update environment variables
docker service update --env-add NEW_CONFIG=value secret-manager_secret-manager

# Rolling restart
docker service update --force secret-manager_secret-manager
```

**Adding Nodes:**
```bash
# Get join tokens
docker swarm join-token worker    # For worker nodes
docker swarm join-token manager   # For manager nodes

# On new machines, run the provided join command
docker swarm join --token SWMTKN-xxx <manager-ip>:2377
```

**Service Management:**
```bash
# View service logs
docker service logs secret-manager_secret-manager -f

# Remove the entire stack
docker stack rm secret-manager

# Redeploy with updates
docker stack deploy -c stack.yml secret-manager
```

### Production Checklist
- [ ] **Multi-node Swarm**: Deploy across multiple machines
- [ ] **Persistent Storage**: Configure external volume drivers
- [ ] **Load Balancer**: Set up external load balancer for HA
- [ ] **TLS Termination**: Configure SSL at load balancer level
- [ ] **Monitoring**: Deploy Prometheus/Grafana stack
- [ ] **Backup Strategy**: Automate MongoDB backups
- [ ] **Security Hardening**: Enable Swarm encryption and secrets
- [ ] **Log Aggregation**: Configure centralized logging

## 🔧 Troubleshooting

### Swarm-Specific Issues

**1. Service Won't Start**
```bash
# Check service status
docker service ps secret-manager_secret-manager --no-trunc

# View service logs
docker service logs secret-manager_secret-manager

# Check node resources
docker node ls
docker system df
```

**2. "MASTER_KEY environment variable not set"**
```bash
# Set environment variable before deployment
export MASTER_KEY=$(python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())")

# Verify it's set
echo $MASTER_KEY

# Redeploy with correct environment
docker stack deploy -c stack.yml secret-manager
```

**3. MongoDB Connection Issues**
```bash
# Check MongoDB service status
docker service ps secret-manager_mongodb

# View MongoDB logs
docker service logs secret-manager_mongodb

# Test connection from API container
docker exec -it $(docker ps -q -f name=secret-manager) ping mongodb
```

**4. Network Connectivity Problems**
```bash
# Check overlay network
docker network ls | grep secret-manager
docker network inspect secret-manager_secret-manager-network

# Test service discovery
docker exec -it $(docker ps -q -f name=secret-manager) nslookup mongodb
```

**5. Port Access Issues**
```bash
# Check if ports are published correctly
docker service inspect secret-manager_secret-manager

# Test from different node
curl http://OTHER_NODE_IP:8000/docs

# Check firewall rules
sudo ufw status
```

### Performance Troubleshooting
```bash
# Check resource usage
docker stats $(docker ps -q -f name=secret-manager)

# View service resource limits
docker service inspect secret-manager_secret-manager | grep -A 10 "Resources"

# Check node resource availability
docker node ls
```

### Debug Mode
```bash
# Scale down to 1 replica for debugging
docker service scale secret-manager_secret-manager=1

# Follow logs in real-time
docker service logs secret-manager_secret-manager -f

# Access container shell for debugging
docker exec -it $(docker ps -q -f name=secret-manager) bash
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow existing code style
4. **Add tests**: Ensure new features are tested
5. **Run tests**: `pytest tests/ -v`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**: Describe your changes

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for public functions
- Keep functions focused and testable

## 📝 License

[Specify your license here - e.g., MIT, Apache 2.0]

## ⚠️ Security Considerations

### Key Management
- **Master Key Security**: Store master key in secure key management service (AWS KMS, HashiCorp Vault, etc.)
- **Key Rotation**: Implement regular master key rotation procedures
- **Backup Strategy**: Secure backup of master key with access controls

### Access Control
- **Authentication**: Add API authentication (JWT, API keys)
- **Authorization**: Implement role-based access control
- **Rate Limiting**: Prevent API abuse and brute force attacks
- **IP Allowlisting**: Restrict access to known IP ranges

### Infrastructure Security
- **Network Security**: Enable Swarm network encryption with `encrypted: true`
- **Node Security**: Secure Docker daemon and restrict node access
- **Secrets Management**: Use Docker secrets for sensitive configuration
- **Firewall**: Configure proper firewall rules for Swarm ports (2377, 7946, 4789)

### Docker Swarm Security
```bash
# Enable network encryption
networks:
  secret-manager-network:
    driver: overlay
    encrypted: true

# Use Docker secrets
echo "your_master_key" | docker secret create master_key -
echo "mongo_password" | docker secret create mongo_password -
```

### Compliance
- **Audit Logs**: Maintain detailed audit trails with configurable retention
- **Data Retention**: Implement proper data retention policies via TTL
- **Encryption Standards**: AES-256-GCM meets FIPS 140-2 requirements
- **Container Security**: Regular image updates and vulnerability scanning


