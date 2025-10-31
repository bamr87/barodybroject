#!/bin/bash

# Barodybroject Universal Setup Initializer v1.0.0
# Comprehensive initialization script for Django/OpenAI parody news generator
# File: init_setup.sh
# Description: Main entry point for repository setup and initialization
# Author: Barodybroject Team
# Created: 2025-10-30
# Version: 1.0.0

set -euo pipefail

# ============================================================================
# COLOR CODES AND STYLING
# ============================================================================
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# ============================================================================
# SCRIPT CONFIGURATION
# ============================================================================
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR"
readonly SCRIPTS_DIR="$PROJECT_ROOT/scripts"
readonly LOG_DIR="$PROJECT_ROOT/logs"
readonly LOG_FILE="$LOG_DIR/setup-$(date +%Y%m%d_%H%M%S).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}${BOLD}========================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}${BOLD}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}${BOLD}========================================${NC}" | tee -a "$LOG_FILE"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

get_version() {
    local cmd=$1
    local version_output=$($cmd --version 2>&1 | head -1)
    echo "$version_output" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local response
    
    if [[ "$default" == "y" ]]; then
        read -p "$(echo -e "${CYAN}$prompt [Y/n]: ${NC}")" response
        response=${response:-y}
    else
        read -p "$(echo -e "${CYAN}$prompt [y/N]: ${NC}")" response
        response=${response:-n}
    fi
    
    [[ "$response" =~ ^[Yy]$ ]]
}

# ============================================================================
# BANNER AND WELCOME
# ============================================================================
print_banner() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🎭 BARODYBROJECT SETUP INITIALIZER 🎭                  ║
║                                                                      ║
║        Django/OpenAI Parody News Generator Setup System             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_welcome() {
    log_info "Welcome to the Barodybroject Setup System!"
    log_info "This script will guide you through the complete setup process."
    echo ""
    log_info "Version: 1.0.0"
    log_info "Date: $(date)"
    log_info "OS: $(detect_os)"
    log_info "Log: $LOG_FILE"
    echo ""
}

# ============================================================================
# DEPENDENCY CHECKING
# ============================================================================
check_dependencies() {
    log_section "Checking Dependencies"
    
    local missing_deps=()
    local optional_deps=()
    
    # Critical dependencies
    if ! command_exists python3; then
        missing_deps+=("python3")
        log_error "Python 3 not found"
    else
        local py_version=$(get_version python3)
        log_success "Python 3.${py_version} installed"
    fi
    
    if ! command_exists pip3 && ! command_exists pip; then
        missing_deps+=("pip")
        log_error "pip not found"
    else
        if command_exists pip3; then
            log_success "pip3 installed"
        else
            log_success "pip installed"
        fi
    fi
    
    if ! command_exists git; then
        missing_deps+=("git")
        log_error "Git not found"
    else
        local git_version=$(get_version git)
        log_success "Git ${git_version} installed"
    fi
    
    # Optional but recommended dependencies
    if ! command_exists docker; then
        optional_deps+=("docker")
        log_warning "Docker not found (recommended for development)"
    else
        local docker_version=$(get_version docker)
        log_success "Docker ${docker_version} installed"
    fi
    
    if ! command_exists docker-compose; then
        optional_deps+=("docker-compose")
        log_warning "Docker Compose not found (recommended for development)"
    else
        log_success "Docker Compose installed"
    fi
    
    if ! command_exists az; then
        optional_deps+=("azure-cli")
        log_warning "Azure CLI not found (required for Azure deployment)"
    else
        log_success "Azure CLI installed"
    fi
    
    if ! command_exists azd; then
        optional_deps+=("azd")
        log_warning "Azure Developer CLI not found (required for Azure deployment)"
    else
        log_success "Azure Developer CLI installed"
    fi
    
    if ! command_exists gh; then
        optional_deps+=("gh")
        log_warning "GitHub CLI not found (optional but helpful)"
    else
        log_success "GitHub CLI installed"
    fi
    
    # Handle missing critical dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo ""
        log_error "Missing critical dependencies: ${missing_deps[*]}"
        log_error "Please install these before continuing."
        echo ""
        print_installation_instructions
        return 1
    fi
    
    # Report optional dependencies
    if [ ${#optional_deps[@]} -gt 0 ]; then
        echo ""
        log_warning "Missing optional dependencies: ${optional_deps[*]}"
        log_info "You can continue, but some features may not be available."
    fi
    
    return 0
}

print_installation_instructions() {
    local os=$(detect_os)
    
    log_section "Installation Instructions"
    
    case $os in
        "macos")
            log_info "For macOS, install using Homebrew:"
            echo "  brew install python3 git docker docker-compose"
            echo "  brew tap azure/azd && brew install azd"
            echo "  brew install gh"
            ;;
        "linux")
            log_info "For Linux (Ubuntu/Debian):"
            echo "  sudo apt-get update"
            echo "  sudo apt-get install python3 python3-pip git docker.io docker-compose"
            echo "  # For Azure CLI and azd, see: https://learn.microsoft.com/cli/"
            ;;
        "windows")
            log_info "For Windows:"
            echo "  # Install Python from: https://www.python.org/downloads/"
            echo "  # Install Git from: https://git-scm.com/download/win"
            echo "  # Install Docker Desktop from: https://www.docker.com/products/docker-desktop"
            echo "  # Install Azure CLI from: https://docs.microsoft.com/cli/azure/install-azure-cli"
            ;;
    esac
}

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================
setup_environment() {
    log_section "Environment Setup"
    
    # Check if .env exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Found existing .env file"
        if prompt_yes_no "Do you want to keep the existing .env file?"; then
            log_success "Using existing .env configuration"
            return 0
        fi
    fi
    
    # Create .env from example
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_success ".env file created"
        
        log_warning "IMPORTANT: You need to configure the following in .env:"
        echo "  - SECRET_KEY (generate a secure random string)"
        echo "  - DB_PASSWORD (set a secure database password)"
        echo "  - OPENAI_API_KEY (get from https://platform.openai.com/)"
        echo ""
        
        if prompt_yes_no "Do you want to edit .env now?"; then
            ${EDITOR:-nano} "$PROJECT_ROOT/.env"
        fi
    else
        log_error ".env.example not found"
        return 1
    fi
    
    return 0
}

# ============================================================================
# SETUP MODE SELECTION
# ============================================================================
select_setup_mode() {
    log_section "Setup Mode Selection"
    
    echo "Please select your setup mode:"
    echo ""
    echo "  1) 🐳 Docker Development Setup (Recommended)"
    echo "     - Uses Docker containers for all services"
    echo "     - Fastest and most consistent setup"
    echo "     - Requires Docker and Docker Compose"
    echo ""
    echo "  2) 💻 Local Development Setup"
    echo "     - Install directly on your machine"
    echo "     - More control over environment"
    echo "     - Requires manual dependency installation"
    echo ""
    echo "  3) ☁️ Azure Deployment Setup"
    echo "     - Deploy to Azure Container Apps"
    echo "     - Requires Azure CLI and azd"
    echo "     - Best for production deployment"
    echo ""
    echo "  4) 🧪 Testing/CI Setup"
    echo "     - Minimal setup for running tests"
    echo "     - Used by CI/CD pipelines"
    echo ""
    
    local choice
    read -p "$(echo -e "${CYAN}Enter your choice (1-4): ${NC}")" choice
    
    case $choice in
        1)
            log_info "Selected: Docker Development Setup"
            return 1
            ;;
        2)
            log_info "Selected: Local Development Setup"
            return 2
            ;;
        3)
            log_info "Selected: Azure Deployment Setup"
            return 3
            ;;
        4)
            log_info "Selected: Testing/CI Setup"
            return 4
            ;;
        *)
            log_error "Invalid choice. Please select 1-4."
            select_setup_mode
            return $?
            ;;
    esac
}

# ============================================================================
# DOCKER SETUP
# ============================================================================
setup_docker() {
    log_section "Docker Development Setup"
    
    # Verify Docker is available
    if ! command_exists docker || ! command_exists docker-compose; then
        log_error "Docker or Docker Compose not found"
        log_error "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        return 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        log_error "Please start Docker Desktop and try again"
        return 1
    fi
    
    log_success "Docker is available and running"
    
    # Ask which environment to start
    echo ""
    echo "Which Docker environment do you want to start?"
    echo "  1) Development (with hot-reload)"
    echo "  2) Production (optimized build)"
    echo "  3) Development + Jekyll (static site)"
    echo ""
    
    local env_choice
    read -p "$(echo -e "${CYAN}Enter your choice (1-3): ${NC}")" env_choice
    
    case $env_choice in
        1)
            log_info "Starting development environment..."
            cd "$PROJECT_ROOT"
            docker-compose -f .devcontainer/docker-compose_dev.yml up -d
            ;;
        2)
            log_info "Starting production environment..."
            cd "$PROJECT_ROOT"
            docker-compose up -d
            ;;
        3)
            log_info "Starting development + Jekyll environment..."
            cd "$PROJECT_ROOT"
            docker-compose -f .devcontainer/docker-compose_dev.yml --profile jekyll up -d
            ;;
        *)
            log_error "Invalid choice"
            return 1
            ;;
    esac
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Run initial setup tasks
    log_info "Running database migrations..."
    if [[ "$env_choice" == "1" || "$env_choice" == "3" ]]; then
        docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate
    else
        docker-compose exec web-prod python manage.py migrate
    fi
    
    log_success "Docker environment is ready!"
    
    # Print access information
    print_docker_access_info "$env_choice"
    
    return 0
}

print_docker_access_info() {
    local env_type=$1
    
    echo ""
    log_section "Access Information"
    
    if [[ "$env_type" == "1" || "$env_type" == "3" ]]; then
        log_success "Django Application: http://localhost:8000"
        log_success "Django Admin: http://localhost:8000/admin"
        log_success "API Root: http://localhost:8000/api"
        
        if [[ "$env_type" == "3" ]]; then
            log_success "Jekyll Site: http://localhost:4002"
        fi
    else
        log_success "Django Application: http://localhost:80"
        log_success "Django Admin: http://localhost:80/admin"
        log_success "API Root: http://localhost:80/api"
    fi
    
    echo ""
    log_info "Useful Docker commands:"
    echo "  docker-compose ps              # Check service status"
    echo "  docker-compose logs -f         # View logs"
    echo "  docker-compose down            # Stop services"
    echo "  docker-compose restart         # Restart services"
}

# ============================================================================
# LOCAL SETUP
# ============================================================================
setup_local() {
    log_section "Local Development Setup"
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment
    log_info "Creating Python virtual environment..."
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    source .venv/bin/activate
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    log_success "Dependencies installed"
    
    # Setup database
    log_info "Setting up database..."
    cd src
    python manage.py migrate
    log_success "Database migrations complete"
    
    # Collect static files
    log_info "Collecting static files..."
    python manage.py collectstatic --noinput
    log_success "Static files collected"
    
    # Create superuser (optional)
    echo ""
    if prompt_yes_no "Do you want to create a superuser now?"; then
        python manage.py createsuperuser
    fi
    
    log_success "Local development setup complete!"
    
    # Print instructions
    echo ""
    log_section "Next Steps"
    log_info "To start the development server:"
    echo "  cd src"
    echo "  python manage.py runserver"
    echo ""
    log_info "Then visit: http://localhost:8000"
    
    return 0
}

# ============================================================================
# AZURE SETUP
# ============================================================================
setup_azure() {
    log_section "Azure Deployment Setup"
    
    # Check Azure CLI
    if ! command_exists az; then
        log_error "Azure CLI not found"
        log_error "Install from: https://learn.microsoft.com/cli/azure/install-azure-cli"
        return 1
    fi
    
    # Check azd
    if ! command_exists azd; then
        log_error "Azure Developer CLI (azd) not found"
        log_error "Install from: https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd"
        return 1
    fi
    
    log_success "Azure CLI and azd are installed"
    
    # Check if logged in
    if ! az account show > /dev/null 2>&1; then
        log_warning "Not logged into Azure"
        log_info "Logging in to Azure..."
        az login
    else
        log_success "Already logged into Azure"
    fi
    
    # Deploy with azd
    echo ""
    log_info "Starting Azure deployment with azd..."
    log_warning "This will create Azure resources and may incur costs"
    
    if prompt_yes_no "Do you want to proceed with deployment?"; then
        cd "$PROJECT_ROOT"
        azd up
        
        if [ $? -eq 0 ]; then
            log_success "Azure deployment complete!"
            
            # Run post-deployment setup
            echo ""
            if prompt_yes_no "Do you want to run post-deployment setup?"; then
                bash "$SCRIPTS_DIR/setup-deployment.sh"
            fi
        else
            log_error "Azure deployment failed"
            return 1
        fi
    else
        log_info "Azure deployment cancelled"
    fi
    
    return 0
}

# ============================================================================
# TESTING SETUP
# ============================================================================
setup_testing() {
    log_section "Testing/CI Setup"
    
    cd "$PROJECT_ROOT"
    
    # Install test dependencies
    log_info "Installing test dependencies..."
    pip install -r requirements-dev.txt
    log_success "Test dependencies installed"
    
    # Run infrastructure tests
    if prompt_yes_no "Do you want to run infrastructure tests?" "y"; then
        bash "$SCRIPTS_DIR/test-infrastructure.sh"
    fi
    
    return 0
}

# ============================================================================
# POST-SETUP TASKS
# ============================================================================
post_setup_tasks() {
    log_section "Post-Setup Tasks"
    
    # Validate setup
    log_info "Validating setup..."
    
    # Check if .env exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_success ".env configuration exists"
    else
        log_warning ".env file not found"
    fi
    
    # Check documentation
    echo ""
    log_info "Available documentation:"
    echo "  📚 README.md - Project overview"
    echo "  📖 docs/ - Comprehensive documentation"
    echo "  🔧 scripts/README.md - Script documentation"
    echo "  🧪 docs/INFRASTRUCTURE_TESTING.md - Testing guide"
    
    # Suggest next steps
    echo ""
    log_section "Recommended Next Steps"
    log_info "1. Review the README.md for detailed information"
    log_info "2. Configure your .env file with API keys and secrets"
    log_info "3. Run tests to verify everything is working"
    log_info "4. Start developing your application"
    
    return 0
}

# ============================================================================
# CLEANUP AND EXIT
# ============================================================================
cleanup_and_exit() {
    local exit_code=${1:-0}
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        log_success "Setup completed successfully! 🎉"
    else
        log_error "Setup encountered errors. Please check the log: $LOG_FILE"
    fi
    
    exit $exit_code
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    print_banner
    print_welcome
    
    # Check dependencies
    if ! check_dependencies; then
        cleanup_and_exit 1
    fi
    
    echo ""
    if ! prompt_yes_no "Continue with setup?" "y"; then
        log_info "Setup cancelled by user"
        exit 0
    fi
    
    # Setup environment
    if ! setup_environment; then
        log_error "Environment setup failed"
        cleanup_and_exit 1
    fi
    
    # Select and execute setup mode
    select_setup_mode
    local mode=$?
    
    case $mode in
        1)
            setup_docker || cleanup_and_exit 1
            ;;
        2)
            setup_local || cleanup_and_exit 1
            ;;
        3)
            setup_azure || cleanup_and_exit 1
            ;;
        4)
            setup_testing || cleanup_and_exit 1
            ;;
        *)
            log_error "Invalid setup mode"
            cleanup_and_exit 1
            ;;
    esac
    
    # Post-setup tasks
    post_setup_tasks
    
    cleanup_and_exit 0
}

# Trap errors
trap 'log_error "Error on line $LINENO"; cleanup_and_exit 1' ERR

# Run main function
main "$@"
