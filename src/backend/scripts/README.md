# Database Scripts

This directory contains refactored database management scripts for the Pulse Fitness application.

---

## Quick Examples

### 1. **Set up the database (create/drop tables)**
```bash
# Create tables (if not exist)
python scripts/database_setup.py

# Drop all tables and recreate (DANGER: this deletes all data!)
python scripts/database_setup.py --force-reset
```

### 2. **Import exercises from CSV**
```bash
# Import from the default CSV (data/exercise_table_ext.csv)
python scripts/exercise_importer.py

# Import from a custom CSV and force re-import even if data exists
python scripts/exercise_importer.py --csv-path /path/to/your.csv --force
```

### 3. **Run all tests (including unit tests for import logic)**
```bash
pytest --maxfail=3 --disable-warnings -v
```

### 4. **Use in Python code**
```python
from scripts.exercise_importer import ExerciseImporter

# Import with default settings
importer = ExerciseImporter()
imported_count, error_count = importer.import_exercises()

# Import with custom CSV and force
importer = ExerciseImporter(csv_path=Path("/custom/path.csv"), force_import=True)
imported_count, error_count = importer.import_exercises()
```

---

## File and Class/Function Descriptions

### `database_setup.py`
- **Purpose:** Create or reset all database tables using your SQLAlchemy models.
- **Key Classes/Functions:**
  - `DatabaseManager`: Handles dropping, creating, and verifying tables.
    - `drop_all_tables(session)`: Drops all tables by recreating the schema.
    - `create_tables()`: Creates all tables from SQLAlchemy models.
    - `verify_tables()`: Logs the columns and row count of the `exercises` table.
    - `setup_database(force_reset)`: Orchestrates the full setup/reset process.
  - `main()`: CLI entry point, parses `--force-reset` and runs setup.

### `exercise_importer.py`
- **Purpose:** Import exercise data from a CSV file into the `exercises` table.
- **Key Classes/Functions:**
  - `ExerciseMapper`: Static methods to map CSV fields to model enums/fields.
    - `map_muscle_group`, `map_equipment`, `map_exercise_type`, `map_difficulty`, `parse_list_string`, `calculate_mets`
  - `ExerciseValidator`: Validates each CSV row for required fields and correct types.
    - `validate_exercise_data(row)`: Returns (is_valid, errors)
  - `ExerciseImporter`: Orchestrates the import process.
    - `validate_csv_file()`: Checks file existence.
    - `check_existing_exercises()`: Returns count of existing exercises.
    - `process_csv_row(row)`: Maps and validates a single row.
    - `import_exercises()`: Main import loop, returns (imported_count, error_count).
  - `main()`: CLI entry point, parses `--csv-path` and `--force`.

### `config.py`
- **Purpose:** Centralized configuration for all scripts.
- **Key Class:**
  - `ScriptConfig`: Dataclass holding all config (batch size, mappings, file paths, etc.)
  - `config`: Singleton instance used by all scripts.

### `test_import.py`
- **Purpose:** Unit tests for the import logic (mappings, validation, importer instantiation).
- **Key Functions:**
  - `test_mapper()`: Tests all mapping logic.
  - `test_validator()`: Tests validation logic.
  - `test_importer_creation()`: Tests importer instantiation.
  - `main()`: Runs all tests and logs results.

---

## Overview

The scripts have been refactored according to best practices:

- **Separation of Concerns**: Each script has a single responsibility
- **Configuration Management**: Centralized configuration in `config.py`
- **Error Handling**: Proper exception handling and logging
- **Type Hints**: Full type annotations for better code clarity
- **Context Managers**: Safe database session management
- **Validation**: Data validation before import
- **Testing**: Unit tests for critical functionality

## Scripts

### `database_setup.py`

Sets up the database tables using SQLAlchemy models.

**Usage:**
```bash
python scripts/database_setup.py [--force-reset]
```

**Options:**
- `--force-reset`: Force reset of existing tables

### `exercise_importer.py`

Imports exercise data from CSV files into the database.

**Usage:**
```bash
python scripts/exercise_importer.py [--csv-path PATH] [--force]
```

**Options:**
- `--csv-path`: Path to CSV file (default: `data/exercise_table_ext.csv`)
- `--force`: Force import even if exercises already exist

### `test_import.py`

Tests the refactored exercise importer functionality.

**Usage:**
```bash
python scripts/test_import.py
```

## Configuration

All configuration is centralized in `config.py`:

- **Database settings**: Batch size, retry settings
- **Import settings**: Validation, logging level
- **File paths**: Data directory, CSV file names
- **Mapping configurations**: Muscle groups, equipment, difficulty levels

## Architecture

### ExerciseMapper

Maps CSV data to Exercise model fields:
- Muscle group mapping
- Equipment mapping
- Exercise type detection
- Difficulty level mapping
- METs calculation

### ExerciseValidator

Validates exercise data before import:
- Required field validation
- Field length validation
- Data type validation

### ExerciseImporter

Handles the complete import process:
- CSV file validation
- Data processing and mapping
- Database operations
- Error handling and reporting

## Best Practices Implemented

1. **Error Handling**: Custom exceptions and proper error propagation
2. **Logging**: Structured logging with appropriate levels
3. **Type Safety**: Full type hints throughout
4. **Resource Management**: Context managers for database sessions
5. **Configuration**: Centralized, type-safe configuration
6. **Validation**: Input validation and data integrity checks
7. **Testing**: Unit tests for critical functionality
8. **Documentation**: Comprehensive docstrings and comments

## Example Usage

```python
from scripts.exercise_importer import ExerciseImporter

# Import exercises with default settings
importer = ExerciseImporter()
imported_count, error_count = importer.import_exercises()

# Import exercises with custom settings
importer = ExerciseImporter(
    csv_path=Path("/custom/path/exercises.csv"),
    force_import=True
)
imported_count, error_count = importer.import_exercises()
```

## Migration from Old Scripts

The old scripts (`setup_database.py` and `import_exercises.py`) have been replaced with:

- `database_setup.py` - Improved database setup with better error handling
- `exercise_importer.py` - Refactored importer with configuration management
- `config.py` - Centralized configuration
- `test_import.py` - Unit tests for validation

## How to Extend

- **Add new columns to the model?**
  Update the SQLAlchemy model, then rerun `database_setup.py --force-reset`.
- **Change CSV format?**
  Update mapping logic in `ExerciseMapper` and validation in `ExerciseValidator`.
- **Add new tests?**
  Add functions to `test_import.py` or create new test files in `tests/`.

## Troubleshooting

- **Database errors?**
  Make sure your database is running and matches the connection string in your config.
- **Import errors?**
  Check the warnings for unmapped muscle groups/equipment and update `config.py` mappings as needed.
- **Test failures?**
  Review the error output and ensure all dependencies are installed (`uv pip install -r app/Requirements.txt`).

## Future Improvements

1. **Async Support**: Add async database operations for better performance
2. **Progress Tracking**: Add progress bars for large imports
3. **Dry Run Mode**: Add option to validate without importing
4. **Backup/Restore**: Add database backup before destructive operations
5. **Parallel Processing**: Add parallel processing for large datasets
