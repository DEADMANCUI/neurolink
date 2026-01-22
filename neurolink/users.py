import os
import json
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Roles
ROLE_ADMIN = "system_admin"
ROLE_COMMANDER = "commander"
ROLE_SOLDIER = "soldier"

# Define permissions sets (strings) — expand as needed
PERMISSIONS = {
    ROLE_ADMIN: {"manage_users", "view_reports", "send_commands", "view_status", "configure_system"},
    ROLE_COMMANDER: {"view_reports", "send_commands", "view_status"},
    ROLE_SOLDIER: {"view_status"},
}

DEFAULT_STORE_FILENAME = "users.json"

PBKDF2_ITER = 100_000
HASH_NAME = "sha256"


@dataclass
class User:
    username: str
    role: str
    salt: str
    pwd_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {"username": self.username, "role": self.role, "salt": self.salt, "pwd_hash": self.pwd_hash}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "User":
        return User(username=d["username"], role=d["role"], salt=d["salt"], pwd_hash=d["pwd_hash"])


class UserManager:
    def __init__(self, store_path: Optional[str] = None):
        if store_path is None:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
            store_path = os.path.join(base, DEFAULT_STORE_FILENAME)
        self.store_path = store_path
        self.users: Dict[str, User] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for u in data.get("users", []):
                    user = User.from_dict(u)
                    self.users[user.username] = user
            except Exception:
                # if file corrupt, start fresh
                self.users = {}
        else:
            self.users = {}

    def _save(self):
        data = {"users": [u.to_dict() for u in self.users.values()]}
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        # returns (salt_hex, hash_hex)
        if salt is None:
            salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac(HASH_NAME, password.encode("utf-8"), salt, PBKDF2_ITER)
        return salt.hex(), dk.hex()

    def create_user(self, username: str, password: str, role: str) -> User:
        if username in self.users:
            raise ValueError("user exists")
        salt_hex, hash_hex = self._hash_password(password)
        user = User(username=username, role=role, salt=salt_hex, pwd_hash=hash_hex)
        self.users[username] = user
        self._save()
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        u = self.users.get(username)
        if not u:
            return None
        salt = bytes.fromhex(u.salt)
        dk = hashlib.pbkdf2_hmac(HASH_NAME, password.encode("utf-8"), salt, PBKDF2_ITER)
        if hmac.compare_digest(dk.hex(), u.pwd_hash):
            return u
        return None

    def get_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def has_permission(self, username: str, permission: str) -> bool:
        u = self.get_user(username)
        if not u:
            return False
        perms = PERMISSIONS.get(u.role, set())
        # admin implicitly has all permissions in PERMISSIONS mapping
        return permission in perms

    def set_password(self, username: str, new_password: str) -> None:
        u = self.get_user(username)
        if not u:
            raise KeyError("user not found")
        salt_hex, hash_hex = self._hash_password(new_password)
        u.salt = salt_hex
        u.pwd_hash = hash_hex
        self._save()

    def delete_user(self, username: str) -> None:
        if username in self.users:
            del self.users[username]
            self._save()
        else:
            raise KeyError("user not found")

    def update_role(self, username: str, role: str) -> None:
        u = self.get_user(username)
        if not u:
            raise KeyError("user not found")
        u.role = role
        self._save()


# Convenience: global manager that auto-creates admin if missing
_manager: Optional[UserManager] = None


def get_manager() -> UserManager:
    global _manager
    if _manager is None:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        store = os.path.join(base, DEFAULT_STORE_FILENAME)
        _manager = UserManager(store)
        # ensure admin exists
        if "admin" not in _manager.users:
            try:
                _manager.create_user("admin", "admin", ROLE_ADMIN)
                print("[users] Created default admin/admin")
            except Exception:
                pass
    return _manager


if __name__ == "__main__":
    m = get_manager()
    print("Users:")
    for u in m.users.values():
        print(u.username, u.role)
