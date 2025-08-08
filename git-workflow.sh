#!/bin/bash

# Git Workflow Script for Fishing Weather Portal
# Manages repository updates and deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "Not in a git repository. Please run this script from the fishing-weather directory."
    exit 1
fi

# Function to show usage
show_usage() {
    echo "🎣 Fishing Weather Portal - Git Workflow"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status     - Show current git status and deployment status"
    echo "  commit     - Stage all changes and commit with message"
    echo "  push       - Push changes to remote repository"
    echo "  pull       - Pull latest changes from remote"
    echo "  deploy     - Deploy current changes to production"
    echo "  update     - Pull changes and deploy to production"
    echo "  backup     - Create backup before making changes"
    echo "  clean      - Clean up repository (remove Mac references)"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status                    # Check current status"
    echo "  $0 commit 'Update weather analysis'  # Commit changes"
    echo "  $0 deploy                    # Deploy to production"
    echo "  $0 update                    # Pull and deploy"
}

# Function to show status
show_status() {
    print_status "Checking repository status..."
    
    echo ""
    echo "📊 Git Status:"
    echo "=============="
    git status --short
    
    echo ""
    echo "📈 Recent Commits:"
    echo "=================="
    git log --oneline -5
    
    echo ""
    echo "🌐 Remote Status:"
    echo "================"
    git remote -v
    
    echo ""
    echo "🔧 Service Status:"
    echo "================="
    sudo systemctl status fishing-weather --no-pager -l | head -5
    
    echo ""
    echo "🌐 Production Status:"
    echo "===================="
    if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
        print_success "Production portal is responding"
    else
        print_error "Production portal is not responding"
    fi
}

# Function to commit changes
commit_changes() {
    local message="$1"
    
    if [ -z "$message" ]; then
        print_error "Commit message is required"
        echo "Usage: $0 commit 'Your commit message'"
        exit 1
    fi
    
    print_status "Staging all changes..."
    git add .
    
    print_status "Committing changes with message: '$message'"
    git commit -m "$message"
    
    print_success "Changes committed successfully"
}

# Function to push changes
push_changes() {
    print_status "Pushing changes to remote repository..."
    
    if git push origin main; then
        print_success "Changes pushed successfully"
    else
        print_error "Failed to push changes"
        exit 1
    fi
}

# Function to pull changes
pull_changes() {
    print_status "Pulling latest changes from remote repository..."
    
    if git pull origin main; then
        print_success "Changes pulled successfully"
    else
        print_error "Failed to pull changes"
        exit 1
    fi
}

# Function to deploy to production
deploy_production() {
    print_status "Deploying to production..."
    
    if [ -f "./deploy-production.sh" ]; then
        ./deploy-production.sh
        print_success "Production deployment completed"
    else
        print_error "deploy-production.sh not found"
        exit 1
    fi
}

# Function to update (pull and deploy)
update_production() {
    print_status "Updating production (pull + deploy)..."
    
    pull_changes
    deploy_production
}

# Function to create backup
create_backup() {
    print_status "Creating backup..."
    
    if [ -f "./backup-database.sh" ]; then
        ./backup-database.sh
        print_success "Backup created successfully"
    else
        print_error "backup-database.sh not found"
        exit 1
    fi
}

# Function to clean repository
clean_repository() {
    print_status "Cleaning repository..."
    
    if [ -f "./cleanup-repository.sh" ]; then
        ./cleanup-repository.sh
        print_success "Repository cleaned successfully"
    else
        print_error "cleanup-repository.sh not found"
        exit 1
    fi
}

# Main script logic
case "${1:-help}" in
    "status")
        show_status
        ;;
    "commit")
        commit_changes "$2"
        ;;
    "push")
        push_changes
        ;;
    "pull")
        pull_changes
        ;;
    "deploy")
        deploy_production
        ;;
    "update")
        update_production
        ;;
    "backup")
        create_backup
        ;;
    "clean")
        clean_repository
        ;;
    "help"|*)
        show_usage
        ;;
esac
