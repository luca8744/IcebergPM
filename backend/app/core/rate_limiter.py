"""
Rate Limiter — Protezione brute-force per endpoint di login.
Tiene traccia dei tentativi falliti per IP e blocca temporaneamente
dopo un numero configurabile di errori consecutivi.
"""

import time
import threading
from typing import Dict, Tuple


# Configurazione
MAX_ATTEMPTS = 5          # Tentativi massimi prima del blocco
WINDOW_SECONDS = 300      # Finestra temporale (5 minuti)
CLEANUP_INTERVAL = 60     # Pulizia automatica ogni 60 secondi


class RateLimiter:
    """Rate limiter in-memory thread-safe per tentativi di login."""

    def __init__(self, max_attempts: int = MAX_ATTEMPTS, window_seconds: int = WINDOW_SECONDS):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        # key -> (attempt_count, first_attempt_timestamp)
        self._attempts: Dict[str, Tuple[int, float]] = {}
        self._lock = threading.Lock()

    def _make_key(self, ip: str, username: str) -> str:
        """Genera una chiave combinata IP + username."""
        return f"{ip}::{username}"

    def is_blocked(self, ip: str, username: str) -> Tuple[bool, int]:
        """
        Controlla se l'IP/username è bloccato.
        Ritorna (is_blocked, seconds_remaining).
        """
        key = self._make_key(ip, username)
        now = time.time()

        with self._lock:
            if key not in self._attempts:
                return False, 0

            count, first_ts = self._attempts[key]

            # Finestra scaduta → reset
            if now - first_ts > self.window_seconds:
                del self._attempts[key]
                return False, 0

            if count >= self.max_attempts:
                remaining = int(self.window_seconds - (now - first_ts))
                return True, max(remaining, 1)

            return False, 0

    def record_failure(self, ip: str, username: str) -> None:
        """Registra un tentativo fallito."""
        key = self._make_key(ip, username)
        now = time.time()

        with self._lock:
            if key in self._attempts:
                count, first_ts = self._attempts[key]
                # Finestra scaduta → ricomincia
                if now - first_ts > self.window_seconds:
                    self._attempts[key] = (1, now)
                else:
                    self._attempts[key] = (count + 1, first_ts)
            else:
                self._attempts[key] = (1, now)

    def record_success(self, ip: str, username: str) -> None:
        """Reset dei tentativi dopo un login riuscito."""
        key = self._make_key(ip, username)
        with self._lock:
            self._attempts.pop(key, None)

    def cleanup(self) -> None:
        """Rimuove le entry scadute per evitare memory leak."""
        now = time.time()
        with self._lock:
            expired = [k for k, (_, ts) in self._attempts.items()
                       if now - ts > self.window_seconds]
            for k in expired:
                del self._attempts[k]


# Singleton globale
login_limiter = RateLimiter()
