import pymysql
import subprocess

def fix_db():
    print("Connecting to database...")
    # Connect to the local MySQL database (using settings from .env)
    conn = pymysql.connect(host='127.0.0.1', user='root', database='question')
    cur = conn.cursor()
    
    print("Fixing alembic_version (resetting to the valid base state before the new migration)...")
    cur.execute("UPDATE alembic_version SET version_num = 'b8da4ff8d5eb'")
    conn.commit()
    conn.close()
    
    print("Successfully updated alembic_version.")
    print("Running database migrations (.venv/bin/alembic upgrade head)...")
    
    # Run alembic upgrade head to apply the new migration (which adds the missing columns)
    result = subprocess.run([".venv/bin/alembic", "upgrade", "head"], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors during migration:")
        print(result.stderr)
    else:
        print("Migrations applied successfully!")

if __name__ == "__main__":
    fix_db()
