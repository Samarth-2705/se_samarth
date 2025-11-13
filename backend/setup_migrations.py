"""
Setup Flask-Migrate for database migrations
Run this once to initialize migrations
"""
import os
from flask_migrate import init, migrate, upgrade
from app import create_app, db

def setup_migrations():
    """Initialize Flask-Migrate"""
    app = create_app()

    if os.path.exists('migrations'):
        print("⚠️  Migrations folder already exists!")
        return

    with app.app_context():
        # Initialize migrations
        print("Initializing Flask-Migrate...")
        init()

        # Create initial migration
        print("Creating initial migration...")
        migrate(message='Initial migration')

        # Apply migration
        print("Applying migration...")
        upgrade()

        print("✓ Migrations setup complete!")
        print("\nFuture database changes:")
        print("  1. Make changes to your models")
        print("  2. Run: flask db migrate -m 'description of change'")
        print("  3. Run: flask db upgrade")

if __name__ == '__main__':
    setup_migrations()
