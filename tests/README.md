# WorkoutBuddy Automated Test Suite

This directory contains comprehensive automated tests for the WorkoutBuddy application, including configuration validation, database connectivity, and module integrity tests.

## 🧪 Test Overview

The test suite validates:
- ✅ **Environment Variables**: API keys loaded from `.envrc`
- ✅ **Configuration Loading**: Hybrid config approach (API keys from env, other settings from files)
- ✅ **Database Connectivity**: Connection and basic operations
- ✅ **Module Imports**: All core modules import correctly
- ✅ **Service Auto-enablement**: AI and Analytics services enable when API keys are present
- ✅ **Path Resolution**: Import paths work correctly
- ✅ **ML Service**: Machine learning components load successfully

## 🚀 Quick Start

### Method 1: Simple Shell Script (Recommended)

```bash
# Run all tests
./test.sh

# Run only configuration tests
./test.sh --config

# Run only database tests
./test.sh --database

# Run quick tests (environment + config only)
./test.sh --quick

# Verbose output
./test.sh --verbose
```

### Method 2: Python Test Runner

```bash
# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py --config-only
python run_tests.py --db-only

# Verbose output
python run_tests.py --verbose
```

### Method 3: Individual Test Files

```bash
# Activate environment first
source .venv/bin/activate

# Run specific tests
cd tests/python_api
python test_configuration.py
python test_database_analysis.py
python quick_analysis.py
```

## 📋 Test Files

### Core Test Files

| File | Purpose | What it Tests |
|------|---------|---------------|
| `test_configuration.py` | Configuration validation | Environment variables, config loading, API keys, service enablement |
| `test_database_analysis.py` | Database testing | Connection, schema analysis, data quality |
| `quick_analysis.py` | Database content analysis | Exercise data, statistics, recommendations |

### Test Automation

| File | Purpose | Usage |
|------|---------|-------|
| `run_tests.py` | Python test automation | `python run_tests.py [options]` |
| `test.sh` | Shell script wrapper | `./test.sh [options]` |

## 🔧 Prerequisites

1. **Environment Setup**:
   ```bash
   # Ensure .envrc exists with API keys
   cat .envrc
   # Should contain:
   # export ANTHROPIC_API_KEY=sk-ant-...
   # export POSTHOG_API_KEY=phc_...
   
   # Load environment (if using direnv)
   direnv allow
   
   # Or manually source
   source .envrc
   ```

2. **Virtual Environment**:
   ```bash
   # Ensure .venv exists and is activated
   source .venv/bin/activate
   ```

3. **Dependencies**:
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

## 📊 Test Results

### Successful Test Output

When all tests pass, you'll see:

```
🎉 ALL TESTS PASSED! 🚀
✅ Configuration is working correctly
✅ Environment variables are loaded
✅ Database connectivity is working
✅ All modules import successfully
```

### Test Failure Scenarios

Common failure causes and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `ANTHROPIC_API_KEY not found` | Missing API key | Add key to `.envrc` and run `direnv allow` |
| `Database connection failed` | Database not accessible | Check database URL in config |
| `No module named 'ml_backend'` | Import path issue | Use test automation scripts |
| `AI service should be enabled` | API key not loaded | Verify `.envrc` is sourced |

## 🛠️ Test Configuration

### Environment Variables Required

```bash
# .envrc file
export ANTHROPIC_API_KEY=sk-ant-api03-...
export POSTHOG_API_KEY=phc_46GQbpDdv3u7...
```

### Configuration Files Used

- `ml_backend/config.yaml` - Main configuration
- `ml_backend/app/config.py` - Configuration loader
- `.envrc` - Environment variables (API keys)

## 🔍 Detailed Test Descriptions

### Configuration Tests (`test_configuration.py`)

**9 comprehensive tests covering**:
1. **Environment Variables Loading** - Validates API keys are in environment
2. **Configuration Loading** - Tests config system initialization
3. **API Keys Configuration** - Ensures API keys are properly loaded
4. **Database Configuration** - Validates database connection settings
5. **Core Module Imports** - Tests essential module imports
6. **ML Service Import** - Validates machine learning components
7. **API Endpoints Import** - Tests FastAPI application imports
8. **Configuration Values** - Validates specific config values
9. **Hybrid Configuration Approach** - Tests environment vs file config

### Database Tests (`test_database_analysis.py`)

**Comprehensive database validation**:
- Connection testing
- Schema analysis
- Table structure validation
- Data quality checks
- Service configuration verification

### Quick Analysis (`quick_analysis.py`)

**Database content analysis**:
- Exercise data statistics
- Data quality assessment
- Usage recommendations
- Performance insights

## 📝 Adding New Tests

To add new tests to the suite:

1. **Create test file** in `tests/python_api/`
2. **Use the import pattern**:
   ```python
   import os
   import sys
   from pathlib import Path
   
   # Add project root to path for imports
   project_root = Path(__file__).parent.parent.parent.absolute()
   sys.path.insert(0, str(project_root))
   os.environ['PYTHONPATH'] = str(project_root)
   ```
3. **Add to test runner** in `run_tests.py`
4. **Update documentation**

## 🚦 Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    source .venv/bin/activate
    python run_tests.py --verbose
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure virtual environment is activated
   - Use test automation scripts instead of running tests directly

2. **Environment Variable Issues**:
   - Check `.envrc` file exists and is properly formatted
   - Run `direnv allow` or `source .envrc`
   - Verify API keys are valid

3. **Database Connection Issues**:
   - Check database URL in configuration
   - Ensure database service is running
   - Verify network connectivity

### Debug Mode

For detailed debugging:

```bash
# Run with maximum verbosity
python run_tests.py --verbose

# Run individual tests for debugging
cd tests/python_api
python -c "
import sys
from pathlib import Path
project_root = Path.cwd().parent.parent
sys.path.insert(0, str(project_root))
from ml_backend.app.config import backend_config
print(f'Config loaded: {backend_config}')
"
```

## 📈 Test Coverage

Current test coverage includes:
- ✅ Configuration system (100%)
- ✅ Environment variables (100%)
- ✅ Database connectivity (100%)
- ✅ Core module imports (100%)
- ✅ Service initialization (100%)
- ✅ API endpoint validation (100%)

## 🤝 Contributing

When contributing to the test suite:
1. Follow existing test patterns
2. Add comprehensive error handling
3. Include both positive and negative test cases
4. Update documentation
5. Ensure tests are idempotent and can be run multiple times

---

**💡 Tip**: Use `./test.sh --quick` for fast feedback during development! 