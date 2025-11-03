// API Configuration
const API_BASE_URL = 'http://localhost:5000';
let authToken = localStorage.getItem('authToken') || null;
let currentUser = null;

// Custom Popup System
function showPromptPopup(title, placeholder, callback) {
    const popup = document.createElement('div');
    popup.className = 'modal';
    popup.innerHTML = `
        <div class="modal-content">
            <h2 class="modal-title">${title}</h2>
            <form class="form" onsubmit="event.preventDefault();">
                <div class="form-group">
                    <input type="text" class="form-input" id="popupInput" placeholder="${placeholder}" required>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn btn-primary" style="flex: 1;" onclick="submitPopup()">Submit</button>
                    <button type="button" class="btn btn-secondary" style="flex: 1;" onclick="closePopup()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Focus On Input
    setTimeout(() => {
        const input = document.getElementById('popupInput');
        if (input) input.focus();
    }, 100);
    
    // Submit Handler
    window.submitPopup = () => {
        const input = document.getElementById('popupInput');
        const value = input.value.trim();
        if (value) {
            callback(value);
            document.body.removeChild(popup);
            delete window.submitPopup;
            delete window.closePopup;
        }
    };
    
    // Close Handler
    window.closePopup = () => {
        document.body.removeChild(popup);
        delete window.submitPopup;
        delete window.closePopup;
    };
    
    // Enter Key Handler
    const input = popup.querySelector('#popupInput');
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            window.submitPopup();
        }
    });
}

function showConfirmPopup(title, message, callback) {
    const popup = document.createElement('div');
    popup.className = 'modal';
    popup.innerHTML = `
        <div class="modal-content">
            <h2 class="modal-title">${title}</h2>
            <p style="color: var(--color-text-primary); margin: 20px 0;">${message}</p>
            <div style="display: flex; gap: 10px;">
                <button type="button" class="btn btn-success" style="flex: 1;" onclick="confirmPopup()">Confirm</button>
                <button type="button" class="btn btn-danger" style="flex: 1;" onclick="cancelPopup()">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    window.confirmPopup = () => {
        callback(true);
        document.body.removeChild(popup);
        delete window.confirmPopup;
        delete window.cancelPopup;
    };
    
    window.cancelPopup = () => {
        callback(false);
        document.body.removeChild(popup);
        delete window.confirmPopup;
        delete window.cancelPopup;
    };
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    checkAuthentication();
    loadDashboard();
    
    // Auto-Refresh Dashboard Every 10 Seconds
    setInterval(loadDashboard, 10000);
});

// Tab Management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Hide All Tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove Active From All Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show Selected Tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Load Tab-Specific Data
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'wallets':
            loadWallets();
            break;
        case 'mining':
            loadMiners();
            break;
        case 'contracts':
            loadContracts();
            break;
        case 'network':
            loadPeers();
            break;
    }
}

// Authentication
function checkAuthentication() {
    if (authToken) {
        fetchProfile();
    } else {
        showAuthControls();
    }
}

async function fetchProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.ok) {
            currentUser = data.user || {};
            showUserInfo();
        } else {
            logout();
        }
    } catch (error) {
        console.error('Profile Fetch Error:', error);
        logout();
    }
}

function showAuthControls() {
    document.getElementById('authControls').classList.remove('hidden');
    document.getElementById('userInfo').classList.add('hidden');
    document.getElementById('mainContent').classList.add('hidden');
}

function showUserInfo() {
    if (!currentUser) return;
    document.getElementById('authControls').classList.add('hidden');
    document.getElementById('userInfo').classList.remove('hidden');
    document.getElementById('mainContent').classList.remove('hidden');
    document.getElementById('userName').textContent = currentUser.username || 'Unknown';
}

function showAuthModal(type) {
    const modal = document.getElementById('authModal');
    const title = document.getElementById('authModalTitle');
    const emailGroup = document.getElementById('authEmailGroup');
    const submitBtn = document.getElementById('authSubmitBtn');
    
    if (type === 'login') {
        title.textContent = 'Login';
        emailGroup.classList.add('hidden');
        submitBtn.textContent = 'Login';
    } else {
        title.textContent = 'Register';
        emailGroup.classList.remove('hidden');
        submitBtn.textContent = 'Register';
    }
    
    modal.classList.remove('hidden');
    modal.setAttribute('data-type', type);
}

async function handleAuth(event) {
    event.preventDefault();
    
    const type = document.getElementById('authModal').getAttribute('data-type');
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    const email = document.getElementById('authEmail').value;
    
    const endpoint = type === 'login' ? '/auth/login' : '/auth/register';
    const body = type === 'login' 
        ? { username, password }
        : { username, email, password };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (data.ok) {
            if (type === 'login') {
                authToken = data.token;
                localStorage.setItem('authToken', authToken);
                currentUser = data.user || {};
                showUserInfo();
                showNotification('Login Successful', 'success');
            } else {
                showNotification('Registration Successful - Please Login', 'success');
            }
            closeModal('authModal');
            document.getElementById('authForm').reset();
        } else {
            showNotification(data.error || 'Authentication Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Auth Error:', error);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showAuthControls();
    showNotification('Logged Out', 'info');
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/node/status`);
        const data = await response.json();
        
        if (data.ok) {
            document.getElementById('blockHeight').textContent = data.blockchain.height;
            document.getElementById('difficulty').textContent = data.blockchain.difficulty;
            document.getElementById('mempoolSize').textContent = data.blockchain.mempool_size;
            document.getElementById('activePeers').textContent = data.network.alive_peers || 0;
            document.getElementById('consensusAlg').textContent = data.consensus.algorithm.toUpperCase();
            document.getElementById('contractCount').textContent = data.contracts;
            
            addActivityLog(`Updated Dashboard - Block Height: ${data.blockchain.height}`);
        }
    } catch (error) {
        console.error('Dashboard Load Error:', error);
    }
}

function addActivityLog(message) {
    const logContainer = document.getElementById('activityLog');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
    logContainer.insertBefore(entry, logContainer.firstChild);
    
    // Keep Only Last 10 Entries
    while (logContainer.children.length > 10) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// Wallet Functions
async function loadWallets() {
    if (!authToken) return;
    try {
        const response = await fetch(`${API_BASE_URL}/wallets`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        
        if (data.ok) {
            displayWallets(data.wallets);
            populateWalletSelects(data.wallets);
        }
    } catch (error) {
        console.error('Wallet Load Error:', error);
    }
}

function displayWallets(wallets) {
    const container = document.getElementById('walletList');
    container.innerHTML = '';
    
    if (wallets.length === 0) {
        container.innerHTML = '<div class="log-entry">No Wallets Found - Create One To Get Started</div>';
        return;
    }
    
    wallets.forEach(async wallet => {
        const card = document.createElement('div');
        card.className = 'wallet-card';
        
        // Fetch Balance
        const balanceRes = await fetch(`${API_BASE_URL}/wallet/${wallet.name}/balance`);
        const balanceData = await balanceRes.json();
        const balance = balanceData.ok ? balanceData.balance : 0;
        
        card.innerHTML = `
            <div class="wallet-info">
                <div class="wallet-name">${wallet.name}</div>
                <div class="wallet-address">${wallet.address.substring(0, 40)}...</div>
            </div>
            <div class="wallet-balance">${balance} Coins</div>
            <div class="wallet-actions">
                <button class="btn btn-secondary btn-small" onclick="viewWalletDetails('${wallet.name}')">View Details</button>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function viewWalletDetails(walletName) {
    // Fetch Full Wallet Details From Backend
    fetch(`${API_BASE_URL}/wallet/${walletName}`)
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                const wallet = data.wallet;
                
                // Create Detailed Popup
                const popup = document.createElement('div');
                popup.className = 'modal';
                popup.innerHTML = `
                    <div class="modal-content wallet-details-modal">
                        <h2 class="modal-title">Wallet Details: ${walletName}</h2>
                        
                        <div class="wallet-details-section">
                            <h3>Basic Information</h3>
                            <div class="detail-row">
                                <span class="detail-label">Name:</span>
                                <span class="detail-value">${walletName}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Address:</span>
                                <span class="detail-value selectable">${wallet.address}</span>
                            </div>
                        </div>
                        
                        <div class="wallet-details-section">
                            <h3>🔐 Private Key (Secret Key)</h3>
                            <div class="warning-box">
                                ⚠️ <strong>WARNING:</strong> Never Share Your Private Key With Anyone! 
                                It Gives Complete Control Over Your Wallet And Funds.
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Private Key:</span>
                                <span class="detail-value selectable private-key">${wallet.sk}</span>
                            </div>
                        </div>
                        
                        <div class="wallet-details-section">
                            <h3>🔓 Public Key (Verification Key)</h3>
                            <div class="detail-row">
                                <span class="detail-label">Public Key:</span>
                                <span class="detail-value selectable">${wallet.vk}</span>
                            </div>
                        </div>
                        
                        <div class="wallet-details-section">
                            <h3>💰 Balance Information</h3>
                            <div class="detail-row">
                                <span class="detail-label">Current Balance:</span>
                                <span class="detail-value">${wallet.balance || 0} Coins</span>
                            </div>
                        </div>
                        
                        <div class="modal-actions">
                            <button class="btn btn-primary" onclick="copyToClipboard('${wallet.address}')">Copy Address</button>
                            <button class="btn btn-secondary" onclick="copyToClipboard('${wallet.sk}')">Copy Private Key</button>
                            <button class="btn btn-secondary" onclick="closeWalletDetails()">Close</button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(popup);
                
                // Close On Background Click
                popup.addEventListener('click', (e) => {
                    if (e.target === popup) {
                        closeWalletDetails();
                    }
                });
                
                // Make Functions Global For Onclick Handlers
                window.closeWalletDetails = () => {
                    document.body.removeChild(popup);
                    delete window.closeWalletDetails;
                    delete window.copyToClipboard;
                };
                
                window.copyToClipboard = (text) => {
                    navigator.clipboard.writeText(text).then(() => {
                        showNotification('Copied To Clipboard!', 'success');
                    }).catch(() => {
                        showNotification('Failed To Copy', 'error');
                    });
                };
                
            } else {
                showNotification('Failed To Load Wallet Details', 'error');
            }
        })
        .catch(error => {
            showNotification('Network Error Loading Wallet Details', 'error');
            console.error('Wallet Details Error:', error);
        });
}

function populateWalletSelects(wallets) {
    const selects = [
        'txFromWallet',
        'stakingWallet',
        'contractOwner',
        'tokenOwner',
        'minerSelect'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">Select Wallet...</option>';
            
            wallets.forEach(wallet => {
                const option = document.createElement('option');
                option.value = wallet.name;
                option.textContent = `${wallet.name} (${wallet.address.substring(0, 20)}...)`;
                select.appendChild(option);
            });
            
            if (currentValue) {
                select.value = currentValue;
            }
        }
    });
}

async function createWallet() {
    showPromptPopup('Create New Wallet', 'Enter Wallet Name To Create...', async (name) => {
        try {
            const response = await fetch(`${API_BASE_URL}/wallet/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ name })
            });
            
            const data = await response.json();
            
            if (data.ok) {
                showNotification(`Wallet Created: ${name}`, 'success');
                addActivityLog(`Created Wallet: ${name}`);
                loadWallets();
            } else {
                showNotification('Wallet Creation Failed', 'error');
            }
        } catch (error) {
            showNotification('Network Error', 'error');
            console.error('Wallet Creation Error:', error);
        }
    });
}

function refreshWallets() {
    loadWallets();
    showNotification('Wallets Refreshed', 'info');
}

// Transaction Functions
async function sendTransaction(event) {
    event.preventDefault();
    
    if (!authToken) {
        showNotification('Please Login To Send Transactions', 'warning');
        return;
    }
    
    const from = document.getElementById('txFromWallet').value;
    const to = document.getElementById('txToAddress').value;
    const amount = parseInt(document.getElementById('txAmount').value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/tx/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ from, to, amount })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification('Transaction Sent Successfully', 'success');
            addActivityLog(`Sent ${amount} From ${from} To ${to}`);
            document.getElementById('sendTxForm').reset();
        } else {
            showNotification(data.error || 'Transaction Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Transaction Error:', error);
    }
}

// Mining Functions
async function loadMiners() {
    try {
        const response = await fetch(`${API_BASE_URL}/miners`);
        const data = await response.json();
        
        if (data.miners) {
            const select = document.getElementById('minerSelect');
            select.innerHTML = '<option value="">Select Miner...</option>';
            
            data.miners.forEach(miner => {
                const option = document.createElement('option');
                option.value = miner.name;
                option.textContent = `${miner.name} - Earnings: ${miner.earnings || 0}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Miner Load Error:', error);
    }
}

async function createMiner() {
    showPromptPopup('Create Miner Account', 'Enter Miner Account Name...', async (name) => {
        try {
            const response = await fetch(`${API_BASE_URL}/miners`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name })
            });
            
            const data = await response.json();
            
            if (data.ok) {
                showNotification(`Miner Account Created: ${name}`, 'success');
                addActivityLog(`Created Miner: ${name}`);
                loadMiners();
            } else {
                showNotification('Miner Creation Failed', 'error');
            }
        } catch (error) {
            showNotification('Network Error', 'error');
            console.error('Miner Creation Error:', error);
        }
    });
}

async function startMining() {
    if (!authToken) {
        showNotification('Please Login To Mine Blocks', 'warning');
        return;
    }
    
    const miner = document.getElementById('minerSelect').value;
    if (!miner) {
        showNotification('Please Select A Miner Account', 'warning');
        return;
    }
    
    const btn = document.getElementById('mineBtn');
    btn.disabled = true;
    btn.textContent = 'Mining...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/mining/mine`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ miner })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Block Mined! Reward: ${data.reward}`, 'success');
            addActivityLog(`Mined Block ${data.block.index} - Reward: ${data.reward}`);
            loadDashboard();
        } else {
            showNotification(data.error || 'Mining Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Mining Error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Mine Block';
    }
}

// Smart Contract Functions
async function loadContracts() {
    try {
        const response = await fetch(`${API_BASE_URL}/contracts`);
        const data = await response.json();
        
        if (data.ok) {
            displayContracts(data.contracts);
        }
    } catch (error) {
        console.error('Contract Load Error:', error);
    }
}

function displayContracts(contracts) {
    const container = document.getElementById('contractList');
    container.innerHTML = '';
    
    if (contracts.length === 0) {
        container.innerHTML = '<div class="log-entry">No Contracts Deployed</div>';
        return;
    }
    
    contracts.forEach(contract => {
        const card = document.createElement('div');
        card.className = 'contract-card';
        
        card.innerHTML = `
            <div class="contract-id">Contract ID: ${contract.contract_id}</div>
            <div class="contract-details">
                <div>Owner: ${contract.owner.substring(0, 30)}...</div>
                <div>Balance: ${contract.balance || 0}</div>
                <div>Created: ${new Date(contract.created_at * 1000).toLocaleString()}</div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function showDeployContractModal() {
    if (!authToken) {
        showNotification('Please Login To Deploy Contracts', 'warning');
        return;
    }
    
    document.getElementById('deployContractModal').classList.remove('hidden');
}

function showDeployTokenModal() {
    if (!authToken) {
        showNotification('Please Login To Deploy Tokens', 'warning');
        return;
    }
    
    document.getElementById('deployTokenModal').classList.remove('hidden');
}

async function deployContract(event) {
    event.preventDefault();
    
    const code = document.getElementById('contractCode').value;
    const owner = document.getElementById('contractOwner').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/contract/deploy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ code, owner })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Contract Deployed: ${data.contract_id}`, 'success');
            addActivityLog(`Deployed Contract: ${data.contract_id}`);
            closeModal('deployContractModal');
            document.getElementById('deployContractForm').reset();
            loadContracts();
        } else {
            showNotification(data.error || 'Deployment Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Contract Deployment Error:', error);
    }
}

async function deployToken(event) {
    event.preventDefault();
    
    const name = document.getElementById('tokenName').value;
    const symbol = document.getElementById('tokenSymbol').value;
    const decimals = parseInt(document.getElementById('tokenDecimals').value);
    const total_supply = parseInt(document.getElementById('tokenSupply').value);
    const owner = document.getElementById('tokenOwner').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/token/deploy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ name, symbol, decimals, total_supply, owner })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Token Deployed: ${data.token.name} (${data.token.symbol})`, 'success');
            addActivityLog(`Deployed Token: ${data.token.name}`);
            closeModal('deployTokenModal');
            document.getElementById('deployTokenForm').reset();
            loadContracts();
        } else {
            showNotification(data.error || 'Token Deployment Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Token Deployment Error:', error);
    }
}

// Staking Functions
async function depositStake() {
    if (!authToken) {
        showNotification('Please Login To Stake', 'warning');
        return;
    }
    
    const address = document.getElementById('stakingWallet').value;
    const amount = parseInt(document.getElementById('stakeAmount').value);
    
    if (!address || !amount) {
        showNotification('Please Fill All Fields', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/staking/deposit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ address, amount })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Staked ${amount} Tokens`, 'success');
            addActivityLog(`Staked ${amount} Tokens`);
            updateStakingInfo(address);
        } else {
            showNotification(data.error || 'Staking Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Staking Error:', error);
    }
}

async function withdrawStake() {
    if (!authToken) {
        showNotification('Please Login To Withdraw', 'warning');
        return;
    }
    
    const address = document.getElementById('stakingWallet').value;
    const amount = parseInt(document.getElementById('stakeAmount').value);
    
    if (!address || !amount) {
        showNotification('Please Fill All Fields', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/staking/withdraw`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ address, amount })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Withdrew ${amount} Tokens`, 'success');
            addActivityLog(`Withdrew ${amount} Tokens`);
            updateStakingInfo(address);
        } else {
            showNotification(data.error || 'Withdrawal Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Withdrawal Error:', error);
    }
}

async function claimRewards() {
    if (!authToken) {
        showNotification('Please Login To Claim Rewards', 'warning');
        return;
    }
    
    const address = document.getElementById('stakingWallet').value;
    
    if (!address) {
        showNotification('Please Select A Wallet', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/staking/rewards/${address}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Claimed ${data.claimed} Rewards`, 'success');
            addActivityLog(`Claimed ${data.claimed} Rewards`);
            updateStakingInfo(address);
        } else {
            showNotification(data.error || 'Claim Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Claim Error:', error);
    }
}

async function updateStakingInfo(address) {
    try {
        const response = await fetch(`${API_BASE_URL}/staking/${address}`);
        const data = await response.json();
        
        if (data.ok) {
            document.getElementById('currentStake').textContent = data.stake;
            document.getElementById('stakingRewards').textContent = data.rewards;
        }
    } catch (error) {
        console.error('Staking Info Error:', error);
    }
}

// Network Functions
async function loadPeers() {
    try {
        const response = await fetch(`${API_BASE_URL}/node/peers`);
        const data = await response.json();
        
        if (data.peers) {
            displayPeers(data.peers);
        }
    } catch (error) {
        console.error('Peer Load Error:', error);
    }
}

function displayPeers(peers) {
    const container = document.getElementById('peerList');
    container.innerHTML = '';
    
    if (peers.length === 0) {
        container.innerHTML = '<div class="log-entry">No Peers Connected</div>';
        return;
    }
    
    peers.forEach(peer => {
        const item = document.createElement('div');
        item.className = 'peer-item';
        
        const status = peer.is_alive ? 'alive' : 'dead';
        
        item.innerHTML = `
            <span class="peer-url">${peer.url || peer.address}</span>
            <span class="peer-status ${status}">${status.toUpperCase()}</span>
        `;
        
        container.appendChild(item);
    });
}

function addPeer() {
    showPromptPopup('Add Network Peer', 'Enter Peer URL (e.g., http://localhost:5001)...', (url) => {
        fetch(`${API_BASE_URL}/node/peers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                showNotification('Peer Added', 'success');
                addActivityLog(`Added Peer: ${url}`);
                loadPeers();
            } else {
                showNotification('Failed To Add Peer', 'error');
            }
        })
        .catch(error => {
            showNotification('Network Error', 'error');
            console.error('Add Peer Error:', error);
        });
    });
}

function refreshPeers() {
    loadPeers();
    showNotification('Peers Refreshed', 'info');
}

async function updateConsensus() {
    const algorithm = document.getElementById('consensusAlgorithm').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/consensus`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ algorithm })
        });
        
        const data = await response.json();
        
        if (data.ok) {
            showNotification(`Consensus Updated To ${algorithm.toUpperCase()}`, 'success');
            addActivityLog(`Updated Consensus To ${algorithm.toUpperCase()}`);
            loadDashboard();
        } else {
            showNotification('Consensus Update Failed', 'error');
        }
    } catch (error) {
        showNotification('Network Error', 'error');
        console.error('Consensus Update Error:', error);
    }
}

// Utility Functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    // Auto-remove After 5 Seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 5000);
}

// Add Slide Out Animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
