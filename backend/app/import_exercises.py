import pandas as pd
import os
import psycopg2
from psycopg2.extras import execute_values
import logging
from typing import Optional
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSVToPostgreSQL:
    def __init__(
        self, host: str, database: str, user: str, password: str, port: int = 5432
    ):
        """
        Initialize the CSV to PostgreSQL exporter

        Args:
            host: PostgreSQL host
            database: Database name
            user: Username
            password: Password
            port: Port (default 5432)
        """
        self.connection_params = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port,
        }
        self.connection = None

    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def create_table_from_csv(
        self, csv_file: str, table_name: str, schema: str = "public"
    ) -> bool:
        """
        Create table based on CSV structure

        Args:
            csv_file: Path to CSV file
            table_name: Name of the table to create
            schema: Database schema (default 'public')
        """
        try:
            # Read CSV to infer data types
            df = pd.read_csv(
                csv_file, nrows=1000
            )  # Sample first 1000 rows for type inference

            # Map pandas dtypes to PostgreSQL types
            dtype_mapping = {
                "object": "TEXT",
                "int64": "BIGINT",
                "int32": "INTEGER",
                "float64": "DOUBLE PRECISION",
                "float32": "REAL",
                "bool": "BOOLEAN",
                "datetime64[ns]": "TIMESTAMP",
            }

            # Build CREATE TABLE statement
            columns = []
            for col, dtype in df.dtypes.items():
                pg_type = dtype_mapping.get(str(dtype), "TEXT")
                # Clean column name (replace spaces and special chars with underscores)
                clean_col = col.replace(" ", "_").replace("-", "_").replace(".", "_")
                columns.append(f'"{clean_col}" {pg_type}')

            create_sql = f"""
            DROP TABLE IF EXISTS {schema}.{table_name};
            CREATE TABLE {schema}.{table_name} (
                {", ".join(columns)}
            );
            """

            cursor = self.connection.cursor()
            cursor.execute(create_sql)
            self.connection.commit()
            cursor.close()

            logger.info(f"Table {schema}.{table_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating table: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def export_csv_to_table(
        self,
        csv_file: str,
        table_name: str,
        schema: str = "public",
        chunk_size: int = 1000,
        create_table: bool = True,
    ) -> bool:
        """
        Export CSV data to PostgreSQL table

        Args:
            csv_file: Path to CSV file
            table_name: Target table name
            schema: Database schema
            chunk_size: Number of rows to insert at once
            create_table: Whether to create table first
        """
        try:
            if create_table:
                if not self.create_table_from_csv(csv_file, table_name, schema):
                    return False

            # Read and process CSV in chunks
            total_rows = 0
            cursor = self.connection.cursor()

            for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
                # Clean column names to match table
                chunk.columns = [
                    col.replace(" ", "_").replace("-", "_").replace(".", "_")
                    for col in chunk.columns
                ]

                # Replace NaN with None for proper NULL handling
                chunk = chunk.where(pd.notnull(chunk), None)

                # Prepare data for insertion
                columns = ", ".join([f'"{col}"' for col in chunk.columns])
                values = [tuple(row) for row in chunk.values]

                # Insert data using execute_values for better performance
                insert_sql = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES %s"
                execute_values(cursor, insert_sql, values, page_size=chunk_size)

                total_rows += len(chunk)
                logger.info(f"Inserted {len(chunk)} rows (Total: {total_rows})")

            self.connection.commit()
            cursor.close()

            logger.info(
                f"Successfully exported {total_rows} rows to {schema}.{table_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Error exporting CSV to PostgreSQL: {e}")
            if self.connection:
                self.connection.rollback()
            return False


def main():
    # Database configuration
    DB_CONFIG = {
        "host": "localhost",
        "database": "workoutbuddy",  # Updated for exercise data
        "user": "wk",
        "password": "workoutbuddy",
        "port": 5432,
    }

    # File and table configuration
    CSV_FILE = os.path.join(
        os.path.dirname(__file__), "../../data/exercise_table_ext.csv"
    )
    # CSV_FILE = 'data/exercise_table_ext.csv'  # Your exercise CSV file
    TABLE_NAME = "exercises"  # More descriptive table name
    SCHEMA = "public"

    # Initialize exporter
    exporter = CSVToPostgreSQL(**DB_CONFIG)

    try:
        # Connect to database
        if not exporter.connect():
            sys.exit(1)

        # Export CSV to PostgreSQL
        success = exporter.export_csv_to_table(
            csv_file=CSV_FILE,
            table_name=TABLE_NAME,
            schema=SCHEMA,
            chunk_size=1000,
            create_table=True,
        )

        if success:
            print(
                f"✅ Exercise data successfully exported to PostgreSQL table: {SCHEMA}.{TABLE_NAME}"
            )
            print(f"📊 Table structure:")
            print(f"   - exercise_name: Exercise name")
            print(f"   - short_description: Brief description of the exercise")
            print(f"   - main_muscle_group: Primary muscles targeted")
            print(f"   - equipment_required: Equipment needed")
            print(f"   - difficulty_level: Beginner/Intermediate/Advanced")
            print(f"   - key_form_cues: Important form points")
            print(f"   - visual_reference: Reference links/sources")
        else:
            print("❌ Failed to export exercise data")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        exporter.disconnect()


if __name__ == "__main__":
    main()
