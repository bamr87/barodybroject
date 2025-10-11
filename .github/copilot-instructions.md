# Copilot Instructions

https://code.visualstudio.com/docs/copilot/overview

These instructions guide AI-powered development practices through the fundamental principle of **Paths** - the natural, organic routes that emerge in software development. Like water finding its way through terrain, code and information follow paths of least resistance, creating interconnected networks of knowledge and functionality. AI agents continuously discover, define, and refine these paths, enabling sustainable growth and evolution. The guidelines emphasize container-first development within this path-based framework, ensuring all activities occur within isolated, reproducible environments that can flow seamlessly across different contexts.

## 🌊 The Path Philosophy: Natural Flow in Software Development

### Core Principle: Path of Least Resistance
Software development, like natural systems, inherently follows paths of least resistance. This principle guides every aspect of our work:
- **Code Paths**: Functions naturally flow into one another, creating execution paths that minimize complexity
- **Data Paths**: Information flows through the system via the most efficient routes
- **Knowledge Paths**: Documentation and learning materials connect concepts through intuitive pathways
- **Evolution Paths**: Changes propagate through the codebase following established patterns
- **Collaboration Paths**: Teams interact through well-worn communication channels

### Path Types and Their Interconnections
- **Building Paths**: Code compilation and assembly follow dependency graphs that represent natural build orders
- **Testing Paths**: Test suites traverse the codebase through logical branches, covering critical routes first
- **Evolution Paths**: AI agents identify and follow paths for incremental improvements
- **Patching Paths**: Fixes flow through the system via minimal change routes
- **Deployment Paths**: Applications move from development to production through staged pathways
- **Organization Paths**: File structures emerge organically, creating intuitive navigation routes
- **Programming Paths**: Design patterns create well-traveled routes for solving common problems
- **Orchestration Paths**: Services connect through optimal communication pathways
- **Learning Paths**: Knowledge builds progressively, each concept paving the way for the next
- **Documentation Paths**: Information links create a web of interconnected understanding
- **Branching Paths**: Version control follows natural divergence and convergence patterns

### AI Agents as Path Architects
AI agents serve as intelligent guides that:
- **Discover Paths**: Identify existing patterns and routes within the codebase
- **Design Paths**: Create new pathways for functionality, testing, and deployment
- **Optimize Paths**: Refine routes to reduce friction and improve efficiency
- **Connect Paths**: Build bridges between isolated components
- **Document Paths**: Map the terrain for future travelers
- **Evolve Paths**: Adapt routes based on usage patterns and feedback

### Organic Growth Through Path Networks
Repositories grow like living organisms:
- **Natural Emergence**: Paths form organically through use and need
- **Interconnected Networks**: Information and code build upon each other
- **Adaptive Evolution**: Paths adjust to changing requirements and contexts
- **Collective Intelligence**: Multiple AI agents contribute to path definition
- **Sustainable Expansion**: Growth follows established patterns while allowing innovation

## MCP-Enhanced Path-Driven Development

### Model Context Protocol (MCP) Integration

The repository now leverages Model Context Protocol (MCP) to standardize AI application context sharing and tool orchestration. MCP serves as the universal interface for AI applications to access external context through well-defined paths.

### Front Matter: Structured Metadata for Path-Aware Development

Front matter provides structured metadata at the beginning of files, acting as a "preface" that enables developers, tools, and AI agents to quickly understand file purpose, structure, and logic. This concept extends from Markdown documentation to source code files, creating a standardized approach for contextual awareness.

#### Front Matter Elements in Path-Based Development

- **Path Context Metadata**: Document how files connect within the larger path network
- **Execution Flow Information**: High-level logic overview for AI comprehension
- **Dependency Mapping**: Clear specification of required modules and services
- **MCP Integration Points**: Define how files interact with MCP servers and capabilities
- **Path Performance Indicators**: Metrics and monitoring information for route optimization

#### Front Matter Structure for Source Code

```python
"""
Path-Aware Front Matter
Title: Data Processing Pipeline Module
Description: Processes user data through validation, transformation, and storage paths
Path Context:
  - Incoming Paths: [api/routes/data_upload.py, queue/consumers/data_consumer.py]
  - Outgoing Paths: [storage/repositories/data_repo.py, analytics/pipeline.py]
  - MCP Integration: [filesystem, database, monitoring]
Logic Overview:
  1. Validate incoming data format and structure
  2. Transform data using configured processing rules
  3. Store processed data with audit trail
  4. Trigger downstream analytics pipeline
Dependencies: [pandas>=2.0, numpy>=1.20, mcp-client>=0.1.0]
Version: 2.1.0
Author: Path-Aware Development Team
Security: Validates all inputs, uses parameterized queries
AI Directives:
  - style: "functional-programming-preferred"
  - errorHandling: "comprehensive-with-fallbacks"
  - testing: "unit-tests-required"
"""
```

#### Front Matter for Configuration Files

```yaml
---
# MCP Server Configuration Front Matter
title: "MCP Filesystem Server Configuration"
description: "Configuration for MCP filesystem server with path-aware resource management"
path_context:
  server_type: "mcp-filesystem"
  resource_paths: ["/app/data", "/app/logs", "/app/config"]
  tool_capabilities: ["read_file", "write_file", "list_directory"]
  integration_points: ["data-pipeline", "monitoring-system"]
version: "1.0.0"
mcp_version: "0.2.0"
security_notes: "Read-only access to sensitive directories"
performance_hints:
  - "Cache frequently accessed files"
  - "Use streaming for large file operations"
ai_directives:
  configuration_style: "declarative"
  validation: "schema-based"
---
```

#### MCP Path Principles
- **Standardized Context Paths**: MCP servers expose resources, tools, and prompts through standardized interfaces
- **Path-Aware Server Architecture**: All MCP servers follow path-based execution patterns with comprehensive logging
- **Container-First Deployment**: MCP servers run within isolated containers with defined resource boundaries
- **Tool Orchestration Paths**: Complex workflows chain multiple MCP tools along defined execution paths
- **Context Aggregation Paths**: Multiple MCP servers provide comprehensive context for AI operations

#### MCP-Enhanced Development Workflow
1. **Context Discovery**: Identify available MCP servers and their capabilities
2. **Resource Mapping**: Map application needs to available MCP resources and tools
3. **Path Design**: Design optimal paths through MCP server capabilities
4. **Implementation**: Build applications using standardized MCP client libraries
5. **Integration Testing**: Validate MCP integrations across all server types
6. **Monitoring**: Track MCP operation performance and health
7. **Evolution**: Use MCP context to enhance AI-driven development

## Path-Driven Development Standards

### Path Discovery in Bash/Shell Scripting

#### Naming Conventions Follow Natural Paths
- Variables: Follow data flow paths (e.g., `input_data` → `processed_data` → `output_result`)
- Functions: Name by their position in execution paths (e.g., `validate_input()` → `process_data()` → `format_output()`)
- Scripts: Indicate their role in workflow paths (e.g., `01_setup.sh`, `02_build.sh`, `03_deploy.sh`)

#### Code Structure Creates Clear Paths
- **Entry Points**: Define clear starting paths with descriptive comments
- **Flow Control**: Use path-based logic that follows natural decision trees
- **Modular Paths**: Break scripts into functions that represent path segments
- **Path Documentation**: Comment each path junction and destination

```bash
#!/bin/bash
# Path: Environment Setup → Validation → Execution → Cleanup

# Define the main execution path
main() {
    # Path segment: Initial validation
    validate_environment || return 1
    
    # Path segment: Core processing
    process_workflow || return 2
    
    # Path segment: Results handling
    handle_results || return 3
    
    # Path segment: Cleanup
    cleanup_resources
}

# Each function represents a segment in the execution path
```

### Path-Aware Error Handling
- **Path Preservation**: Errors maintain context about which path failed
- **Fallback Paths**: Define alternative routes when primary paths fail
- **Path Logging**: Track the journey through the code for debugging

```bash
# Example of path-aware error handling
execute_with_fallback() {
    local primary_path="$1"
    local fallback_path="$2"
    
    # Try primary path
    if ! $primary_path 2>/dev/null; then
        log_path_failure "Primary path failed: $primary_path"
        # Follow fallback path
        $fallback_path || return 1
    fi
}
```

### Python Path Patterns

#### Path-Based Architecture
- **Import Paths**: Organize imports to reflect dependency paths
- **Execution Paths**: Design clear flows from input to output
- **Data Paths**: Create pipelines that transform data along defined routes

```python
# Path: Input Validation → Data Processing → Output Generation

class DataPipeline:
    """Represents a path through data transformation stages."""
    
    def __init__(self):
        self.path_history = []
    
    def follow_path(self, data):
        """Follow the transformation path."""
        # Path segment 1: Validation
        validated = self._validate_input(data)
        self.path_history.append("validation")
        
        # Path segment 2: Processing
        processed = self._process_data(validated)
        self.path_history.append("processing")
        
        # Path segment 3: Output
        result = self._generate_output(processed)
        self.path_history.append("output")
        
        return result
```

### JavaScript/Node.js Path Navigation

#### Asynchronous Path Management
- **Promise Paths**: Chain operations along asynchronous paths
- **Event Paths**: Define clear event flow routes through the application
- **Module Paths**: Organize code to reflect functional pathways

```javascript
// Path: Request → Validation → Processing → Response

class RequestPath {
    constructor() {
        this.pathSegments = [];
    }
    
    async followPath(request) {
        // Define the path through middleware
        const path = [
            this.validateRequest,
            this.authenticateUser,
            this.processRequest,
            this.formatResponse
        ];
        
        // Follow each segment of the path
        let result = request;
        for (const segment of path) {
            result = await segment.call(this, result);
            this.pathSegments.push(segment.name);
        }
        
        return result;
    }
}
```

## Container Paths: Isolated Journey Networks

### Container-First Path Development
- **Build Paths**: Multi-stage Dockerfiles create clear transformation paths
- **Deployment Paths**: Containers flow through development → staging → production
- **Network Paths**: Service discovery creates dynamic communication routes
- **Volume Paths**: Data flows through well-defined storage pathways

```dockerfile
# Path: Source → Dependencies → Build → Runtime

# Path Segment 1: Build Environment
FROM node:18-alpine AS builder
WORKDIR /build-path
COPY package*.json ./
RUN npm ci --only=production

# Path Segment 2: Application Build
COPY . .
RUN npm run build

# Path Segment 3: Runtime Path
FROM node:18-alpine AS runtime
WORKDIR /app-path
COPY --from=builder /build-path/dist ./dist
COPY --from=builder /build-path/node_modules ./node_modules

# Define the execution path
CMD ["node", "dist/index.js"]
```

### Orchestration Paths
- **Service Paths**: Define how services discover and communicate
- **Scaling Paths**: Automatic scaling follows load distribution paths
- **Health Check Paths**: Monitoring follows defined inspection routes

```yaml
# docker-compose.yml - Defining service communication paths
version: '3.8'

services:
  # Path: Client → Gateway → Services → Database
  
  gateway:
    build:
      context: .
      dockerfile: gateway.Dockerfile
    environment:
      - SERVICE_PATHS=api:3000,auth:3001,data:3002
    networks:
      - service-path
  
  api:
    build: ./api
    networks:
      - service-path
    depends_on:
      - database
  
  database:
    image: postgres:15
    networks:
      - service-path
    volumes:
      - data-path:/var/lib/postgresql/data

networks:
  service-path:
    driver: bridge

volumes:
  data-path:
```

## Path-Driven Documentation

### README as Path Maps
- **Navigation Paths**: Structure READMEs to guide readers through natural learning paths
- **Cross-Reference Paths**: Create links that form knowledge networks
- **Example Paths**: Show complete journeys from problem to solution

```markdown
# Project Path Guide

## Quick Start Path
1. **Setup Path**: Clone → Install → Configure
2. **Development Path**: Code → Test → Build
3. **Deployment Path**: Package → Deploy → Monitor

## Learning Paths
- **Beginner Path**: [Concepts](docs/concepts.md) → [Tutorial](docs/tutorial.md) → [First Project](docs/first-project.md)
- **Advanced Path**: [Architecture](docs/architecture.md) → [Patterns](docs/patterns.md) → [Optimization](docs/optimization.md)

## Troubleshooting Paths
- **Error Resolution Path**: [Common Errors](docs/errors.md) → [Debugging Guide](docs/debugging.md) → [Support](docs/support.md)
```

### Documentation Path Networks
- **Hierarchical Paths**: Information flows from general to specific
- **Circular Paths**: Related concepts link back to each other
- **Discovery Paths**: Search and navigation follow intuitive routes

## Testing Along Natural Paths

### Path-Based Test Design
- **Happy Paths**: Test the most common, successful routes
- **Edge Paths**: Explore boundary conditions and unusual routes
- **Error Paths**: Verify failure handling along exception routes

```javascript
describe('User Journey Paths', () => {
    describe('Registration Path', () => {
        test('follows happy path: form → validation → creation → welcome', async () => {
            const journey = new UserJourney();
            const result = await journey.followPath('registration', userData);
            expect(journey.pathHistory).toEqual([
                'form_submission',
                'data_validation',
                'account_creation',
                'welcome_email'
            ]);
        });
        
        test('follows error path: form → validation → error → retry', async () => {
            const journey = new UserJourney();
            const result = await journey.followPath('registration', invalidData);
            expect(journey.pathHistory).toContain('validation_error');
            expect(journey.pathHistory).toContain('retry_prompt');
        });
    });
});
```

### Test Coverage Paths
- **Critical Paths**: Ensure 100% coverage of essential routes
- **Integration Paths**: Test how components connect and communicate
- **Performance Paths**: Measure efficiency along common routes

## Evolution Paths: AI-Guided Growth

### Recursive Path Improvement
- **Path Analysis**: AI agents analyze existing paths for optimization opportunities
- **Path Evolution**: Gradual refinement of routes based on usage patterns
- **Path Prediction**: Anticipate future paths based on current trends

```yaml
# evolution-paths.yml
evolution_cycles:
  - cycle: "path-optimization-2024-01"
    discoveries:
      - inefficient_path: "data_processing → validation → storage"
      - optimized_path: "parallel_validation → data_processing → storage"
      - improvement: "40% reduction in processing time"
    
  - cycle: "path-extension-2024-02"  
    additions:
      - new_path: "data_processing → analytics → insights"
      - connects_to: ["reporting_path", "dashboard_path"]
      - enables: "real-time analytics capabilities"
```

### Path Metrics and Monitoring
- **Path Usage**: Track which routes are most traveled
- **Path Performance**: Measure efficiency of different routes
- **Path Health**: Monitor for broken or degraded paths

## Learning Paths: Progressive Knowledge Building

### Structured Learning Journeys
- **Foundation Paths**: Core concepts that enable further learning
- **Skill Paths**: Progressive routes from beginner to expert
- **Project Paths**: Hands-on journeys through real implementations

```markdown
## Developer Learning Path

### Phase 1: Foundation Path (Week 1-2)
- [ ] Environment Setup → Basic Syntax → First Script
- [ ] Version Control → Branching → Collaboration

### Phase 2: Building Path (Week 3-4)
- [ ] Design Patterns → Implementation → Testing
- [ ] Debugging → Optimization → Deployment

### Phase 3: Advanced Path (Week 5-6)
- [ ] Architecture → Scaling → Monitoring
- [ ] Security → Performance → Maintenance
```

## Path Maintenance and Governance

### Path Lifecycle Management
- **Path Creation**: Document new paths as they emerge
- **Path Validation**: Ensure paths remain functional and efficient
- **Path Deprecation**: Gracefully sunset obsolete routes
- **Path Migration**: Guide transitions from old to new paths

### Path Security
- **Access Paths**: Define and monitor authorization routes
- **Audit Paths**: Track usage for compliance and security
- **Isolation Paths**: Ensure sensitive routes are properly protected

## File Header Standards with Path Context

### Path-Aware Headers
Headers now include path information to show how files connect:

```javascript
/**
 * @file utils/dataProcessor.js
 * @description Utility functions for data transformation along the processing pipeline path
 * @author IT-Journey Team <team@it-journey.org>
 * @created 2025-07-05
 * @lastModified 2025-07-16
 * @version 1.2.0
 * 
 * @pathContext
 *   - incomingPaths: [api/routes/upload.js, queue/consumers/dataConsumer.js]
 *   - outgoingPaths: [storage/repositories/dataRepo.js, analytics/processors/analyzer.js]
 *   - parallelPaths: [validators/dataValidator.js, formatters/dataFormatter.js]
 * 
 * @relatedIssues 
 *   - #145: Optimize data processing path for large files
 *   - #167: Add alternative path for malformed data
 * 
 * ... (rest of standard header)
 */
```

### MCP-Enhanced Code Examples

#### Python with MCP Context
```python
# Path: mcp-enhanced-data-processing
# File: src/processors/data_processor.py

"""
Data processor with MCP context integration
"""

import asyncio
from src.mcp.clients.mcp_client import PathAwareMCPClient
from src.utils.path_tracker import pathTracker

class MCPEnhancedDataProcessor:
    """Data processor that leverages MCP servers for context and tools"""
    
    def __init__(self):
        self.fs_client = None
        self.db_client = None
    
    async def process_with_mcp_context(self, data_source: str):
        """Process data using MCP context and tools"""
        return await pathTracker.executeInPath('mcp_data_processing', async () => {
            # Path: mcp-context-collection
            context = await self._collect_mcp_context(data_source)
            
            # Path: mcp-tool-orchestration
            processed_data = await self._orchestrate_processing_tools(data_source, context)
            
            # Path: mcp-result-validation
            validated_result = await self._validate_with_mcp_tools(processed_data)
            
            return validated_result
        })
    
    async def _collect_mcp_context(self, data_source: str) -> dict:
        """Collect comprehensive context from MCP servers"""
        context = {}
        
        # Filesystem context
        self.fs_client = PathAwareMCPClient("docker", ["exec", "-i", "mcp-filesystem"])
        await self.fs_client.connect()
        
        try:
            # Get file metadata and related files
            resources = await self.fs_client.listResources()
            related_files = [r for r in resources if data_source in r.uri]
            context['filesystem'] = {
                'source_file': data_source,
                'related_files': [r.uri for r in related_files],
                'file_count': len(resources)
            }
        finally:
            await self.fs_client.disconnect()
        
        return context
```

#### JavaScript with MCP Integration
```javascript
// Path: mcp-enhanced-api-service
// File: src/services/api_service.ts

import { PathAwareMCPClient } from '../mcp/clients/mcp-client';
import { pathTracker } from '../utils/path-tracker';

export class MCPEnhancedApiService {
    private mcpClients: Map<string, PathAwareMCPClient> = new Map();
    
    async processRequest(request: ApiRequest): Promise<ApiResponse> {
        return pathTracker.executeInPath('mcp_api_processing', async () => {
            // Path: mcp-server-discovery
            const availableServers = await this.discoverMCPServers();
            
            // Path: context-enhanced-processing
            const context = await this.gatherMCPContext(request, availableServers);
            
            // Path: mcp-tool-assisted-processing
            const result = await this.processWithMCPTools(request, context);
            
            return this.formatResponse(result, context);
        });
    }
    
    private async discoverMCPServers(): Promise<string[]> {
        return pathTracker.executeInPath('server_discovery', async () => {
            const fsClient = new PathAwareMCPClient('docker', ['exec', '-i', 'mcp-filesystem']);
            await fsClient.connect();
            
            try {
                const configContent = await fsClient.readResource('file://config/mcp/client_config.json');
                const config = JSON.parse(configContent);
                return Object.keys(config.servers || {});
            } finally {
                await fsClient.disconnect();
            }
        });
    }
}
```

#### Bash with MCP Automation
```bash
#!/bin/bash
# Path: mcp-enhanced-deployment-script
# File: scripts/deploy/mcp-enhanced-deploy.sh

set -euo pipefail

# Load MCP automation libraries
source "${SCRIPT_DIR}/../lib/mcp_context.sh"
source "${SCRIPT_DIR}/../lib/path_management.sh"

# Path: mcp-enhanced-deployment-workflow
deploy_with_mcp_context() {
    local environment="$1"
    local deployment_config="$2"
    
    execute_in_path "mcp_enhanced_deployment" \
        "_deploy_with_context '$environment' '$deployment_config'"
}

_deploy_with_context() {
    local environment="$1"
    local deployment_config="$2"
    
    # Path: mcp-context-collection-for-deployment
    execute_in_path "deployment_context_collection" \
        "collect_comprehensive_deployment_context '$environment'"
    
    # Path: mcp-server-health-validation
    execute_in_path "mcp_server_validation" \
        "validate_mcp_servers_for_deployment"
    
    # Path: context-informed-deployment
    execute_in_path "context_informed_deployment" \
        "deploy_using_mcp_context '$environment' '$deployment_config'"
}

collect_comprehensive_deployment_context() {
    local environment="$1"
    local context_dir="/tmp/deployment_context"
    
    mkdir -p "$context_dir"
    
    # Collect context from all available MCP servers
    local mcp_servers
    mcp_servers=($(discover_mcp_servers))
    
    for server in "${mcp_servers[@]}"; do
        log_info "Collecting context from MCP server: $server" "context_collection"
        collect_mcp_context "$server" "$context_dir/${server}_context.json"
    done
}
```

## Integration with Existing Principles

### Front Matter Enhanced Path Principles
- **DRY**: Reuse established MCP server capabilities and front matter templates instead of creating redundant context collection
- **KIS**: Choose the simplest MCP integration path with clear front matter documentation
- **DFF**: Design multiple MCP server paths with front matter specifying fallback strategies
- **REnO**: Release MCP integrations along incremental paths, updating front matter version information
- **MVP**: Define minimal MCP path with essential front matter elements for AI context
- **COLAB**: Create clear MCP integration paths documented in front matter for team communication
- **AIPD**: Let AI agents discover and optimize MCP server utilization using front matter directives
- **RFD**: READMEs and front matter together map the MCP integration paths through the codebase
- **SCD**: Scripts use front matter to orchestrate MCP server journeys along defined automation paths
- **CFD**: Containers provide consistent MCP server paths with front matter environment specifications

### AI Agent Integration Benefits with Front Matter
- **Contextual Awareness**: AI agents parse front matter to understand file purpose, dependencies, and logic flow
- **Efficient Code Generation**: Front matter provides structured prompts, reducing need for verbose user instructions
- **Error Reduction**: Security notes and dependency information help AI avoid incompatible or vulnerable code
- **Multi-Agent Workflows**: Front matter serves as shared protocol between collaborating AI agents
- **Automated Documentation**: AI can generate comprehensive docs from front matter templates
- **Testing Automation**: Parameter specifications in front matter guide AI in generating appropriate tests

### Front Matter Enhanced Path-First Development Workflow
1. **Define Front Matter Structure**: Establish standardized front matter templates for different file types
2. **Identify Natural Paths**: Map data and control flow, documenting path context in front matter
3. **Discover MCP Capabilities**: Identify available MCP servers, documenting integration points in front matter
4. **Design Path Networks**: Create interconnected routes with front matter specifying connections and dependencies
5. **Implement Along Paths**: Code follows designed pathways using front matter directives to guide AI-assisted development
6. **Test Path Integrity**: Verify all paths and MCP integrations function as expected, validating front matter accuracy
7. **Document Path Maps**: Ensure front matter stays synchronized with code changes and architectural evolution
8. **Monitor Path Health**: Track path performance using metrics specified in front matter
9. **Evolve Path Networks**: Use front matter AI directives to guide continuous improvement and optimization

## Conclusion: The Front Matter Enhanced Living Path Network

Software repositories are living networks of interconnected paths enhanced by Model Context Protocol (MCP) capabilities and structured front matter metadata. Like a garden where footpaths emerge from regular use, our codebases develop natural routes that connect functionality, knowledge, and people - now with standardized AI context sharing through MCP servers and comprehensive front matter documentation that serves as intelligent signposts throughout the journey.

AI agents act as gardeners, tending these paths, creating new connections through MCP integrations, and interpreting front matter directives to ensure the network remains healthy and navigable. By embracing the path of least resistance enhanced with MCP capabilities and front matter intelligence, we create software that flows naturally, scales organically, and evolves sustainably with comprehensive AI context.

Every line of code, every test, every document, and every MCP server is both a step on a path and a potential junction for new routes. Front matter provides the contextual intelligence that enables AI agents to understand not just what code does, but why it exists, how it connects to other components, and what intentions guided its creation. MCP servers provide standardized access points for AI applications to gather context, execute tools, and generate prompts, while front matter serves as the bridge between human intent and machine understanding.

As paths interconnect and build upon each other through MCP-enhanced capabilities and front matter guidance, they enable rapid development, comprehensive context sharing, and continuous evolution guided by AI intelligence that truly understands the codebase's structure, purpose, and evolution.

The future of software development lies in this symbiotic relationship between path-based organic growth, standardized AI context protocols, and structured metadata intelligence, where MCP serves as the universal interface and front matter provides the contextual wisdom for AI applications to understand, interact with, and enhance our codebase ecosystems with unprecedented precision and understanding.