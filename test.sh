#!/bin/bash
"""
WorkoutBuddy Test Runner Script

Quick and easy way to run tests for WorkoutBuddy application.
Automatically sets up the environment and runs comprehensive tests.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if direnv is installed
check_direnv() {
    if ! command -v direnv &> /dev/null; then
        print_warning "direnv is not installed or not in PATH"
        print_warning "Install direnv for automatic environment loading"
        return 1
    fi
    return 0
}

# Load environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Check if .envrc exists
    if [ ! -f ".envrc" ]; then
        print_error ".envrc file not found!"
        print_error "Please create .envrc with your API keys"
        exit 1
    fi
    
    # Load direnv if available
    if check_direnv; then
        print_status "Loading direnv environment..."
        eval "$(direnv export bash)"
    else
        print_status "Loading environment manually..."
        source .envrc
    fi
    
    # Activate virtual environment
    if [ -d ".venv" ]; then
        print_status "Activating virtual environment..."
        source .venv/bin/activate
    else
        print_error "Virtual environment not found!"
        print_error "Please create .venv: python -m venv .venv"
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --config            Run only configuration tests"
    echo "  --database          Run only database tests"
    echo "  --verbose, -v       Verbose output"
    echo "  --quick             Quick tests (config + environment only)"
    echo ""
    echo "Examples:"
    echo "  $0                  Run all tests"
    echo "  $0 --config        Run configuration tests only"
    echo "  $0 --database       Run database tests only"
    echo "  $0 --verbose        Run all tests with verbose output"
    echo "  $0 --quick          Run quick tests only"
}

# Main execution
main() {
    print_status "🏋️ WorkoutBuddy Test Runner"
    echo "=============================================="
    
    # Parse arguments
    VERBOSE=""
    CONFIG_ONLY=""
    DB_ONLY=""
    QUICK=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_usage
                exit 0
                ;;
            --config)
                CONFIG_ONLY="--config-only"
                shift
                ;;
            --database)
                DB_ONLY="--db-only"
                shift
                ;;
            --verbose|-v)
                VERBOSE="--verbose"
                shift
                ;;
            --quick)
                QUICK="true"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Setup environment
    setup_environment
    
    # Run tests
    if [ "$QUICK" = "true" ]; then
        print_status "Running quick tests..."
        python -c "
import os
import sys
sys.path.append('ml_backend')

print('🧪 Quick Configuration Test')
print('=' * 40)

# Test environment variables
anthropic = os.getenv('ANTHROPIC_API_KEY')
posthog = os.getenv('POSTHOG_API_KEY')

if anthropic and posthog:
    print('✅ Environment variables loaded')
else:
    print('❌ Environment variables missing')
    sys.exit(1)

# Test configuration
try:
    from ml_backend.app.config import backend_config
    print('✅ Configuration loaded')
    print(f'   AI enabled: {backend_config.ai.enabled}')
    print(f'   Analytics enabled: {backend_config.analytics.enabled}')
except Exception as e:
    print(f'❌ Configuration failed: {e}')
    sys.exit(1)

print('🎉 Quick tests passed!')
"
    else
        print_status "Running comprehensive tests..."
        python run_tests.py $VERBOSE $CONFIG_ONLY $DB_ONLY
    fi
    
    # Check exit code
    if [ $? -eq 0 ]; then
        print_success "All tests completed successfully! 🚀"
    else
        print_error "Some tests failed. Please check the output above."
        exit 1
    fi
}

# Run main function
main "$@" 