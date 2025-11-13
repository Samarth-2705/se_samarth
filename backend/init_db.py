"""
Initialize the database with all tables
"""
from app import create_app, db

def init_database():
    """Create all database tables"""
    app = create_app()

    with app.app_context():
        # Drop all tables (if any)
        print("Dropping existing tables...")
        db.drop_all()

        # Create all tables
        print("Creating all tables...")
        db.create_all()

        print("✓ Database initialized successfully!")
        print("\nCreated tables:")

        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f"  - {table_name}")

if __name__ == '__main__':
    init_database()
