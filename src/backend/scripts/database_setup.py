#!/usr/bin/env python3
"""
Database setup script for Pulse Fitness application.

This script handles the creation and verification of database tables
using SQLAlchemy models.
"""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.database import Base, SessionLocal, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseSetupError(Exception):
    """Custom exception for database setup errors."""

    pass


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseManager:
    """Manages database operations for the application."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def drop_all_tables(self, session: Session) -> None:
        """Drop all existing tables and recreate the schema."""
        try:
            logger.info("Dropping all existing tables...")

            # Drop and recreate the public schema
            session.execute(text("DROP SCHEMA public CASCADE"))
            session.execute(text("CREATE SCHEMA public"))
            session.commit()

            logger.info("Schema reset completed successfully")

        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            session.rollback()
            raise DatabaseSetupError(f"Failed to drop tables: {e}")

    def create_tables(self) -> None:
        """Create all tables using SQLAlchemy models."""
        try:
            logger.info("Creating all tables...")
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseSetupError(f"Failed to create tables: {e}")

    def verify_tables(self) -> list[tuple[str, str]]:
        """Verify that tables were created correctly."""
        with get_db_session() as session:
            try:
                # Check if exercises table exists and has the right columns
                result = session.execute(
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
                result = session.execute(text("SELECT COUNT(*) FROM exercises"))
                count = result.scalar()
                logger.info(f"Exercises table has {count} rows")

                return columns

            except Exception as e:
                logger.error(f"Error verifying tables: {e}")
                raise DatabaseSetupError(f"Failed to verify tables: {e}")

    def setup_database(self, force_reset: bool = False) -> bool:
        """Set up the complete database."""
        try:
            with get_db_session() as session:
                if force_reset:
                    self.drop_all_tables(session)

                self.create_tables()
                self.verify_tables()

            return True

        except DatabaseSetupError:
            return False
        except Exception as e:
            logger.error(f"Unexpected error during database setup: {e}")
            return False


def main(force_reset: bool = False) -> None:
    """Main function to set up the database."""
    logger.info("Starting database setup...")

    try:
        db_manager = DatabaseManager(engine)
        success = db_manager.setup_database(force_reset=force_reset)

        if success:
            logger.info("Database setup completed successfully")
        else:
            logger.error("Database setup failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Set up database tables")
    parser.add_argument(
        "--force-reset", action="store_true", help="Force reset of existing tables"
    )

    args = parser.parse_args()
    main(force_reset=args.force_reset)
