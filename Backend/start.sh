#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

# Function to wait for database
wait_for_db() {
    print_status "Waiting for PostgreSQL to be ready..."
    
    while ! pg_isready -h postgres -p 5432 -U postgres; do
        sleep 2
    done
    
    print_success "PostgreSQL is ready!"
}

# Main execution
main() {
    print_status "Starting XNFL Fantasy API..."
    
    # Wait for database to be ready
    wait_for_db
    
    # Start the FastAPI application
    print_status "Starting FastAPI application..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Execute main function
main "$@"