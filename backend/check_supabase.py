import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine
import traceback

async def check_connections():
    """
    Loads .env variables and checks Supabase Storage & DB connections.
    """
    print("Attempting to load environment variables from .env file...")
    load_dotenv() 
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    all_vars_present = all([SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, DATABASE_URL])
    
    if not all_vars_present:
        print("---")
        print("❌ ERROR: One or more environment variables are missing from your .env file.")
        if not SUPABASE_URL: print("- SUPABASE_URL is missing")
        if not SUPABASE_KEY: print("- SUPABASE_KEY is missing")
        if not SUPABASE_BUCKET: print("- SUPABASE_BUCKET is missing")
        if not DATABASE_URL: print("- DATABASE_URL is missing")
        return
    
    print("✅ All environment variables found.")
    print(f"   Connecting to Supabase URL: {SUPABASE_URL}")
    print(f"   Using Bucket: {SUPABASE_BUCKET}")
    print("---")
    
    # --- 1. Check Supabase Client & Storage ---
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized.")
        
        buckets = supabase.storage.list_buckets()
        print(f"✅ Supabase Storage connection successful. Found buckets: {[b.name for b in buckets]}")
        
        if SUPABASE_BUCKET not in [b.name for b in buckets]:
            print(f"⚠️ Warning: Bucket '{SUPABASE_BUCKET}' not found. Please create it in your Supabase dashboard.")
    except Exception as e:
        print(f"❌ ERROR connecting to Supabase Storage: {e}")
        return
    
    print("---")
    
    # --- 2. Check Database (Postgres) Connection ---
    try:
        print(f"   Connecting to Database...")
        print(f"   Database URL (masked): {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'invalid'}")
        print(f'DATA_BASE_URL: {DATABASE_URL}')
        
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # This will show SQL queries
            connect_args={
                "server_settings": {"application_name": "rag_backend_check"}
            }
        )
        
        async with engine.connect() as conn:
            from sqlalchemy import text

# Then in the execute:
            result = await conn.execute(text("SELECT now();"))
            db_time = result.scalar()
            print(f"✅ Supabase Postgres connection successful. Database time: {db_time}")
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ ERROR connecting to Supabase Postgres:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n   Full traceback:")
        traceback.print_exc()
        return
    
    print("\n🎉 All connections successful! Your backend is ready.")

if __name__ == "__main__":
    asyncio.run(check_connections())