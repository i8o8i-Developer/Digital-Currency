# I8o8iCoin

## ProjectDescription

I8o8iCoin Is A Decentralized Cryptocurrency Built On A Custom Blockchain Implementation. This Project Provides A Complete Backend Solution For A Digital Currency System, Including Blockchain Management, Consensus Mechanisms, Smart Contracts, Peer-To-Peer Networking, And Wallet Functionality.

**Note:** Only The Backend Part Is Completed. The Frontend Is Not Yet Implemented.

## Features

### BlockchainCore
- **Proof-Of-Work (PoW):** Basic Mining And Block Validation.
- **Proof-Of-Stake (PoS):** Stake-Based Consensus For Energy Efficiency.
- **Delegated Proof-Of-Stake (DPoS):** Delegate-Based Voting System.
- **UTXO Model:** Unspent Transaction Output System For Secure Transactions.
- **Mempool:** Transaction Pool For Pending Transactions.
- **Genesis Block:** Initial Block Creation.

### SmartContracts
- **Script Engine:** Basic Scripting Language For Programmable Money.
- **OpCodes Support:** Includes Common Operations Like OP_DUP, OP_HASH160, OP_CHECKSIG, Etc.
- **Contract Manager:** Handles Deployment And Execution Of Smart Contracts.

### Networking
- **Peer-To-Peer Network:** Advanced P2P With Peer Discovery And Gossip Protocol.
- **WebSocket Support:** Real-Time Communication Between Nodes.
- **Peer Quality Assessment:** Scoring System For Reliable Network Connections.

### WalletAndTransactions
- **Wallet Creation:** Generate New Wallets With Public/Private Key Pairs.
- **Balance Management:** Check Wallet Balances.
- **Transaction Handling:** Send And Receive Transactions.
- **Cryptographic Security:** ECDSA Signatures For Transaction Verification.

### ApiAndMonitoring
- **Flask API:** RESTful API For Wallet, Transaction, And Node Operations.
- **Rate Limiting:** Prevents Abuse With Request Limits.
- **Swagger Documentation:** Interactive API Docs.
- **Prometheus Metrics:** Monitoring And Alerting Support.
- **JWT Authentication:** Secure API Access.

### AdditionalFeatures
- **Logging:** Comprehensive Logging System.
- **Configuration Management:** YAML-Based Config Files.
- **Data Storage:** Persistent Storage For Blockchain Data.
- **Consensus Engine:** Switchable Consensus Algorithms.

## Installation

1. **Clone The Repository:**
   ```
   git clone <repository-url>
   cd i8o8iCoin
   ```

2. **Install Dependencies:**
   ```
   pip install -r Requirements.txt
   ```

3. **Configure The Application:**
   - Edit `BackEnd/Config.py` Or Use YAML Config Files In `Config/` Directory.

4. **Run The Application:**
   ```
   python BackEnd/App.py
   ```

## Usage

### StartingTheNode
Run The Main Application To Start The Blockchain Node:
```
python BackEnd/App.py
```

The API Will Be Available At `http://localhost:5000` (Default Port).

### ApiEndpoints
- `POST /wallet/create` - Create A New Wallet.
- `GET /wallet/balance/<address>` - Get Wallet Balance.
- `POST /transaction/send` - Send A Transaction.
- `GET /blockchain/chain` - Get The Current Blockchain.
- `POST /node/register` - Register A New Peer Node.

For Full API Documentation, Visit `http://localhost:5000/apidocs` When The Server Is Running.

### Mining
The Node Supports Mining Blocks Based On The Configured Consensus Algorithm. Mining Can Be Started Via API Calls Or Programmatically.

## Architecture

- **BackEnd/App.py:** Main Flask Application And API Endpoints.
- **BackEnd/BlockChain.py:** Blockchain Logic And Block Management.
- **BackEnd/Consensus.py:** Consensus Algorithms (PoW, PoS, DPoS).
- **BackEnd/SmartContract.py:** Smart Contract Engine.
- **BackEnd/P2PNetwork.py:** Peer-To-Peer Networking.
- **BackEnd/Wallet.py:** Wallet And Key Management.
- **BackEnd/Transaction.py:** Transaction Creation And Validation.
- **BackEnd/Storage.py:** Data Persistence.
- **BackEnd/Config.py:** Configuration Settings.
- **BackEnd/logger.py:** Logging Utilities.

## Dependencies

See `Requirements.txt` For A Complete List Of Dependencies, Including Flask, ECDSA, WebSockets, Prometheus, And More.

## Contributing

1. Fork The Repository.
2. Create A Feature Branch.
3. Commit Your Changes.
4. Push To The Branch.
5. Open A Pull Request.

## License

This Project Is Licensed Under The [MIT License](LICENSE).

## Disclaimer

This Is A Proof-Of-Concept Implementation. Not Intended For Production Use Without Further Security Audits And Testing.