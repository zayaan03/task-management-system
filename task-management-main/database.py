from supabase import Client, create_client
import os
from dotenv import load_dotenv

# load_dotenv()

class Database():
    '''
    This class creates a single connection with Supabase client (Database)
    which is used in all CRUD functions
    '''
    _instance = None

    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            if not url or not key:
                raise ValueError('SUPABASE_URL and SUPABASE_KEY must be set in .env')
            cls._instance.client: Client = create_client(url, key)
        return cls._instance
    def get_client(self) -> Client:
        return self.client
