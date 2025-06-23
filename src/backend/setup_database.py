#!/usr/bin/env python3
"""
Script to set up the database tables using SQLAlchemy models
"""

import logging
import sys
from pathlib import Path

from sqlalchemy import text

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.database import Base, SessionLocal, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Set up database tables using SQLAlchemy models"""
    db = SessionLocal()
    try:
        logger.info("Dropping all existing tables...")

        # Drop all tables with CASCADE to handle foreign key dependencies
        db.execute(text("DROP SCHEMA public CASCADE"))
        db.execute(text("CREATE SCHEMA public"))
        db.execute(text("GRANT ALL ON SCHEMA public TO pulse"))
        db.execute(text("GRANT ALL ON SCHEMA public TO public"))

        db.commit()

        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)

        logger.info("Database tables created successfully")
        return True

    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_tables():
    """Verify that tables were created correctly"""
    db = SessionLocal()
    try:
        # Check if exercises table exists and has the right columns
        result = db.execute(
            text(
                """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'exercises'
            ORDER BY ordinal_position
        """
            )
        )

        columns = result.fetchall()
        logger.info("Exercises table columns:")
        for column in columns:
            logger.info(f"  {column[0]}: {column[1]}")

        # Check table count
        result = db.execute(text("SELECT COUNT(*) FROM exercises"))
        count = result.scalar()
        logger.info(f"Exercises table has {count} rows")

        return True

    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False
    finally:
        db.close()


def main():
    """Main function"""
    logger.info("Setting up database...")

    # Set up database
    success = setup_database()

    if success:
        logger.info("Database setup completed successfully")

        # Verify tables
        verify_tables()
    else:
        logger.error("Database setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
