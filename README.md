```
 ____  _       _ _        _       ____                                       
|  _ \(_) __ _(_) |_ __ _| |     / ___|   _ _ __ _ __ ___ _ __   ___ _   _ 
| | | | |/ _` | | __/ _` | |____| |  | | | | '__| '__/ _ \ '_ \ / __| | | |
| |_| | | (_| | | || (_| | |____| |__| |_| | |  | | |  __/ | | | (__| |_| |
|____/|_|\__, |_|\__\__,_|_|     \____\__,_|_|  |_|  \___|_| |_|\___|\__, |
         |___/                                                        |___/ 
```

# Digital Currency - I8o8iCoin

**A Complete Blockchain Cryptocurrency Implementation With Smart Contracts**

[![GitHub](https://img.shields.io/badge/GitHub-i8o8i--Developer-green.svg)](https://github.com/i8o8i-Developer)
[![Repo](https://img.shields.io/badge/Repo-Digital--Currency-brightgreen.svg)](https://github.com/i8o8i-Developer/Digital-Currency)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table Of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [API Documentation](#api-documentation)
- [Frontend Interface](#frontend-interface)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Digital Currency** Is A Full-Featured Blockchain Cryptocurrency Platform With A Complete Backend Implementation And Modern Web Interface. Built From Scratch With Python And Vanilla JavaScript, It Demonstrates Core Blockchain Concepts Including Multiple Consensus Algorithms, Smart Contracts, P2P Networking, And Secure Wallet Management.

### Key Highlights

✅ **Multiple Consensus Mechanisms** - Proof Of Work (PoW), Proof Of Stake (PoS), Delegated Proof Of Stake (DPoS)  
✅ **Smart Contract Engine** - Full Script Execution With OpCode Support  
✅ **P2P Network** - WebSocket-Based Peer Discovery And Gossip Protocol  
✅ **UTXO Model** - Bitcoin-Style Transaction Management  
✅ **RESTful API** - Complete Flask Backend With JWT Authentication  
✅ **Modern Web UI** - Bright Green Theme With Retro Aesthetics  
✅ **Virtual Environment** - Automated Setup With Python Scripts  

---

## ⚡ Features

### 🔗 Blockchain Core

- **Multi-Consensus Support**
  - Proof Of Work (PoW) With Adjustable Difficulty
  - Proof Of Stake (PoS) For Energy Efficiency
  - Delegated Proof Of Stake (DPoS) With Voting System
  
- **Transaction Management**
  - UTXO Model For Security And Transparency
  - Transaction Mempool With Priority Queue
  - Multi-Input/Multi-Output Transactions
  - Transaction Validation And Verification
  
- **Block Management**
  - Genesis Block Creation
  - Block Propagation And Validation
  - Chain Reorganization Support
  - Merkle Tree Implementation

### 📜 Smart Contracts

- **Script Engine**
  - Stack-Based Execution Model
  - OpCode Support (OP_DUP, OP_HASH160, OP_CHECKSIG, OP_IF, OP_RETURN)
  - Contract State Management
  - Event Emission System
  
- **Contract Features**
  - Deploy Custom Contracts
  - Execute Contract Functions
  - Query Contract State
  - Listen To Contract Events

### 🌐 Networking

- **P2P Protocol**
  - Peer Discovery Mechanism
  - Gossip-Based Propagation
  - WebSocket Real-Time Communication
  - Peer Quality Scoring System
  
- **Network Features**
  - Automatic Peer Connection
  - Block And Transaction Broadcasting
  - Node Synchronization
  - Network Health Monitoring

### 💼 Wallet System

- **Key Management**
  - ECDSA Key Pair Generation
  - Schnorr Signature Support
  - Hierarchical Deterministic (HD) Wallets
  - Secure Private Key Storage
  
- **Wallet Operations**
  - Create Multiple Wallets
  - Check Balance And UTXOs
  - Send And Receive Transactions
  - Transaction History Tracking

### 🖥️ Web Interface

- **Modern Design**
  - Bright Green Theme With Retro Elements
  - Responsive Layout For All Devices
  - Custom Modal Popups And Notifications
  - Pixelated Typography Effects
  
- **Interface Features**
  - Wallet Management Dashboard
  - Transaction Creation Form
  - Blockchain Explorer
  - Smart Contract Deployment
  - Mining Controls
  - Network Peer Management
  - Real-Time Status Updates

### 🔐 Security & Monitoring

- **Authentication**
  - JWT Token-Based Authentication
  - Password Hashing (bcrypt)
  - Session Management
  - Rate Limiting Protection
  
- **Monitoring**
  - Prometheus Metrics Export
  - Comprehensive Logging System
  - API Request Tracking
  - Network Health Checks

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 Or Higher
- Pip Package Manager
- Git (For Cloning Repository)

### Installation Steps

1. **Clone The Repository**
   ```bash
   git clone https://github.com/i8o8i-Developer/Digital-Currency.git
   cd Digital-Currency
   ```

2. **Start Backend Server**
   ```bash
   python Start_BackEnd.py
   ```
   This Script Will:
   - Create A Virtual Environment
   - Install All Dependencies From `Requirements.txt`
   - Start The Flask Server On Port 5000

3. **Start Frontend Server** (In A New Terminal)
   ```bash
   python Start_FrontEnd.py
   ```
   This Script Will:
   - Start HTTP Server On Port 8080
   - Automatically Open Your Browser To `http://localhost:8080`

4. **Access The Application**
   - **Frontend UI:** http://localhost:8080
   - **Backend API:** http://localhost:5000
   - **API Docs:** http://localhost:5000/apidocs

### First Steps

1. **Create A Wallet** - Navigate To Wallet Tab And Click "Create New Wallet"
2. **Get Some Coins** - Start Mining Or Request Coins From Faucet
3. **Send Transaction** - Use The Transaction Tab To Send Coins
4. **Explore Blockchain** - View Blocks And Transactions In The Explorer Tab

---

## 📁 Project Structure

```
Digital-Currency/
│
├── BackEnd/                    # Backend Python Application
│   ├── __init__.py            # Package Initializer
│   ├── App.py                 # Flask API Server (Main Entry Point)
│   ├── BlockChain.py          # Blockchain Logic And Block Management
│   ├── Config.py              # Configuration Settings
│   ├── Consensus.py           # Consensus Algorithms (PoW, PoS, DPoS)
│   ├── Crypto.py              # Cryptographic Functions (ECDSA, Schnorr)
│   ├── logger.py              # Logging Utilities
│   ├── P2PNetwork.py          # Peer-To-Peer Networking
│   ├── P2PStr.py              # P2P Protocol Structures
│   ├── SmartContract.py       # Smart Contract Engine
│   ├── Storage.py             # SQLite Database Operations
│   ├── Transaction.py         # Transaction Creation And Validation
│   ├── Wallet.py              # Wallet And Key Management
│   └── Data/                  # Data Storage Directory
│       └── Wallets.json       # Wallet Storage File
│
├── FrontEnd/                   # Frontend Web Application
│   ├── index.html             # Main HTML File
│   ├── Css/                   # Stylesheets
│   │   └── Retro.css          # Bright Green Retro Theme
│   └── Js/                    # JavaScript Files
│       └── App.js             # Frontend Application Logic
│
├── Source/                     # Additional Source Files
│   └── Proxy.php              # PHP Proxy (Optional)
│
├── Start_BackEnd.py           # Backend Startup Script (With Venv)
├── Start_FrontEnd.py          # Frontend HTTP Server Script
├── Requirements.txt           # Python Dependencies
├── LICENSE                    # MIT License
└── README.md                  # This File
```

---

## 🛠️ Technology Stack

### Backend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python 3.8+ | Core Programming Language |
| **Web Framework** | Flask 2.3.0 | RESTful API Server |
| **Database** | SQLite3 | Data Persistence |
| **Cryptography** | ECDSA, Hashlib | Digital Signatures And Hashing |
| **Networking** | WebSockets | Real-Time P2P Communication |
| **Authentication** | JWT (PyJWT) | Token-Based Auth |
| **Monitoring** | Prometheus Client | Metrics Collection |
| **Documentation** | Flasgger | Swagger API Docs |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Markup** | HTML5 | Structure |
| **Styling** | CSS3 | Bright Green Theme With Retro Effects |
| **Scripting** | Vanilla JavaScript | Application Logic (No Frameworks) |
| **Server** | Python http.server | Static File Serving |

### Key Dependencies

```
Flask==2.3.0
Flask-CORS==4.0.0
Flask-SocketIO==5.3.4
Flask-Limiter==3.3.1
flasgger==0.9.7.1
PyJWT==2.8.0
ecdsa==0.18.0
bcrypt==4.0.1
prometheus-client==0.17.1
python-socketio==5.9.0
websockets==11.0.3
pyyaml==6.0.1
requests==2.31.0
```

---

## 📡 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

#### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

Response: { "token": "jwt_token_here" }
```

### Wallet Endpoints

#### Create Wallet
```http
POST /wallet/create
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "My Wallet",
  "algorithm": "ecdsa"
}

Response: { "address": "wallet_address", "public_key": "...", "private_key": "..." }
```

#### Get Balance
```http
GET /wallet/balance/<address>
Authorization: Bearer <jwt_token>

Response: { "address": "...", "balance": 100.0, "utxos": [...] }
```

#### List Wallets
```http
GET /wallet/list
Authorization: Bearer <jwt_token>

Response: { "wallets": ["address1", "address2", ...] }
```

### Transaction Endpoints

#### Send Transaction
```http
POST /transaction/send
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "from_address": "sender_address",
  "to_address": "recipient_address",
  "amount": 10.0,
  "private_key": "sender_private_key"
}

Response: { "transaction_id": "...", "status": "pending" }
```

#### Get Transaction
```http
GET /transaction/<tx_id>
Authorization: Bearer <jwt_token>

Response: { "transaction": {...} }
```

#### Get Mempool
```http
GET /transaction/mempool
Authorization: Bearer <jwt_token>

Response: { "transactions": [...], "count": 10 }
```

### Blockchain Endpoints

#### Get Chain
```http
GET /blockchain/chain
Authorization: Bearer <jwt_token>

Response: { "chain": [...], "length": 100 }
```

#### Get Block
```http
GET /blockchain/block/<block_id>
Authorization: Bearer <jwt_token>

Response: { "block": {...} }
```

#### Mine Block
```http
POST /blockchain/mine
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "miner_address": "your_address"
}

Response: { "block": {...}, "reward": 50.0 }
```

### Smart Contract Endpoints

#### Deploy Contract
```http
POST /contract/deploy
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "MyContract",
  "code": "contract_bytecode",
  "creator": "wallet_address"
}

Response: { "contract_id": "...", "address": "..." }
```

#### Call Contract
```http
POST /contract/<contract_id>/call
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "function": "transfer",
  "args": ["recipient", 100],
  "caller": "wallet_address"
}

Response: { "result": {...}, "events": [...] }
```

#### Get Contract State
```http
GET /contract/<contract_id>/state
Authorization: Bearer <jwt_token>

Response: { "state": {...} }
```

### P2P Network Endpoints

#### Register Peer
```http
POST /node/register
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "address": "192.168.1.100:5001"
}

Response: { "message": "Peer registered", "total_peers": 5 }
```

#### Get Peers
```http
GET /node/peers
Authorization: Bearer <jwt_token>

Response: { "peers": ["192.168.1.100:5001", ...], "count": 5 }
```

#### Get Node Info
```http
GET /node/info
Authorization: Bearer <jwt_token>

Response: { "node_id": "...", "version": "1.0.0", "peers": 5, "blocks": 100 }
```

### Staking Endpoints (PoS)

#### Stake Coins
```http
POST /stake/create
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "address": "wallet_address",
  "amount": 1000.0
}

Response: { "stake_id": "...", "amount": 1000.0 }
```

#### Get Stake Info
```http
GET /stake/<address>
Authorization: Bearer <jwt_token>

Response: { "address": "...", "amount": 1000.0, "weight": 0.15 }
```

### Monitoring Endpoints

#### Prometheus Metrics
```http
GET /metrics

Response: Prometheus Format Metrics
```

#### Health Check
```http
GET /health

Response: { "status": "healthy", "uptime": 3600 }
```

---

## 🎨 Frontend Interface

### Theme Customization

The UI Uses A Bright Green Theme With Retro Aesthetics. Color Scheme:

```css
:root {
  --primary-green: #2d7a2d;          /* Primary Green */
  --bright-green: #3fb83f;           /* Bright Accent */
  --light-green: #90ee90;            /* Light Highlights */
  --dark-green: #1a4d1a;             /* Dark Shadows */
  --bg-light: #f0f4f0;               /* Light Background */
  --bg-lighter: #fafdfb;             /* Lighter Areas */
  --text-dark: #1a1a1a;              /* Primary Text */
  --border-green: #2d7a2d;           /* Borders */
}
```

### UI Components

1. **Dashboard** - Overview Of Wallet Balance, Recent Transactions, Network Status
2. **Wallet Manager** - Create, Import, And Manage Multiple Wallets
3. **Transaction Form** - Send Coins With Address And Amount
4. **Blockchain Explorer** - Browse Blocks And Transactions
5. **Smart Contracts** - Deploy And Interact With Contracts
6. **Mining Panel** - Start/Stop Mining, View Mining Stats
7. **Network Panel** - Manage P2P Connections And Peers
8. **Settings** - Configure Node Options

### Custom Popup System

The UI Features Custom Modal Popups Instead Of Browser Alerts:

```javascript
// Prompt Popup
showPromptPopup("Enter Wallet Name:", "My Wallet", (value) => {
  if (value) {
    // User Entered Value
  }
});

// Confirm Popup
showConfirmPopup("Are You Sure?", (confirmed) => {
  if (confirmed) {
    // User Confirmed
  }
});

// Notification
showNotification("Transaction Sent Successfully!", "success");
```

---

## ⚙️ Configuration

### Backend Configuration (BackEnd/Config.py)

```python
# Network Settings
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# Blockchain Settings
DIFFICULTY = 4
BLOCK_REWARD = 50.0
BLOCK_TIME = 10  # Seconds

# Consensus
CONSENSUS_TYPE = 'pow'  # Options: 'pow', 'pos', 'dpos'

# P2P Network
P2P_PORT = 5001
MAX_PEERS = 20

# Database
DB_PATH = 'BackEnd/Data/blockchain.db'

# JWT Secret
JWT_SECRET_KEY = 'your-secret-key-here'
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 Hour
```

### Environment Variables

You Can Override Config Settings With Environment Variables:

```bash
export FLASK_PORT=5000
export CONSENSUS_TYPE=pos
export JWT_SECRET=my-secret-key
```

---

## 👨‍💻 Development

### Setting Up Development Environment

1. **Clone And Install**
   ```bash
   git clone https://github.com/i8o8i-Developer/Digital-Currency.git
   cd Digital-Currency
   python Start_BackEnd.py
   ```

2. **Run Tests** (If Available)
   ```bash
   python -m pytest tests/
   ```

3. **Code Style**
   - Follow PEP 8 Guidelines
   - Use Pascal Case For UI Text
   - Comment Complex Logic

### Project Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (Frontend UI)  │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│   Flask API     │
│  (App.py)       │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    ▼         ▼          ▼         ▼
┌─────┐  ┌─────┐  ┌──────────┐  ┌─────┐
│Wallet│  │Txns │  │Blockchain│  │P2P  │
└─────┘  └─────┘  └──────────┘  └─────┘
    │         │          │         │
    └─────────┴──────────┴─────────┘
              ▼
        ┌──────────┐
        │ Storage  │
        │(SQLite)  │
        └──────────┘
```

### Adding New Features

1. **Backend** - Add Endpoint In `App.py`, Implement Logic In Appropriate Module
2. **Frontend** - Add UI Component In `index.html`, Add Logic In `App.js`
3. **Testing** - Test API With Postman Or Curl, Test UI In Browser
4. **Documentation** - Update This README And API Docs

---

## 🤝 Contributing

We Welcome Contributions! Here's How To Get Started:

1. **Fork The Repository**
   ```bash
   git fork https://github.com/i8o8i-Developer/Digital-Currency.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Write Clean, Documented Code
   - Follow Existing Code Style
   - Test Your Changes Thoroughly

4. **Commit Changes**
   ```bash
   git commit -m "Add Amazing Feature"
   ```

5. **Push To Branch**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open Pull Request**
   - Describe Your Changes
   - Reference Any Issues
   - Wait For Review

### Contribution Guidelines

- ✅ Write Clear Commit Messages
- ✅ Add Comments For Complex Logic
- ✅ Update Documentation
- ✅ Test Before Submitting
- ✅ Follow Pascal Case For UI Text
- ✅ Use Bright Green Theme Colors

---

## 📄 License

This Project Is Licensed Under The **MIT License**.

```
MIT License

Copyright (c) 2024 i8o8i-Developer

Permission Is Hereby Granted, Free Of Charge, To Any Person Obtaining A Copy
Of This Software And Associated Documentation Files (the "Software"), To Deal
In The Software Without Restriction, Including Without Limitation The Rights
To Use, Copy, Modify, Merge, Publish, Distribute, Sublicense, And/Or Sell
Copies Of The Software, And To Permit Persons To Whom The Software Is
Furnished To Do So, Subject To The Following Conditions:

The Above Copyright Notice And This Permission Notice Shall Be Included In All
Copies Or Substantial Portions Of The Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See [LICENSE](LICENSE) File For Full License Text.

---

## ⚠️ Disclaimer

**Important Notice:**

This Project Is A **Proof-Of-Concept** And **Educational Implementation** Of Blockchain Technology. It Is **NOT** Intended For Production Use Without Extensive Security Audits, Testing, And Hardening.

### Security Considerations

- 🔒 **Private Keys** - Store Securely, Never Share Or Commit To Git
- 🔒 **JWT Secrets** - Use Strong Random Keys In Production
- 🔒 **Network Security** - Use TLS/SSL For Production Deployments
- 🔒 **Input Validation** - Always Validate User Inputs
- 🔒 **Rate Limiting** - Implement Proper Rate Limits To Prevent Abuse

### Known Limitations

- Limited Scalability (Suitable For Small Networks)
- Basic Smart Contract Engine (Limited OpCode Set)
- SQLite Database (Not Suitable For High-Throughput)
- No Byzantine Fault Tolerance In Current Implementation
- Simplified P2P Protocol (No Advanced Routing)

### Use Cases

✅ **Learning** - Study Blockchain Concepts  
✅ **Research** - Experiment With Consensus Algorithms  
✅ **Development** - Build Prototypes And POCs  
✅ **Education** - Teaching Cryptocurrency Fundamentals  

❌ **Production** - Not Ready For Real-World Deployments  
❌ **Financial** - Do Not Use For Real Money Transactions  
❌ **Critical Systems** - Not Audited For Security Vulnerabilities  

---

## 📞 Support & Contact

- **GitHub:** [@i8o8i-Developer](https://github.com/i8o8i-Developer)
- **Repository:** [Digital-Currency](https://github.com/i8o8i-Developer/Digital-Currency)
- **Issues:** [Report Bug Or Request Feature](https://github.com/i8o8i-Developer/Digital-Currency/issues)

---

## 🎉 Acknowledgments

Special Thanks To:

- The Open Source Community
- Bitcoin And Ethereum Projects For Inspiration
- All Contributors And Testers

---

<div align="center">

**Made With 💚 By i8o8i-Developer**

⭐ **Star This Repository If You Find It Useful!** ⭐

</div>