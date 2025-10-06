"""
P2PNetwork.py
Advanced Peer-To-Peer Networking With Discovery, Gossip, and WebSocket Support.
"""
import asyncio
import websockets
import json
import threading
import time
import requests
from typing import Set, Dict, List, Optional
from urllib.parse import urlparse
from .Config import config
from .logger import logger

class Peer:
    """Represents A Network Peer."""

    def __init__(self, address: str, port: int, last_seen: float = None):
        self.address = address
        self.port = port
        self.last_seen = last_seen or time.time()
        self.is_alive = True
        self.quality_score = 1.0  # For Peer Quality Assessment

    def to_dict(self) -> Dict:
        return {
            'address': self.address,
            'port': self.port,
            'last_seen': self.last_seen,
            'is_alive': self.is_alive,
            'quality_score': self.quality_score
        }

    @property
    def url(self) -> str:
        return f"http://{self.address}:{self.port}"

    def update_last_seen(self):
        """Update The Last Seen Timestamp."""
        self.last_seen = time.time()

    def mark_alive(self):
        """Mark Peer As Alive And Improve Quality Score."""
        self.is_alive = True
        self.quality_score = min(1.0, self.quality_score + 0.1)
        self.update_last_seen()

    def mark_dead(self):
        """Mark Peer As Dead And Reduce Quality Score."""
        self.is_alive = False
        self.quality_score = max(0.0, self.quality_score - 0.2)


class P2PNetwork:
    """Advanced P2P Network With Peer Discovery And Gossip."""

    def __init__(self):
        self.peers: Dict[str, Peer] = {}  # url -> Peer
        self.max_peers = config.get('network.max_peers', 50)
        self.heartbeat_interval = config.get('network.heartbeat_interval', 60)
        self.peer_discovery_interval = config.get('network.peer_discovery_interval', 300)
        self.lock = threading.Lock()
        self.running = False
        self.websocket_server = None
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.shutdown_event = asyncio.Event()

        # Start Background Tasks
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.websocket_thread = None

    def start(self):
        """Start The P2P Network."""
        self.running = True
        self.heartbeat_thread.start()
        self.discovery_thread.start()

        # Start WebSocket Server
        websocket_port = config.get('network.websocket_port', 5001)
        self.websocket_thread = threading.Thread(target=self._run_websocket_server, args=(websocket_port,), daemon=True)
        self.websocket_thread.start()

        logger.info(f"P2P Network Started With Max {self.max_peers} Peers")

    def stop(self):
        """Stop The P2P Network."""
        self.running = False
        self.shutdown_event.set()
        logger.info("P2P Network Stopped")

    def add_peer(self, url: str) -> bool:
        """Add A New Peer To The Network."""
        with self.lock:
            if url in self.peers:
                self.peers[url].mark_alive()
                return True

            if len(self.peers) >= self.max_peers:
                # Remove lowest Quality Peer
                lowest_peer = min(self.peers.values(), key=lambda p: p.quality_score)
                del self.peers[lowest_peer.url]

            try:
                parsed = urlparse(url)
                peer = Peer(parsed.hostname, parsed.port or 5000)
                self.peers[url] = peer
                logger.info(f"Added Peer: {url}")
                return True
            except Exception as e:
                logger.warning(f"Failed To Add Peer {url}: {e}")
                return False

    def remove_peer(self, url: str):
        """Remove A Peer From The Network."""
        with self.lock:
            if url in self.peers:
                del self.peers[url]
                logger.info(f"Removed Peer: {url}")

    def get_alive_peers(self) -> List[str]:
        """Get List of Alive Peer URLs."""
        with self.lock:
            return [url for url, peer in self.peers.items() if peer.is_alive]

    def broadcast(self, endpoint: str, data: Dict, exclude_urls: List[str] = None):
        """Broadcast Message to All Alive Peers."""
        exclude_urls = exclude_urls or []
        alive_peers = [url for url in self.get_alive_peers() if url not in exclude_urls]

        for url in alive_peers:
            try:
                full_url = url.rstrip('/') + endpoint
                response = requests.post(full_url, json=data, timeout=5)
                if response.status_code == 200:
                    self.peers[url].mark_alive()
                else:
                    self.peers[url].mark_dead()
            except Exception as e:
                logger.debug(f"Failed To Broadcast To {url}: {e}")
                self.peers[url].mark_dead()

    async def broadcast_ws(self, message: Dict):
        """Broadcast Message Via WebSocket To Connected Clients."""
        if self.websocket_clients:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_json) for client in self.websocket_clients],
                return_exceptions=True
            )

    def _heartbeat_loop(self):
        """Background Thread For Peer Heartbeat Checks."""
        while self.running:
            try:
                self._check_peer_health()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat Loop Error: {e}")
                time.sleep(10)

    def _discovery_loop(self):
        """Background Thread For Peer Discovery."""
        while self.running:
            try:
                self._discover_peers()
                time.sleep(self.peer_discovery_interval)
            except Exception as e:
                logger.error(f"Discovery Loop Error: {e}")
                time.sleep(30)

    def _check_peer_health(self):
        """Check Health of All Peers."""
        with self.lock:
            for url, peer in list(self.peers.items()):
                try:
                    response = requests.get(f"{url}/node/status", timeout=5)
                    if response.status_code == 200:
                        peer.mark_alive()
                    else:
                        peer.mark_dead()
                except Exception:
                    peer.mark_dead()

                # Remove Dead Peers After Too Many Failures
                if not peer.is_alive and time.time() - peer.last_seen > 3600:  # 1 hour
                    del self.peers[url]

    def _discover_peers(self):
        """Discover New Peers From Existing Peers."""
        alive_peers = self.get_alive_peers()
        discovered_peers = set()

        for url in alive_peers[:5]:  # Ask Only a Few Peers
            try:
                response = requests.get(f"{url}/node/peers", timeout=5)
                if response.status_code == 200:
                    peer_data = response.json()
                    if 'peers' in peer_data:
                        discovered_peers.update(peer_data['peers'])
            except Exception:
                continue

        # Add Discovered Peers
        for peer_url in discovered_peers:
            if peer_url not in self.peers and len(self.peers) < self.max_peers:
                self.add_peer(peer_url)

    def _run_websocket_server(self, port: int):
        """Run WebSocket Server In A Separate Thread."""
        asyncio.run(self._start_websocket_server(port))

    async def _start_websocket_server(self, port: int):
        """Start WebSocket Server For Real-Time Communication."""
        try:
            self.websocket_server = await websockets.serve(
                self._handle_websocket,
                "0.0.0.0",
                port
            )
            logger.info(f"WebSocket Server Started On Port {port}")
            await self.shutdown_event.wait()
        except Exception as e:
            logger.error(f"WebSocket Server Error: {e}")
        finally:
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
                logger.info("WebSocket Server Stopped")

    async def _handle_websocket(self, websocket, path):
        """Handle WebSocket Connections."""
        self.websocket_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    # Handle Incoming Messages
                    await self._process_websocket_message(data, websocket)
                except json.JSONDecodeError:
                    logger.warning("Invalid WebSocket Message Received")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.websocket_clients.remove(websocket)

    async def _process_websocket_message(self, data: Dict, websocket):
        """Process incoming WebSocket messages."""
        msg_type = data.get('type')

        if msg_type == 'new_transaction':
            # Handle New Transaction Announcement
            tx_data = data.get('transaction')
            if tx_data:
                # Forward to Other Peers
                await self.broadcast_ws({
                    'type': 'new_transaction',
                    'transaction': tx_data,
                    'source': str(websocket.remote_address)
                })

        elif msg_type == 'new_block':
            # Handle New Block Announcement
            block_data = data.get('block')
            if block_data:
                # Forward To Other Peers
                await self.broadcast_ws({
                    'type': 'new_block',
                    'block': block_data,
                    'source': str(websocket.remote_address)
                })

        elif msg_type == 'peer_discovery':
            # Handle Peer Discovery Requests
            peers_list = list(self.peers.keys())
            await websocket.send(json.dumps({
                'type': 'peer_list',
                'peers': peers_list
            }))

    def get_network_stats(self) -> Dict:
        """Get Network Statistics."""
        with self.lock:
            alive_count = sum(1 for peer in self.peers.values() if peer.is_alive)
            return {
                'total_peers': len(self.peers),
                'alive_peers': alive_count,
                'dead_peers': len(self.peers) - alive_count,
                'max_peers': self.max_peers,
                'websocket_clients': len(self.websocket_clients)
            }


# Global P2P Network Instance
p2p_network = P2PNetwork()