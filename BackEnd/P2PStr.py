"""
P2PStr.py
A Tiny Peer-to-Peer Gossip Layer Using HTTP Broadcast (Simple). For Real P2P You'd Use Raw TCP/UDP With Discovery.
"""
import threading
import requests
import time

class PeerNetwork:
    def __init__(self):
        self.peers = set()
        self.lock = threading.Lock()

    def add_peer(self, url: str):
        with self.lock:
            self.peers.add(url)

    def remove_peer(self, url: str):
        with self.lock:
            self.peers.discard(url)

    def broadcast(self, path: str, payload: dict):
        urls = list(self.peers)
        for u in urls:
            try:
                requests.post(u.rstrip('/') + path, json=payload, timeout=2)
            except Exception:
                pass

    def list_peers(self):
        with self.lock:
            return list(self.peers)
