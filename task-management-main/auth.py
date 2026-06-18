import sqlite3
import hashlib
from database import Database

class User():
    """Represents an authenticated user."""
    def __init__(self, user_id: str, username: str, email: str ):
        self.user_id = user_id
        self.username = username
        self.email = email
    
    def __repr__(self):
        return f"User(id={self.user_id},username='{self.username}', email='{self.email}')"

class Auth():
    """
    Handles register and login with Supabase users table.
    """
    def __init__(self, db = Database()):
        self.client = db.get_client()
    ##encrypting password
    @staticmethod
    def _hash_pass(password):
        return hashlib.sha256(password.encode()).hexdigest()
    def register_user(self, username: str, email: str, password: str) -> bool:
        """
        Handles user registeration, returns True on success,
        Returns False if username or email already exists
        """
        try:
            response = self.client.table('users').insert(
                {
                    'username': username,
                    'email': email,
                    'password': self._hash_pass(password)                   

                }
            ).execute()

            return len(response.data) > 0
        except Exception:
            return False

    def login(self, username: str, password: str):
        """
        Returns a User object on success, None on failure.
        """

        response = (self.client.table('users').
                    select('id,username,email').
                    eq('username', username).
                    eq('password', self._hash_pass(password))
                    .execute()

                    )
        if response.data:
            row = response.data
            return User(
                user_id = row[0]['id'],
                username = row[0]['username'],
                email = row[0]['email']
            )
        
        return None
            




