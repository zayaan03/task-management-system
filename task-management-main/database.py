from supabase import Client, create_client
import os
from dotenv import load_dotenv

# load_dotenv()

class Database():
    '''
    This class creates a single connection with Supabase client (Database)
    which is used in all CRUD functions
    '''
    def __init__(self):
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')

        if not url or not key:
            raise ValueError("Supabase credentials not found")

        self.client = create_client(url, key)

    def get_client(self):
        return self.client
