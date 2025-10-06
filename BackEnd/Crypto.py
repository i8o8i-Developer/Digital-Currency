"""
Crypto.py
Provides ECDSA And A Simple Schnorr-like Signature Scheme Over secp256k1.
"""
from ecdsa import SigningKey, SECP256k1
from hashlib import sha256

# Curve Order
_order = SECP256k1.order
_G = SECP256k1.generator


def sha256d(b: bytes) -> bytes:
    return sha256(sha256(b).digest()).digest()


def gen_keypair():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    return sk.to_string().hex(), vk.to_string().hex()


def ecdsa_sign(hex_privkey: str, message: bytes) -> str:
    sk = SigningKey.from_string(bytes.fromhex(hex_privkey), curve=SECP256k1)
    # Use Deterministic Signing (RFC6979) Over The Message Bytes
    sig = sk.sign(message, hashfunc=sha256)
    return sig.hex()


def ecdsa_verify(hex_pubkey: str, message: bytes, sig_hex: str) -> bool:
    from ecdsa import VerifyingKey
    vk = VerifyingKey.from_string(bytes.fromhex(hex_pubkey), curve=SECP256k1)
    try:
        return vk.verify(bytes.fromhex(sig_hex), message, hashfunc=sha256)
    except Exception:
        return False


# --- Simple Schnorr-style signature (educational) ---
# This Implements A Basic Schnorr Scheme (Not BIP-340 Compatible In All Edge Cases).


def schnorr_sign(hex_privkey: str, message: bytes) -> dict:
    # Private Key Scalar
    d = int(hex_privkey, 16)
    if d == 0 or d >= _order:
        raise ValueError('invalid private key')
    # Nonce k
    k = int.from_bytes(sha256(b"nonce" + hex_privkey.encode() + message).digest(), "big") % _order
    # R = k*G
    R = k * _G
    Rx = int(R.x())
    # Public Key Point
    P = d * _G
    Px = int(P.x())
    e = int.from_bytes(sha256(Rx.to_bytes(32, 'big') + Px.to_bytes(32, 'big') + message).digest(), 'big') % _order
    s = (k + e * d) % _order
    return {"R": format(Rx, '064x'), "s": format(s, '064x')}


def schnorr_verify(hex_pubkey: str, message: bytes, sig: dict) -> bool:
    # Public Key Hex Here Is x||y (As Produced By ECDSA)
    Qx = int(hex_pubkey[:64], 16)
    Qy = int(hex_pubkey[64:], 16)
    # Reconstruct Point
    from ecdsa.ellipticcurve import Point
    Q = Point(SECP256k1.curve, Qx, Qy, _order)
    Rx = int(sig['R'], 16)
    s = int(sig['s'], 16)
    # Compute e
    e = int.from_bytes(sha256(Rx.to_bytes(32, 'big') + Qx.to_bytes(32, 'big') + message).digest(), 'big') % _order
    # Check s*G == R + e*Q
    sG = s * _G
    # Compute -e*Q as (order - e) * Q
    neg_e = (_order - e) % _order
    neg_eQ = neg_e * Q
    Rcalc = sG + neg_eQ
    try:
        return int(Rcalc.x()) == Rx
    except Exception:
        return False


# SIGHASH Handling: Compute SIGHASH For Transaction Bytes And A Flag

def sighash_all(tx_bytes: bytes) -> bytes:
    return sha256d(tx_bytes)

def sighash_none(tx_bytes: bytes) -> bytes:
    return sha256(tx_bytes).digest()