#!/bin/bash
# README.sh - The Forbidden Librarian's Tool
# Version: 1.0.0
# Description: Compiles, analyzes, and enhances all README.md files in the repository
# Author: Barodybroject Development Team
# Last Modified: 2025-10-30

set -euo pipefail

# ============================================================================
# COLORS AND FORMATTING
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Mystical symbols
STAR="⭐"
BOOK="📚"
SPARKLES="✨"
WARNING="⚠️"
CHECK="✅"
CROSS="❌"
MAGNIFY="🔍"
BRAIN="🧠"
SHIELD="🛡️"
WAND="🪄"

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
README_LIBRARY="${PROJECT_ROOT}/README"
LOG_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/readme-architect-${TIMESTAMP}.log"

# Create necessary directories
mkdir -p "${README_LIBRARY}"
mkdir -p "${LOG_DIR}"

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] ${message}" | tee -a "${LOG_FILE}" >&2
}

log_info() {
    echo -e "${BLUE}${STAR} $*${RESET}" | tee -a "${LOG_FILE}" >&2
}

log_success() {
    echo -e "${GREEN}${CHECK} $*${RESET}" | tee -a "${LOG_FILE}" >&2
}

log_warning() {
    echo -e "${YELLOW}${WARNING} $*${RESET}" | tee -a "${LOG_FILE}" >&2
}

log_error() {
    echo -e "${RED}${CROSS} $*${RESET}" | tee -a "${LOG_FILE}" >&2
}

log_mystical() {
    echo -e "${MAGENTA}${SPARKLES} $*${RESET}" | tee -a "${LOG_FILE}" >&2
}

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ${BOOK} THE README ARCHITECT AGENT ${BOOK}"
    echo "  Forbidden Librarian of Documentation Mastery"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${RESET}"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in find grep sed awk python3; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

scan_readmes() {
    log_mystical "Initiating repository scan..."
    
    local readme_list="${LOG_DIR}/readme-list-${TIMESTAMP}.txt"
    
    # Find all README.md files, excluding .git and node_modules
    find "${PROJECT_ROOT}" \
        -type f \
        -name "README.md" \
        ! -path "*/\.git/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/venv/*" \
        ! -path "*/__pycache__/*" \
        > "${readme_list}"
    
    local count=$(wc -l < "${readme_list}" | tr -d ' ')
    
    log_success "Discovered ${count} README files"
    log "INFO" "README list saved to: ${readme_list}"
    
    echo "${readme_list}"
}

analyze_readme() {
    local readme_path="$1"
    local analysis_file="${2:-}"
    
    # Initialize scores
    local engagement_score=0
    local structure_score=0
    local ai_readability=0
    local completeness=0
    
    # Check file existence
    if [ ! -f "${readme_path}" ]; then
        echo "0,0,0,0"
        return
    fi
    
    # Read content
    local content=$(cat "${readme_path}")
    
    # ---- ENGAGEMENT SCORE (0-100) ----
    # Check for compelling elements
    [ -n "$(echo "$content" | grep -i "don't\|forbidden\|secret\|warning")" ] && ((engagement_score+=20))
    [ -n "$(echo "$content" | grep -E "⚠️|✨|🔮|💡")" ] && ((engagement_score+=15))
    [ -n "$(echo "$content" | grep -i "mystical\|power\|ancient\|hidden")" ] && ((engagement_score+=10))
    
    # Check for visual elements
    [ -n "$(echo "$content" | grep '```')" ] && ((engagement_score+=20))
    [ -n "$(echo "$content" | grep -E '\|.*\|')" ] && ((engagement_score+=15))
    [ -n "$(echo "$content" | grep -E '^\s*[-*+]')" ] && ((engagement_score+=10))
    
    # Check for clear purpose
    [ -n "$(echo "$content" | grep -iE '^#+\s+(purpose|overview|what)')" ] && ((engagement_score+=10))
    
    # ---- STRUCTURE SCORE (0-100) ----
    # Check for markdown headers
    local h1_count=$(echo "$content" | grep -cE '^#\s+' || true)
    local h2_count=$(echo "$content" | grep -cE '^##\s+' || true)
    local h3_count=$(echo "$content" | grep -cE '^###\s+' || true)
    
    [ "$h1_count" -eq 1 ] && ((structure_score+=30)) || ((structure_score+=0))
    [ "$h2_count" -ge 3 ] && ((structure_score+=20)) || ((structure_score+=10))
    [ "$h3_count" -ge 2 ] && ((structure_score+=10)) || ((structure_score+=5))
    
    # Check for essential sections
    [ -n "$(echo "$content" | grep -iE '^#+\s+(installation|setup|getting started)')" ] && ((structure_score+=15))
    [ -n "$(echo "$content" | grep -iE '^#+\s+(usage|examples?)')" ] && ((structure_score+=15))
    [ -n "$(echo "$content" | grep -iE '^#+\s+(features?|capabilities)')" ] && ((structure_score+=10))
    
    # ---- AI READABILITY (0-100) ----
    # Check for structured metadata
    [ -n "$(echo "$content" | grep -E '^---')" ] && ((ai_readability+=25))
    
    # Check for context sections
    [ -n "$(echo "$content" | grep -i 'purpose:\|description:')" ] && ((ai_readability+=20))
    [ -n "$(echo "$content" | grep -i 'dependencies:\|requires:')" ] && ((ai_readability+=15))
    [ -n "$(echo "$content" | grep -i 'ai context\|ai agents')" ] && ((ai_readability+=15))
    
    # Check for clear navigation
    [ -n "$(echo "$content" | grep -E '\[.*\]\(.*\)')" ] && ((ai_readability+=15))
    [ -n "$(echo "$content" | grep -iE '^#+\s+table of contents')" ] && ((ai_readability+=10))
    
    # ---- COMPLETENESS (0-100) ----
    # Check content length
    local line_count=$(echo "$content" | wc -l | tr -d ' ')
    [ "$line_count" -gt 100 ] && ((completeness+=30)) || ((completeness+=15))
    
    # Check for examples
    [ -n "$(echo "$content" | grep -E '```[a-z]*$')" ] && ((completeness+=25))
    
    # Check for links and references
    local link_count=$(echo "$content" | grep -oE '\[.*\]\(.*\)' | wc -l | tr -d ' ')
    [ "$link_count" -gt 5 ] && ((completeness+=20)) || [ "$link_count" -gt 0 ] && ((completeness+=10))
    
    # Check for comprehensive sections
    [ -n "$(echo "$content" | grep -iE 'contributing|license|credits')" ] && ((completeness+=15))
    [ -n "$(echo "$content" | grep -iE 'troubleshooting|faq')" ] && ((completeness+=10))
    
    # Cap scores at 100
    [ $engagement_score -gt 100 ] && engagement_score=100
    [ $structure_score -gt 100 ] && structure_score=100
    [ $ai_readability -gt 100 ] && ai_readability=100
    [ $completeness -gt 100 ] && completeness=100
    
    # Write to analysis file if provided
    if [ -n "${analysis_file}" ]; then
        echo "${readme_path}|${engagement_score}|${structure_score}|${ai_readability}|${completeness}" >> "${analysis_file}"
    fi
    
    echo "${engagement_score},${structure_score},${ai_readability},${completeness}"
}

analyze_all_readmes() {
    local readme_list="$1"
    local analysis_file="${LOG_DIR}/readme-analysis-${TIMESTAMP}.csv"
    
    log_mystical "Analyzing documentation quality..."
    
    # Create CSV header
    echo "Path|Engagement|Structure|AI Readability|Completeness" > "${analysis_file}"
    
    local total_engagement=0
    local total_structure=0
    local total_ai_readability=0
    local total_completeness=0
    local count=0
    
    while IFS= read -r readme_path; do
        count=$((count + 1))
        
        local scores=$(analyze_readme "${readme_path}" "${analysis_file}")
        IFS=',' read -r eng struct ai comp <<< "$scores"
        
        total_engagement=$((total_engagement + eng))
        total_structure=$((total_structure + struct))
        total_ai_readability=$((total_ai_readability + ai))
        total_completeness=$((total_completeness + comp))
        
        log_info "Analyzed: $(basename $(dirname "${readme_path}"))/README.md"
    done < "${readme_list}"
    
    # Calculate averages (protect against division by zero)
    local avg_engagement=0
    local avg_structure=0
    local avg_ai_readability=0
    local avg_completeness=0
    
    if [ $count -gt 0 ]; then
        avg_engagement=$((total_engagement / count))
        avg_structure=$((total_structure / count))
        avg_ai_readability=$((total_ai_readability / count))
        avg_completeness=$((total_completeness / count))
    fi
    
    log_success "Analysis complete: ${count} files"
    echo ""
    echo -e "${CYAN}${BOLD}Quality Metrics:${RESET}"
    echo -e "  ${SPARKLES} Engagement Score:    ${avg_engagement}/100"
    echo -e "  ${SHIELD} Structure Score:     ${avg_structure}/100"
    echo -e "  ${BRAIN} AI Readability:      ${avg_ai_readability}/100"
    echo -e "  ${CHECK} Completeness:        ${avg_completeness}/100"
    echo ""
    
    log "INFO" "Detailed analysis saved to: ${analysis_file}"
    
    echo "${analysis_file}"
}

compile_library() {
    local readme_list="$1"
    
    log_mystical "Compiling the Forbidden Library..."
    
    # Clear existing library
    rm -rf "${README_LIBRARY}"/*
    
    local copied_count=0
    
    while IFS= read -r readme_path; do
        # Get relative path from project root
        local rel_path="${readme_path#${PROJECT_ROOT}/}"
        local dir_path=$(dirname "${rel_path}")
        
        # Create directory structure in library
        local target_dir="${README_LIBRARY}/${dir_path}"
        mkdir -p "${target_dir}"
        
        # Copy README to library
        cp "${readme_path}" "${target_dir}/"
        
        copied_count=$((copied_count + 1))
        log_info "Archived: ${rel_path}"
    done < "${readme_list}"
    
    log_success "Compiled ${copied_count} README files into library"
    log "INFO" "Library location: ${README_LIBRARY}"
}

generate_master_index() {
    local readme_list="$1"
    local analysis_file="$2"
    local master_readme="${README_LIBRARY}/README.md"
    
    log_mystical "Generating Master Index..."
    
    cat > "${master_readme}" << 'EOF'
---
title: "The Forbidden Library - Master Index"
description: "A comprehensive catalog of all documentation in the repository"
author: "README Architect Agent"
version: "1.0.0"
lastmod: "2025-10-30"
---

# 📚 The Forbidden Library
## Master Index of All Documentation

*⚠️ You have discovered the central archive of all knowledge within this repository ⚠️*

This mystical library contains every README.md file, organized by location and purpose. Each document is a gateway to understanding, a map to navigate the codebase, and a guide for both humans and AI agents.

## 🎯 Quick Navigation

- [📖 By Directory](#by-directory)
- [📊 Quality Metrics](#quality-metrics)
- [🔍 Search Tips](#search-tips)
- [🤖 For AI Agents](#for-ai-agents)

---

## 📖 By Directory

EOF

    # Generate directory tree
    log_info "Building directory tree..."
    
    local prev_dir=""
    local indent_level=0
    
    while IFS= read -r readme_path; do
        local rel_path="${readme_path#${PROJECT_ROOT}/}"
        local dir_path=$(dirname "${rel_path}")
        
        # Skip root README
        [ "${dir_path}" = "." ] && continue
        
        # Calculate indent level
        indent_level=$(echo "${dir_path}" | tr -cd '/' | wc -c)
        
        # Create indent
        local indent=""
        for ((i=0; i<indent_level; i++)); do
            indent+="  "
        done
        
        # Add entry to index
        echo "${indent}- **[${dir_path}/](${dir_path}/README.md)**" >> "${master_readme}"
        
        # Add purpose if found
        if [ -f "${readme_path}" ]; then
            local purpose=$(grep -m 1 -iE '^#+\s+(purpose|overview|what)' "${readme_path}" | sed 's/^#*\s*//' || echo "")
            if [ -n "${purpose}" ]; then
                echo "${indent}  - ${purpose}" >> "${master_readme}"
            fi
        fi
        
    done < "${readme_list}"
    
    # Add quality metrics section
    cat >> "${master_readme}" << 'EOF'

---

## 📊 Quality Metrics

### Overall Documentation Health

EOF

    # Calculate and add average scores
    if [ -f "${analysis_file}" ]; then
        local total_engagement=0
        local total_structure=0
        local total_ai_readability=0
        local total_completeness=0
        local count=0
        
        while IFS='|' read -r path eng struct ai comp; do
            [ "${path}" = "Path" ] && continue  # Skip header
            
            total_engagement=$((total_engagement + eng))
            total_structure=$((total_structure + struct))
            total_ai_readability=$((total_ai_readability + ai))
            total_completeness=$((total_completeness + comp))
            count=$((count + 1))
        done < "${analysis_file}"
        
        if [ $count -gt 0 ]; then
            local avg_eng=$((total_engagement / count))
            local avg_struct=$((total_structure / count))
            local avg_ai=$((total_ai_readability / count))
            local avg_comp=$((total_completeness / count))
            
            cat >> "${master_readme}" << EOF
| Metric | Score | Status |
|--------|-------|--------|
| 📝 Engagement | ${avg_eng}/100 | $([ $avg_eng -ge 70 ] && echo "✅ Good" || echo "⚠️ Needs Improvement") |
| 🏛️ Structure | ${avg_struct}/100 | $([ $avg_struct -ge 70 ] && echo "✅ Good" || echo "⚠️ Needs Improvement") |
| 🧠 AI Readability | ${avg_ai}/100 | $([ $avg_ai -ge 70 ] && echo "✅ Good" || echo "⚠️ Needs Improvement") |
| ✅ Completeness | ${avg_comp}/100 | $([ $avg_comp -ge 70 ] && echo "✅ Good" || echo "⚠️ Needs Improvement") |

**Total Documentation Files:** ${count}

EOF
        fi
    fi
    
    # Add search tips section
    cat >> "${master_readme}" << 'EOF'

---

## 🔍 Search Tips

### Finding Documentation

1. **By Topic**: Use the directory tree above to browse by location
2. **By Keyword**: Use your IDE's search (`Cmd+Shift+F` or `Ctrl+Shift+F`)
3. **By Quality**: Check the metrics table to find areas needing improvement

### Common Searches

```bash
# Find all READMEs mentioning Django
grep -r "Django" README/

# Find setup instructions
grep -r "installation\|setup" README/

# Find API documentation
grep -r "API\|endpoint" README/
```

---

## 🤖 For AI Agents

### How to Use This Library

This master index provides:
- **Complete directory structure** for navigation
- **Quality metrics** for prioritizing documentation improvements
- **Direct links** to all README files
- **Context clues** from section headings

### Recommended AI Workflows

1. **Understanding Project Structure**: Start with root README, then navigate by directory
2. **Finding Specific Information**: Use keyword search across all READMEs
3. **Code Generation**: Reference relevant READMEs for context and patterns
4. **Documentation Improvement**: Identify low-scoring READMEs for enhancement

### AI Context

```yaml
repository_structure:
  documentation_style: "Engaging with forbidden knowledge theme"
  target_audience: "Both humans and AI agents"
  quality_standards: "Engagement, Structure, AI Readability, Completeness"
  
best_practices:
  - Use mystical theme for engagement
  - Include AI context sections
  - Maintain consistent structure
  - Add visual elements (code blocks, tables, diagrams)
  - Cross-reference related documentation
```

---

## 🎪 The Meta-Documentation

This README was automatically generated by the **README Architect Agent**, the Forbidden Librarian that catalogs all documentation in the repository. It is updated whenever the compilation script runs.

### Last Updated

- **Date**: 2025-10-30
- **READMEs Cataloged**: [count from analysis]
- **Average Quality Score**: [calculated above]

### Regenerate This Index

```bash
# From project root
./scripts/README.sh compile
```

---

*"In a world of scattered documentation, the Forbidden Library brings order and discovery."*

**The README Architect Agent**  
*Guardian of Documentation, Weaver of Understanding*

EOF

    log_success "Master index generated: ${master_readme}"
}

validate_readmes() {
    local readme_list="$1"
    
    log_mystical "Validating documentation quality..."
    
    local errors=0
    local warnings=0
    
    while IFS= read -r readme_path; do
        local issues_found=false
        
        # Check markdown syntax (basic)
        if grep -qE '^#{7,}' "${readme_path}"; then
            log_warning "Invalid heading depth in: ${readme_path}"
            warnings=$((warnings + 1))
            issues_found=true
        fi
        
        # Check for broken internal links
        local links=$(grep -oE '\[.*\]\([^h)]*\)' "${readme_path}" || true)
        while IFS= read -r link; do
            local target=$(echo "$link" | sed -E 's/\[.*\]\((.*)\)/\1/')
            local base_dir=$(dirname "${readme_path}")
            local full_path="${base_dir}/${target}"
            
            if [ -n "${target}" ] && [ "${target:0:1}" != "#" ] && [ ! -f "${full_path}" ] && [ ! -d "${full_path}" ]; then
                log_warning "Broken link in ${readme_path}: ${target}"
                warnings=$((warnings + 1))
                issues_found=true
            fi
        done <<< "$links"
        
        # Check for required sections
        local content=$(cat "${readme_path}")
        if ! echo "$content" | grep -qiE '^#+\s+(overview|purpose|what)'; then
            log_warning "Missing purpose/overview section: ${readme_path}"
            warnings=$((warnings + 1))
            issues_found=true
        fi
        
        [ "$issues_found" = false ] && log_success "Validated: $(basename $(dirname "${readme_path}"))/README.md"
        
    done < "${readme_list}"
    
    echo ""
    if [ $warnings -eq 0 ] && [ $errors -eq 0 ]; then
        log_success "All READMEs passed validation!"
    else
        log_warning "Found ${warnings} warnings and ${errors} errors"
    fi
    echo ""
}

# ============================================================================
# MAIN WORKFLOW FUNCTIONS
# ============================================================================

run_full_compile() {
    print_banner
    
    log_mystical "Beginning full repository documentation compilation..."
    echo ""
    
    # Step 1: Scan
    local readme_list=$(scan_readmes)
    echo ""
    
    # Step 2: Analyze
    local analysis_file=$(analyze_all_readmes "${readme_list}")
    echo ""
    
    # Step 3: Validate
    validate_readmes "${readme_list}"
    
    # Step 4: Compile
    compile_library "${readme_list}"
    echo ""
    
    # Step 5: Generate Index
    generate_master_index "${readme_list}" "${analysis_file}"
    echo ""
    
    log_success "Compilation complete!"
    log_info "Master library: ${README_LIBRARY}"
    log_info "Full log: ${LOG_FILE}"
    echo ""
    
    echo -e "${MAGENTA}${SPARKLES}${BOLD} The Forbidden Library has been updated ${SPARKLES}${RESET}"
    echo ""
}

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

cmd_scan() {
    print_banner
    log_mystical "Scanning repository for README files..."
    local readme_list=$(scan_readmes)
    cat "${readme_list}"
}

cmd_analyze() {
    print_banner
    local readme_list=$(scan_readmes)
    analyze_all_readmes "${readme_list}"
}

cmd_validate() {
    print_banner
    local readme_list=$(scan_readmes)
    validate_readmes "${readme_list}"
}

cmd_compile() {
    run_full_compile
}

cmd_index() {
    print_banner
    local readme_list=$(scan_readmes)
    local analysis_file=$(analyze_all_readmes "${readme_list}")
    generate_master_index "${readme_list}" "${analysis_file}"
}

# ============================================================================
# USAGE INFORMATION
# ============================================================================

usage() {
    cat << EOF
${CYAN}${BOLD}README.sh - The Forbidden Librarian's Tool${RESET}

${BOLD}USAGE:${RESET}
    ./scripts/README.sh [COMMAND] [OPTIONS]

${BOLD}COMMANDS:${RESET}
    ${GREEN}compile${RESET}     Full compilation: scan, analyze, validate, and build library
    ${GREEN}scan${RESET}        Discover all README.md files in the repository
    ${GREEN}analyze${RESET}     Deep analysis of README content quality
    ${GREEN}validate${RESET}    Check README files for errors and issues
    ${GREEN}index${RESET}       Generate master library index

${BOLD}OPTIONS:${RESET}
    -h, --help      Show this help message
    -v, --version   Show version information

${BOLD}EXAMPLES:${RESET}
    # Full compilation (recommended)
    ./scripts/README.sh compile

    # Just scan for README files
    ./scripts/README.sh scan

    # Analyze documentation quality
    ./scripts/README.sh analyze

    # Validate all READMEs
    ./scripts/README.sh validate

${BOLD}OUTPUT:${RESET}
    - Master library: ${README_LIBRARY}
    - Logs: ${LOG_DIR}
    - Analysis data: ${LOG_DIR}/readme-analysis-*.csv

${CYAN}${SPARKLES} May your documentation always be irresistible ${SPARKLES}${RESET}
EOF
}

# ============================================================================
# MAIN SCRIPT LOGIC
# ============================================================================

main() {
    # Check dependencies first
    check_dependencies
    
    # Parse command
    local command="${1:-}"
    
    case "$command" in
        compile)
            cmd_compile
            ;;
        scan)
            cmd_scan
            ;;
        analyze)
            cmd_analyze
            ;;
        validate)
            cmd_validate
            ;;
        index)
            cmd_index
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        -v|--version|version)
            echo "README.sh version 1.0.0"
            exit 0
            ;;
        "")
            log_error "No command specified"
            echo ""
            usage
            exit 1
            ;;
        *)
            log_error "Unknown command: ${command}"
            echo ""
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
