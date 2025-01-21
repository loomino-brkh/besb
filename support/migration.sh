#!/bin/bash

# Exit on any error
set -e

# Activate virtual environment
source /app/support/venv/bin/activate

# Change to the main directory where alembic.ini is located
cd /app/main

# Function to display usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  init      - Initialize alembic migrations"
    echo "  create    - Create a new migration (requires -m message)"
    echo "  upgrade   - Upgrade to the latest version"
    echo "  downgrade - Downgrade to the previous version"
    echo "  history   - Show migration history"
    echo "  current   - Show current revision"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 create -m 'add user table'"
    echo "  $0 upgrade"
    echo "  $0 downgrade"
}

# Function to check if alembic is initialized
check_alembic_initialized() {
    if [ ! -d "migrations" ]; then
        echo "Error: Alembic is not initialized. Run '$0 init' first."
        exit 1
    fi
}

# Main logic
case "$1" in
    "init")
        if [ -d "migrations" ]; then
            echo "Migrations directory already exists!"
            exit 1
        fi
        echo "Initializing alembic..."
        alembic init migrations
        echo "Done! Now edit migrations/env.py to configure your models"
        ;;
    
    "create")
        check_alembic_initialized
        if [ -z "$2" ] || [ "$2" != "-m" ] || [ -z "$3" ]; then
            echo "Error: Migration message required"
            echo "Usage: $0 create -m 'your message here'"
            exit 1
        fi
        echo "Creating new migration..."
        alembic revision --autogenerate -m "$3"
        echo "Done! Review the generated migration file before applying"
        ;;
    
    "upgrade")
        check_alembic_initialized
        echo "Upgrading database to latest version..."
        alembic upgrade head
        echo "Done!"
        ;;
    
    "downgrade")
        check_alembic_initialized
        echo "Downgrading database one version..."
        alembic downgrade -1
        echo "Done!"
        ;;
    
    "history")
        check_alembic_initialized
        echo "Migration history:"
        alembic history --verbose
        ;;
    
    "current")
        check_alembic_initialized
        echo "Current revision:"
        alembic current
        ;;
    
    *)
        show_usage
        exit 1
        ;;
esac