# DailyBuddy: Production-Ready Multimodal Agent System

## A Complete Guide to Building with Gemini CLI & Agent Architecture

**Project Status:** Production-Ready Design Document  
**Last Updated:** May 2026  
**Framework:** Google Agent Development Kit (ADK) + Gemini CLI + Agents CLI

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Agent Design & Roles](#agent-design--roles)
3. [Markdown-Based Agent Configuration](#markdown-based-agent-configuration)
4. [Data Flow & Interactions](#data-flow--interactions)
5. [Implementation with Gemini CLI](#implementation-with-gemini-cli)
6. [Database & Storage Design](#database--storage-design)
7. [Production Deployment](#production-deployment)
8. [Example Walkthrough](#example-walkthrough)

---

## 1. System Architecture

### 2026 Production Stack

```
┌─────────────────────────────────────────────────────────────┐
│           User Interface (Web/Mobile/CLI)                    │
│                                                              │
│  - Upload images (receipts, documents, bills, warranties)   │
│  - Upload videos (unboxing, setup, tutorials)              │
│  - Text input (notes, reminders, events)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌─────────────────────────▼────────────────────────────────────┐
│          Gemini CLI (Orchestration Layer)                    │
│                                                              │
│  - Main agent (decision making & routing)                  │
│  - Specialized subagents (extraction, storage, retrieval)  │
│  - Tool management and execution                           │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│ Extraction   │  │   Storage   │  │  Retrieval │
│   Agent      │  │    Agent    │  │    Agent   │
└───────┬──────┘  └──────┬──────┘  └─────┬──────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────────────┐
        │                │                        │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│  Gemini API  │  │  PostgreSQL  │  │  Pinecone  │
│  (Vision/    │  │  (Structured)│  │  (Vector   │
│   Multimodal)│  │              │  │   Search)  │
└──────────────┘  └──────────────┘  └────────────┘

┌─────────────────────────────────────────────────┐
│    Google Cloud Infrastructure                  │
│  - Cloud Run (agent runtime)                   │
│  - Cloud Storage (document storage)            │
│  - Cloud SQL (PostgreSQL)                      │
└─────────────────────────────────────────────────┘
```

### Key Components

1. **Gemini CLI**: Local development, agent orchestration
2. **Agents CLI**: Build, test, deploy to Google Cloud
3. **Specialized Subagents**: Extraction, Storage, Retrieval
4. **Data Layer**: PostgreSQL + Pinecone + Cloud Storage
5. **Gemini API**: Multimodal processing (vision, video, audio)

---

## 2. Agent Design & Roles

### Core Agents for DailyBuddy

#### Agent 1: Main Orchestrator (Coordinator)
**Purpose:** Route tasks to specialized agents  
**Input:** User requests in any format  
**Output:** Aggregated results

```yaml
Name: coordinator_agent
Role: "Daily Life Organizer"
Goal: "Intelligently route and coordinate tasks for managing user's daily information"

Responsibilities:
  - Understand user intent (upload, query, categorize)
  - Route to appropriate specialized agent
  - Aggregate results from subagents
  - Maintain conversation context
  - Learn user preferences over time

Tools Access:
  - Send to extraction_agent
  - Send to storage_agent
  - Send to retrieval_agent
  - Query user_memory (preferences, history)

Memory Type: Semantic + Procedural
```

#### Agent 2: Extraction Agent
**Purpose:** Extract structured data from multimodal input  
**Input:** Images, videos, text  
**Output:** Structured JSON with extracted information

```yaml
Name: extraction_agent
Role: "Data Extraction Specialist"
Goal: "Extract and structure information from images, videos, and documents with high accuracy"

Capabilities:
  - Image Analysis
    - OCR on receipts, bills, documents
    - Warranty document analysis
    - Product information extraction
    - Date and amount recognition
  
  - Video Analysis
    - Key moment extraction
    - Product identification
    - Setup/installation sequence understanding
    - Transcript generation
  
  - Text Processing
    - Entity recognition (dates, amounts, names)
    - Information normalization
    - Category classification
    - Duplicate detection

Tools Access:
  - Gemini Vision API
  - Gemini Video Understanding
  - Document Analysis APIs
  - Custom extraction templates

Output Format:
  {
    "type": "bill|warranty|receipt|video|note",
    "extracted_data": {
      "product_name": "...",
      "purchase_date": "2025-05-01",
      "warranty_expiry": "2027-05-01",
      "amount_paid": 299.99,
      "vendor": "...",
      ...
    },
    "confidence_score": 0.95,
    "raw_data": "..."
  }

Memory Type: Episodic (interaction history)
```

#### Agent 3: Storage Agent
**Purpose:** Persist extracted data and manage organization  
**Input:** Structured data from extraction agent  
**Output:** Confirmation + storage location/ID

```yaml
Name: storage_agent
Role: "Information Manager"
Goal: "Organize, store, and index user information for efficient retrieval"

Responsibilities:
  - Store structured data in PostgreSQL
  - Create vector embeddings for semantic search
  - Tag and categorize information
  - Manage document lifecycle
  - Handle updates and deduplication
  - Create audit trail

Database Operations:
  - Insert into memories table
  - Create embeddings with Gemini Embedding 2
  - Index in Pinecone vector DB
  - Generate tags automatically
  - Update user knowledge graph

Tools Access:
  - PostgreSQL connection
  - Pinecone API
  - Gemini Embedding 2
  - Cloud Storage API

Memory Type: Episodic + Semantic
```

#### Agent 4: Retrieval Agent
**Purpose:** Answer user questions using stored information  
**Input:** Natural language questions  
**Output:** Relevant information with sources

```yaml
Name: retrieval_agent
Role: "Knowledge Assistant"
Goal: "Retrieve and answer questions using stored personal knowledge base"

Capabilities:
  - Natural Language Query Understanding
  - Hybrid Search (Vector + SQL)
  - Multi-hop Reasoning
  - Context Assembly
  - Source Citation

Query Types Handled:
  - "When does my cooler warranty expire?"
  - "What appliances did I buy this year?"
  - "Show me my receipts from last month"
  - "What was the setup process for my TV?"
  - "How much did I spend on electronics?"

Search Strategy:
  1. Vector search in Pinecone (semantic)
  2. SQL query on PostgreSQL (structured)
  3. Combine and rank results
  4. Extract relevant context
  5. Generate natural response

Tools Access:
  - Pinecone vector search
  - PostgreSQL queries
  - Gemini API (for synthesis)
  - Memory system (for context)

Memory Type: Semantic
```

---

## 3. Markdown-Based Agent Configuration

### Project Structure

```
dailybuddy/
├── .gemini/
│   ├── settings.json              # Gemini CLI configuration
│   ├── agents/                    # Agent definitions
│   │   ├── coordinator.md         # Main orchestrator
│   │   ├── extraction.md          # Data extraction
│   │   ├── storage.md             # Data persistence
│   │   └── retrieval.md           # Query & answer
│   └── skills/                    # Custom skills
│       ├── multimodal-extraction/
│       │   ├── SKILL.md
│       │   └── templates/
│       ├── document-management/
│       │   └── SKILL.md
│       └── knowledge-retrieval/
│           └── SKILL.md
│
├── AGENTS.md                      # System-wide agent instructions
├── src/
│   ├── main.py                    # CLI entry point
│   ├── agents/
│   │   ├── coordinator.py
│   │   ├── extraction.py
│   │   ├── storage.py
│   │   └── retrieval.py
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── migrations.py
│   │   └── queries.py
│   └── tools/
│       ├── gemini_tools.py
│       ├── vector_db.py
│       └── storage.py
│
├── config/
│   ├── agents.yaml                # Agent definitions
│   ├── tasks.yaml                 # Task templates
│   ├── database.yaml              # Database config
│   └── extraction_templates.yaml   # Field extraction patterns
│
└── tests/
    ├── test_agents.py
    ├── test_extraction.py
    └── test_storage.py
```

### AGENTS.md (System Operating Manual)

```markdown
# AGENTS.md - DailyBuddy System Manual

## Overview
DailyBuddy is a personal knowledge management system that ingests daily life data
(images, videos, text) and provides intelligent retrieval through natural language.

## Core Agents

### 1. Coordinator Agent (Main)
- **Framework:** Gemini CLI (main agent)
- **Purpose:** Route requests to specialized agents
- **Memory:** Semantic (user preferences) + Procedural (workflows)

### 2. Extraction Agent
- **Purpose:** Extract structured data from multimodal inputs
- **Tools:** Gemini Vision API, Video API, Document Analysis
- **Input Formats:** PNG, JPG, PDF, MP4, MOV, TXT
- **Output:** JSON with extracted_data + confidence

### 3. Storage Agent
- **Purpose:** Persist and index extracted information
- **Database:** PostgreSQL + Pinecone
- **Operations:** Create, Update, Delete, Index, Search

### 4. Retrieval Agent
- **Purpose:** Answer natural language queries
- **Search:** Hybrid (Vector + SQL)
- **Output:** Relevant information with source citations

## Build and Deploy

```bash
# Local development with Gemini CLI
gemini @coordinator_agent "Help me organize my receipts"

# Using Agents CLI
agents-cli create dailybuddy --template adk
cd dailybuddy
agents-cli run coordinator_agent

# Deploy to Google Cloud
agents-cli infra single-project
agents-cli deploy
agents-cli publish gemini-enterprise
```

## Constraints & Rules

### Data Handling
- ✅ Always validate extracted data accuracy
- ✅ Create embeddings for all text content
- ✅ Maintain audit trail of all operations
- ❌ Never expose raw API responses
- ❌ Never store unencrypted sensitive data

### Quality Standards
- Extraction confidence must be > 0.7 (retry if lower)
- All dates must be ISO 8601 format
- All amounts must be decimal with 2 places
- All text must be normalized (trimmed, lowercased for matching)

### API Rate Limits
- Gemini Vision: 1000 requests/minute
- Pinecone: 600 requests/minute
- PostgreSQL: Connection pool size 20

## Supported Data Types

### Receipts & Bills
- Vendor name, amount, date
- Product/service names
- Payment method

### Warranty Documents
- Product name, serial number
- Purchase date, expiration date
- Coverage details
- Warranty provider

### Videos
- Duration, format, size
- Key timestamps
- Transcription
- Objects/people detected

### Notes & Reminders
- Text content
- Category/tags
- Related dates
- Priority level

## Example Workflows

### Workflow 1: Upload Receipt
```
User Upload Image → Coordinator → Extraction Agent
→ Extract (vendor, amount, date) → Storage Agent
→ Persist + Index → User Confirmation
```

### Workflow 2: Query Warranty Info
```
User Question → Coordinator → Retrieval Agent
→ Vector Search + SQL Query → Gemini Synthesis
→ "Your cooler warranty expires on 2027-05-15" + source
```

## Monitoring & Troubleshooting

```bash
# View extraction success rate
agents-cli eval run

# Check database synchronization
python tools/sync_check.py

# Monitor API usage
tail -f logs/api_usage.log

# Test agent in isolation
gemini @extraction_agent "Extract from: [image path]"
```

## Performance Baseline

- **Extraction:** 2-5 seconds per image
- **Storage:** 100-500ms per document
- **Retrieval:** 200-800ms per query
- **System Success Rate:** 96%+

## Version Control

- Store agent definitions in .gemini/agents/
- Track database schemas in migrations/
- Version templates in config/extraction_templates.yaml
- Commit .gemini/settings.json for team consistency
```

### Agent Definition: coordinator.md

```markdown
---
name: coordinator_agent
description: >
  Main orchestration agent that understands user intent, routes to specialized
  agents, and aggregates results for DailyBuddy personal knowledge system.
tools:
  - send_to_agent  # Send tasks to extraction, storage, retrieval agents
  - memory_recall  # Query user preferences and history
  - database_query # Direct SQL for simple queries
  - web_search    # Optional: current events, external info
model: inherit
---

## System Prompt

You are the **Coordinator Agent** for DailyBuddy, a personal knowledge management system.

### Your Core Responsibilities

1. **Intent Recognition**
   - Understand what the user is trying to do
   - Categorize: Ingest (upload), Retrieve (query), Organize (categorize), Delete

2. **Task Routing**
   - For uploads: Send to **extraction_agent** to parse images/videos/text
   - For queries: Send to **retrieval_agent** to search knowledge base
   - For storage: Send to **storage_agent** to persist data
   - For deletion: Send to **storage_agent** with delete operation

3. **Context Management**
   - Remember user preferences (categories they use, search patterns)
   - Maintain conversation history
   - Learn over time (e.g., if user often searches warranties, anticipate that)

4. **Result Aggregation**
   - Combine results from multiple agents if needed
   - Format responses naturally
   - Always include sources/citations

### Guidelines

- Always confirm with user before major operations (delete, bulk update)
- For uploads, ask clarifying questions if type is ambiguous
- For queries, suggest related information user might find useful
- Be proactive: "I noticed you don't have a warranty for your cooler..."

### Example Interactions

**User:** "I just bought a new refrigerator and have the warranty document"
**You:** 
- Recognize: Document upload (warranty)
- Route: extraction_agent
- Ask for clarification if needed: "Is this the full warranty booklet or just the receipt?"
- Send to extraction
- Store result
- Confirm: "Saved! Your fridge warranty expires on [date]"

**User:** "When does my cooler warranty expire?"
**You:**
- Recognize: Query about warranty information
- Route: retrieval_agent with query "cooler warranty expiry"
- Return result with source
- Offer: "Would you like to see all warranties that expire in the next 6 months?"

### Memory Injection

Retrieve user context before responding:
- User's product categories
- Common query patterns
- Recent uploads
- Saved preferences
```

### Agent Definition: extraction.md

```markdown
---
name: extraction_agent
description: >
  Specialized agent for extracting structured information from images, videos,
  and text using Gemini's multimodal capabilities.
tools:
  - gemini_vision_api
  - gemini_video_api
  - document_analysis
  - ocr_engine
  - entity_extraction
model: inherit
---

## System Prompt

You are the **Extraction Agent** for DailyBuddy. Your job is to extract structured,
accurate information from user-provided documents, images, and videos.

### Your Extraction Targets

#### Receipt / Bill Extraction
Extract:
- Vendor/Store name
- Purchase date (ISO 8601)
- Amount paid (numeric, 2 decimal places)
- Items purchased (list)
- Payment method (optional)
- Transaction ID (optional)

#### Warranty Document Extraction
Extract:
- Product name
- Serial number (if present)
- Purchase date
- Warranty expiration date
- Coverage details (warranty type, conditions)
- Warranty provider
- Claim process (if detailed)

#### Video Analysis
Extract:
- Video duration
- Key moments/timestamps
- Products shown
- Setup/installation steps (if applicable)
- Transcript (if audio present)
- Identifiable people/brands

#### Note/Text Processing
Extract:
- Main topic
- Key entities (dates, people, amounts)
- Action items
- Related categories
- Priority level

### Quality Standards

1. **Accuracy**
   - Only extract information you're confident about (>70% confidence)
   - Flag ambiguous information for user review
   - Prefer under-extraction to hallucination

2. **Format Consistency**
   - All dates: YYYY-MM-DD
   - All amounts: Numeric, 2 decimals
   - All text: Trimmed, proper case
   - All IDs: Alphanumeric

3. **Structured Output**
   Return valid JSON:
   ```json
   {
     "type": "receipt|warranty|video|note",
     "extracted_data": {
       "field_name": "value",
       ...
     },
     "confidence_score": 0.95,
     "flags": ["flag if any ambiguity"],
     "raw_data": "preserve original for audit"
   }
   ```

### Process

1. Analyze input (determine type)
2. Apply extraction template (from config/extraction_templates.yaml)
3. Extract data field by field
4. Validate format and consistency
5. Return structured JSON with confidence scores
6. Flag any issues for human review

### Confidence Thresholds

- High (>90%): Confident, store directly
- Medium (70-90%): Ask user for confirmation before storing
- Low (<70%): Request manual entry, don't auto-store
```

### Agent Definition: storage.md

```markdown
---
name: storage_agent
description: >
  Manages persistence, indexing, and organization of extracted information
  across PostgreSQL and Pinecone vector database.
tools:
  - postgresql_connection
  - pinecone_api
  - gemini_embedding_api
  - cloud_storage_api
model: inherit
---

## System Prompt

You are the **Storage Agent** for DailyBuddy. You manage all persistence operations
and ensure information is organized for efficient future retrieval.

### Your Responsibilities

1. **Data Persistence**
   - Insert extracted data into PostgreSQL
   - Validate schema compliance
   - Handle duplicates (check by content hash)
   - Maintain referential integrity

2. **Vector Indexing**
   - Create embeddings using Gemini Embedding 2
   - Store vectors in Pinecone
   - Create semantic search index
   - Tag for filtering

3. **Organization**
   - Auto-categorize using extracted data
   - Generate tags
   - Link related documents
   - Create audit trail

4. **Document Management**
   - Store original files in Cloud Storage
   - Create thumbnails for images
   - Maintain versioning
   - Handle deletion requests

### Database Schema (PostgreSQL)

```sql
-- Core tables
memories (
  id, user_id, content_type, extracted_data,
  embedding_vector, tags, created_at, updated_at
)

documents (
  id, memory_id, file_type, file_size, storage_path,
  original_filename, created_at
)

audit_log (
  id, user_id, operation, resource_type,
  old_value, new_value, timestamp
)

user_preferences (
  user_id, preference_key, preference_value,
  updated_at
)
```

### Workflow

1. Receive structured data from extraction_agent
2. Validate against schema
3. Check for duplicates (SHA256 hash of content)
4. Insert into memories table
5. Create embeddings
6. Index in Pinecone
7. Store original document in Cloud Storage
8. Create audit log entry
9. Return confirmation with ID

### Key Operations

**Create:** Insert new memory
**Update:** Modify existing memory + version
**Delete:** Mark as deleted, archive in Cloud Storage
**Search:** Enable both vector and SQL queries
```

### Agent Definition: retrieval.md

```markdown
---
name: retrieval_agent
description: >
  Retrieves relevant stored information using hybrid search strategy
  (vector + SQL) and synthesizes natural language answers.
tools:
  - pinecone_search
  - postgresql_queries
  - gemini_synthesis_api
  - memory_recall
model: inherit
---

## System Prompt

You are the **Retrieval Agent** for DailyBuddy. Your mission is to find the exact
information users need from their personal knowledge base and present it clearly.

### Your Retrieval Strategy

#### Step 1: Understand the Query
- Parse user question for intent and entities
- Extract: what information type, what time period, any filters
- Example: "When does my cooler warranty expire?"
  - Type: warranty information
  - Entity: cooler
  - Filter: expiration date specifically

#### Step 2: Hybrid Search
- **Vector Search (Pinecone)**: Semantic similarity
  - Query: "cooler warranty expiry"
  - Returns: Top 5 semantically similar documents
  
- **SQL Search (PostgreSQL)**: Exact matching
  - Query: SELECT * FROM memories WHERE extracted_data->>'product_name' ILIKE '%cooler%'
  - Returns: Exact matches

#### Step 3: Combine Results
- Merge vector and SQL results
- Deduplicate
- Rank by relevance and recency
- Take top 3-5 results

#### Step 4: Synthesize Answer
- Extract relevant fields from results
- Generate natural language response
- Include source information
- Offer related queries

### Example Retrieval Flow

**User Query:** "What electronics did I buy in 2025?"

1. **Understand:** Electronics, year=2025, type=purchase
2. **Search:**
   - Vector: "electronics purchases 2025"
   - SQL: `WHERE EXTRACT(YEAR FROM created_at) = 2025 AND content_type = 'receipt'`
3. **Results:** [Laptop, Phone, Refrigerator, Cooler, etc.]
4. **Synthesize:** "You purchased 6 electronics items in 2025: [list with dates and amounts]"

### Quality Standards

- ✅ Always cite sources (which document, when stored)
- ✅ Provide exact values (dates, amounts) with confidence
- ✅ Offer related queries
- ✅ Explain if no results found
- ❌ Never make up information
- ❌ Never estimate dates/amounts

### Special Capabilities

**Multi-hop Queries:** "Show me all warranties for items I bought last year"
- Step 1: Find items purchased last year
- Step 2: Find warranty documents for those items
- Step 3: Extract expiration dates

**Aggregation:** "How much did I spend on appliances?"
- Search: appliances in receipts
- Aggregate: Sum amounts by category
- Return: Total + breakdown

**Trend Analysis:** "Am I buying fewer electronics?"
- Query: Electronics by month for last 12 months
- Calculate: Trend
- Visualize: Timeline
```

---

## 4. Data Flow & Interactions

### Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│  Image/Video (bill, warranty, product) | Text (notes) | Query    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│             COORDINATOR AGENT (Gemini CLI)                       │
│  - Parse intent: Upload vs Query vs Organize                    │
│  - Determine urgency and priority                               │
│  - Retrieve user context from memory                            │
└────────┬───────────────────────────────────────────┬────────────┘
         │                                           │
         ▼ (if UPLOAD)                         ▼ (if QUERY)
┌─────────────────────────┐          ┌──────────────────────┐
│  EXTRACTION AGENT       │          │  RETRIEVAL AGENT     │
│                         │          │                      │
│ 1. Process multimodal   │          │ 1. Parse query       │
│    input               │          │ 2. Vector search     │
│ 2. Extract structure    │          │    (Pinecone)       │
│ 3. Validate accuracy    │          │ 3. SQL query         │
│ 4. Generate JSON output │          │    (PostgreSQL)     │
│ 5. Confidence scoring   │          │ 4. Combine results   │
└────────┬────────────────┘          │ 5. Synthesize answer │
         │                           └─────────┬─────────────┘
         │                                     │
         ▼                                     │
┌──────────────────────────────┐               │
│   STORAGE AGENT              │               │
│                              │               │
│ 1. Validate data schema      │               │
│ 2. Check for duplicates      │               │
│ 3. PostgreSQL INSERT         │               │
│ 4. Create embeddings         │               │
│ 5. Pinecone index            │               │
│ 6. Cloud Storage save        │               │
│ 7. Create audit log          │               │
└────────┬─────────────────────┘               │
         │                                     │
         ▼                                     │
    [Database Layer]◄────────────────────────┘
         │
         ├─▶ PostgreSQL (structured data)
         ├─▶ Pinecone (vector search)
         └─▶ Cloud Storage (original files)
         │
         ▼
┌──────────────────────────────────────────┐
│      COORDINATOR (Response)              │
│  - Format results for user               │
│  - Update user memory                    │
│  - Log interaction                       │
└──────────────────────────────────────────┘
         │
         ▼
    [RETURN TO USER]
```

### Agent Interaction Patterns

#### Pattern 1: Data Ingestion Flow

```python
# User uploads image of warranty document

coordinator = GeminiCLI()
user_input = {
    "type": "upload",
    "file": "warranty.jpg",
    "user_context": {...}
}

# 1. Coordinator receives and understands
intent = coordinator.understand(user_input)  # → "warranty_upload"

# 2. Route to extraction
extracted = coordinator.send_to_agent(
    agent="extraction_agent",
    task={"file": "warranty.jpg"},
    template="warranty_extraction"
)

# Response:
# {
#   "type": "warranty",
#   "extracted_data": {
#     "product_name": "Evaporative Cooler X2000",
#     "purchase_date": "2025-03-15",
#     "warranty_expiry": "2027-03-15",
#     "coverage": "Parts and labor",
#     "provider": "XYZ Warranty",
#     ...
#   },
#   "confidence_score": 0.98
# }

# 3. Route to storage
stored = coordinator.send_to_agent(
    agent="storage_agent",
    task={
        "operation": "create",
        "data": extracted["extracted_data"],
        "original_file": "warranty.jpg"
    }
)

# Response:
# {
#   "id": "mem_abc123xyz",
#   "status": "stored",
#   "embeddings_created": True,
#   "indexed_in_pinecone": True,
#   "storage_path": "gs://bucket/warranties/mem_abc123xyz.jpg"
# }

# 4. Respond to user
coordinator.respond(
    f"✓ Saved your cooler warranty! "
    f"Expires: March 15, 2027"
)
```

#### Pattern 2: Query Resolution Flow

```python
# User asks: "When does my cooler warranty expire?"

coordinator = GeminiCLI()
user_query = {
    "type": "query",
    "question": "When does my cooler warranty expire?",
    "user_context": {...}
}

# 1. Coordinator parses intent
intent = coordinator.understand(user_query)  # → "warranty_expiry_query"

# 2. Route to retrieval
results = coordinator.send_to_agent(
    agent="retrieval_agent",
    task={
        "query": user_query["question"],
        "filters": {"content_type": "warranty"},
        "search_strategy": "hybrid"
    }
)

# Response:
# [
#   {
#     "id": "mem_abc123xyz",
#     "product": "Evaporative Cooler X2000",
#     "warranty_expiry": "2027-03-15",
#     "source": "Warranty document uploaded 2025-03-20",
#     "confidence": 0.99
#   }
# ]

# 3. Synthesize into natural response
response = coordinator.synthesize(
    results=results,
    style="conversational"
)

# 4. Return to user
coordinator.respond(
    "Your cooler warranty expires on March 15, 2027. "
    "That's about 2 years from now."
)
```

---

## 5. Implementation with Gemini CLI

### Setup & Installation

```bash
# 1. Prerequisites
# - Google Cloud project with billing enabled
# - Gemini CLI installed
# - Python 3.11+

# 2. Initialize project
mkdir dailybuddy
cd dailybuddy

# 3. Create agents scaffolding (with Agents CLI or Gemini CLI)
gemini @coordinator_agent "Create a new agent project structure for DailyBuddy"

# OR using agents-cli
agents-cli create dailybuddy --template adk -y
cd dailybuddy

# 4. Install Agents CLI skills
pip install google-agents-cli
uvx google-agents-cli install

# 5. Verify Gemini CLI can see agents
gemini /agents  # List all agents
```

### Agent Configuration in .gemini/

```json
// .gemini/settings.json
{
  "model": "gemini-2.0-flash-exp",
  "temperature": 0.3,
  "experimentalFeatures": {
    "enableAgents": true
  },
  "agents": {
    "coordinator_agent": {
      "model": "gemini-2.0-flash-exp",
      "temperature": 0.1,
      "tools": ["send_to_agent", "memory_recall", "database_query"]
    },
    "extraction_agent": {
      "model": "gemini-2.0-flash-exp",
      "temperature": 0.1,
      "tools": ["gemini_vision_api", "document_analysis"]
    },
    "storage_agent": {
      "model": "gemini-2.0-flash-exp",
      "temperature": 0.0,
      "tools": ["postgresql_connection", "pinecone_api"]
    },
    "retrieval_agent": {
      "model": "gemini-2.0-flash-exp",
      "temperature": 0.3,
      "tools": ["pinecone_search", "postgresql_queries"]
    }
  }
}
```

### Running Agents Locally

```bash
# Start Gemini CLI development environment
gemini

# In Gemini CLI prompt:

# Route through coordinator
@coordinator_agent I have a bill to upload, it's a PDF of my water bill from May

# Direct to extraction (for debugging)
@extraction_agent Extract product name and warranty expiry from: ./warranty.jpg

# Direct to retrieval
@retrieval_agent When did I buy my refrigerator?

# List all available agents
/agents

# Check agent status
/agent-status

# View agent logs
/logs
```

### Building with Agents CLI

```bash
# Create project
agents-cli create dailybuddy --template adk

# Build locally
agents-cli build

# Test locally
agents-cli run coordinator_agent

# Evaluate (run test suite)
agents-cli eval run

# Deploy to Google Cloud
agents-cli deploy

# Publish for team use
agents-cli publish gemini-enterprise

# Monitor in production
agents-cli monitor
```

---

## 6. Database & Storage Design

### PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  preferences JSONB
);

-- Main memories table
CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  
  -- Content metadata
  content_type VARCHAR(50) NOT NULL,  -- 'receipt', 'warranty', 'video', 'note'
  title VARCHAR(255),
  description TEXT,
  
  -- Extracted data (flexible JSONB)
  extracted_data JSONB NOT NULL,
  
  -- Vector embedding for semantic search
  embedding_vector VECTOR(1536),
  
  -- Indexing & discovery
  tags VARCHAR(255)[] DEFAULT '{}',
  category VARCHAR(100),
  
  -- Relationships
  document_id UUID,
  related_memory_ids UUID[],
  
  -- Lifecycle
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,
  
  -- Quality metrics
  extraction_confidence FLOAT,
  is_verified BOOLEAN DEFAULT FALSE,
  verification_notes TEXT
);

-- Documents table (original files)
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  memory_id UUID NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  
  file_name VARCHAR(255),
  file_type VARCHAR(50),  -- 'image', 'video', 'pdf', 'text'
  file_size BIGINT,
  mime_type VARCHAR(100),
  
  storage_path VARCHAR(1024),  -- gs://bucket/path/to/file
  thumbnail_path VARCHAR(1024),  -- For images
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  
  operation VARCHAR(50),  -- 'CREATE', 'UPDATE', 'DELETE', 'QUERY'
  resource_type VARCHAR(100),
  resource_id UUID,
  
  old_value JSONB,
  new_value JSONB,
  
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address INET,
  agent_id VARCHAR(255)
);

-- User preferences & memory
CREATE TABLE user_memory (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  
  memory_type VARCHAR(50),  -- 'preference', 'pattern', 'context'
  key VARCHAR(255),
  value JSONB,
  
  last_accessed TIMESTAMP,
  access_count BIGINT DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_memories ON memories(user_id, created_at DESC);
CREATE INDEX idx_memory_tags ON memories USING GIN(tags);
CREATE INDEX idx_memory_category ON memories(category);
CREATE INDEX idx_memory_type ON memories(content_type);
CREATE INDEX idx_embedding ON memories USING ivfflat(embedding_vector vector_cosine_ops);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_user ON audit_log(user_id);
```

### Pinecone Configuration

```yaml
# Pinecone Vector DB setup
Index: "dailybuddy-memories"
Dimension: 1536  # Gemini Embedding 2 output
Metric: "cosine"
Pods: 3 (production scale)

Namespaces:
  - "user_memories": User-specific embeddings
  - "shared_knowledge": Optional shared knowledge base
  - "temp": Temporary embeddings during processing

Metadata Filters:
  - user_id (for isolation)
  - content_type (warranty, receipt, video, note)
  - category (electronics, home, documents, etc.)
  - date_range (for time-based filtering)
  - confidence_score (filter by extraction quality)
```

### Cloud Storage Structure

```
gs://dailybuddy-storage/
├── users/
│   ├── {user_id}/
│   │   ├── originals/
│   │   │   ├── receipts/{date}/{file_id}.pdf
│   │   │   ├── warranties/{date}/{file_id}.pdf
│   │   │   ├── videos/{date}/{file_id}.mp4
│   │   │   └── notes/{date}/{file_id}.txt
│   │   ├── processed/
│   │   │   ├── images/{file_id}_thumb.jpg
│   │   │   ├── transcripts/{file_id}.txt
│   │   │   └── extractions/{file_id}.json
│   │   └── backups/
│   │       ├── {date}_backup.tar.gz
│   │       └── {date}_metadata.json
│   └── ...
└── system/
    ├── logs/
    ├── backups/
    └── analytics/
```

---

## 7. Production Deployment

### Deployment with Agents CLI

```bash
# Step 1: Build and test locally
agents-cli build
agents-cli eval run

# Step 2: Set up infrastructure
agents-cli infra single-project
# Creates:
# - Cloud Run service
# - Cloud SQL (PostgreSQL)
# - Cloud Storage buckets
# - IAM roles and service accounts

# Step 3: Deploy agents
agents-cli deploy

# Step 4: Publish for team
agents-cli publish gemini-enterprise

# Step 5: Monitor
agents-cli logs coordinator_agent --follow
agents-cli metrics --dashboard
```

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Gemini Enterprise (UI)                          │
│  - Chat interface for all users                             │
│  - Document upload interface                               │
│  - Query interface                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   Gemini Enterprise Agent API   │
        │   (Load balanced Cloud Run)     │
        └────────────────┬────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐  ┌──────▼────┐  ┌───────▼───┐
    │Coordinator│  │Extraction│  │ Storage/  │
    │Agent     │  │Agent     │  │Retrieval  │
    │(Cloud Run)│  │(Cloud Run)│  │(Cloud Run)│
    └────┬────┘  └──────┬────┘  └───────┬───┘
         │               │               │
         └───────────────┼───────────────┘
                         │
        ┌────────────────▼────────────────┐
        │      Google Cloud Services      │
        │                                  │
        ├─ Cloud SQL (PostgreSQL)         │
        ├─ Pinecone Vector DB            │
        ├─ Cloud Storage                  │
        ├─ Cloud Secrets                  │
        ├─ Cloud Monitoring               │
        └─ Cloud Logging                  │
```

### Environment Configuration

```bash
# Set up production environment variables
gcloud secrets create GEMINI_API_KEY --data-file=-
gcloud secrets create POSTGRES_URL --data-file=-
gcloud secrets create PINECONE_API_KEY --data-file=-
gcloud secrets create PINECONE_INDEX --data-file=-

# Grant Cloud Run permissions
gcloud run services update dailybuddy \
  --set-env-vars POSTGRES_URL=cloudsql_connection \
  --add-cloudsql-instances project:region:instance
```

### Monitoring & Observability

```python
# src/monitoring.py

import logging
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3

# Cloud Logging setup
client = cloud_logging.Client()
client.setup_logging()

logger = logging.getLogger(__name__)

# Metrics to track
class DailyBuddyMetrics:
    def __init__(self):
        self.client = monitoring_v3.MetricsServiceClient()
    
    def log_extraction(self, memory_id, confidence, duration_ms):
        """Log extraction metrics"""
        logger.info({
            "event": "extraction_complete",
            "memory_id": memory_id,
            "confidence": confidence,
            "duration_ms": duration_ms
        })
    
    def log_query(self, query, results_count, duration_ms):
        """Log query metrics"""
        logger.info({
            "event": "query_executed",
            "query": query,
            "results": results_count,
            "duration_ms": duration_ms
        })
    
    def log_error(self, agent, error, context):
        """Log errors"""
        logger.error({
            "agent": agent,
            "error": str(error),
            "context": context
        })
```

---

## 8. Example Walkthrough

### Complete Example: Warranty Upload & Query

#### Step 1: User Uploads Warranty Document

```
INPUT:
- File: warranty.pdf (image of warranty document)
- User: john@example.com

┌─ COORDINATOR RECEIVES ─────────────────────────────────────┐
│ Understanding user intent:                                  │
│ - Type: Document upload                                    │
│ - Content likely: Warranty or receipt                      │
│ - Action: Process for extraction                           │
└────────────────┬────────────────────────────────────────────┘
                 │
            Sends to extraction_agent:
            {
              "task": "extract_warranty",
              "file": warranty.pdf,
              "template": "warranty_extraction"
            }
```

#### Step 2: Extraction Agent Processes

```
┌─ EXTRACTION AGENT ─────────────────────────────────────────┐
│                                                              │
│ 1. Analyze file: PDF with warranty document                │
│ 2. Apply template: warranty_extraction                     │
│ 3. Extract fields using Gemini Vision:                    │
│    - Product: "Evaporative Cooler X2000"                  │
│    - Serial: "EC2K-2025-041523"                           │
│    - Purchase date: "2025-03-15"                          │
│    - Warranty expiry: "2027-03-15"                        │
│    - Coverage: "Parts & Labor"                            │
│    - Provider: "CoolTech Warranty"                        │
│                                                              │
│ 4. Validate format:                                        │
│    - Dates: ✓ ISO 8601 format                             │
│    - All fields present: ✓                                │
│    - Confidence: 0.98 (high)                              │
│                                                              │
│ 5. Output JSON:                                            │
│ {                                                          │
│   "type": "warranty",                                     │
│   "extracted_data": {                                     │
│     "product_name": "Evaporative Cooler X2000",          │
│     "serial_number": "EC2K-2025-041523",                 │
│     "purchase_date": "2025-03-15",                       │
│     "warranty_expiry": "2027-03-15",                     │
│     "coverage_type": "Parts & Labor",                    │
│     "warranty_provider": "CoolTech Warranty"             │
│   },                                                      │
│   "confidence_score": 0.98                               │
│ }                                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
       Returns to coordinator who sends to storage_agent
```

#### Step 3: Storage Agent Persists

```
┌─ STORAGE AGENT ────────────────────────────────────────────┐
│                                                              │
│ 1. Validate data schema: ✓                                │
│                                                              │
│ 2. Check for duplicates:                                  │
│    SHA256("EC2K-2025-041523") not found → New document   │
│                                                              │
│ 3. PostgreSQL INSERT:                                     │
│    INSERT INTO memories (                                 │
│      user_id, content_type, extracted_data,              │
│      tags, category, extraction_confidence               │
│    ) VALUES (                                             │
│      'john@example.com', 'warranty', {...},              │
│      ['cooler', 'warranty', 'electronics'],              │
│      'appliances', 0.98                                   │
│    )                                                       │
│    RETURNING id → mem_abc123xyz                           │
│                                                              │
│ 4. Create embeddings with Gemini Embedding 2:            │
│    Text: "Evaporative Cooler X2000 warranty expires      │
│    March 15 2027 parts and labor coverage"               │
│    → Vector: [0.234, -0.512, ..., 0.891] (1536 dims)   │
│                                                              │
│ 5. Pinecone upsert:                                       │
│    {                                                      │
│      "id": "mem_abc123xyz",                               │
│      "values": [0.234, -0.512, ...],                     │
│      "metadata": {                                        │
│        "user_id": "john@example.com",                    │
│        "content_type": "warranty",                       │
│        "product": "Cooler",                              │
│        "expires": "2027-03-15"                           │
│      }                                                    │
│    }                                                      │
│                                                              │
│ 6. Cloud Storage save:                                    │
│    gs://dailybuddy/users/john@example.com/              │
│      warranties/2025-03/warranty_abc123xyz.pdf           │
│                                                              │
│ 7. Audit log entry:                                       │
│    INSERT INTO audit_log (user_id, operation, ...)       │
│    VALUES ('john@example.com', 'CREATE', ...)            │
│                                                              │
│ Response:                                                  │
│ {                                                          │
│   "status": "success",                                    │
│   "memory_id": "mem_abc123xyz",                          │
│   "indexed": true,                                        │
│   "storage_path": "gs://dailybuddy/users/.../..."       │
│ }                                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
       Returns to coordinator for user response
```

#### Step 4: Coordinator Responds to User

```
COORDINATOR RESPONDS:
┌────────────────────────────────────────────────────────────┐
│ ✓ Saved your warranty!                                     │
│                                                              │
│ Product: Evaporative Cooler X2000                         │
│ Expires: March 15, 2027 (in 2 years)                      │
│ Coverage: Parts & Labor                                    │
│ Provider: CoolTech Warranty                               │
│                                                              │
│ Tip: You have 3 other appliances expiring this year.      │
│ Would you like to see them?                               │
└────────────────────────────────────────────────────────────┘
```

### Days Later: User Queries

```
USER ASKS: "When does my cooler warranty expire?"

┌─ COORDINATOR ──────────────────────────────────────────────┐
│ 1. Parse intent: Query about cooler warranty expiry       │
│ 2. Route to retrieval_agent                               │
└─────────────────┬────────────────────────────────────────────┘
                  │
┌─ RETRIEVAL AGENT ──────────────────────────────────────────┐
│                                                              │
│ 1. Understand query:                                       │
│    - Entity: "cooler"                                     │
│    - Field: "warranty expiry"                            │
│    - Type: "warranty"                                     │
│                                                              │
│ 2. Vector search (Pinecone):                              │
│    Query: "cooler warranty expire"                        │
│    → Vector: [0.212, -0.493, ...]                       │
│    Results:                                                │
│    - mem_abc123xyz (score: 0.98)                         │
│      "Evaporative Cooler X2000"                          │
│      expires "2027-03-15"                                │
│                                                              │
│ 3. SQL query (PostgreSQL):                                │
│    SELECT * FROM memories                                │
│    WHERE user_id = 'john@example.com'                    │
│      AND content_type = 'warranty'                       │
│      AND extracted_data->>'product_name' ILIKE '%cooler%'│
│    Result:                                                │
│    - mem_abc123xyz (confidence: 0.98)                    │
│                                                              │
│ 4. Combine & rank:                                        │
│    Top result: mem_abc123xyz                             │
│    Source: Warranty uploaded on 2025-03-20               │
│    Confidence: 0.98                                       │
│                                                              │
│ 5. Extract answer:                                        │
│    warranty_expiry: "2027-03-15"                         │
│    product: "Evaporative Cooler X2000"                   │
│                                                              │
│ Response to coordinator:                                   │
│ {                                                          │
│   "answer": "March 15, 2027",                            │
│   "product": "Evaporative Cooler X2000",                 │
│   "source": "mem_abc123xyz",                             │
│   "confidence": 0.98                                      │
│ }                                                          │
└─────────────────┬────────────────────────────────────────────┘
                  │
┌─ COORDINATOR RESPONDS ──────────────────────────────────────┐
│ Your cooler warranty expires on March 15, 2027.           │
│ That's approximately 2 years from now.                     │
│                                                              │
│ Coverage: Parts & Labor                                    │
│ Provider: CoolTech Warranty                               │
│                                                              │
│ Would you like to see your other warranties?              │
└────────────────────────────────────────────────────────────┘
```

---

## Quick Start: Get Running in 15 Minutes

### 1. Clone & Setup (2 min)

```bash
git clone https://github.com/your-org/dailybuddy.git
cd dailybuddy

# Install dependencies
pip install -r requirements.txt
uvx google-agents-cli install
```

### 2. Configure Secrets (3 min)

```bash
cp .env.example .env
# Edit .env with your Google Cloud credentials and API keys
# - GEMINI_API_KEY
# - GOOGLE_CLOUD_PROJECT
# - POSTGRES_URL
# - PINECONE_API_KEY
```

### 3. Start Gemini CLI (2 min)

```bash
gemini

# In Gemini prompt:
@coordinator_agent I have a warranty document to upload
```

### 4. Upload & Query (5 min)

```
Follow on-screen prompts to:
1. Upload warranty image
2. Review extracted data
3. Confirm storage
4. Query the data with "When does X expire?"
```

### 5. Deploy (3 min)

```bash
agents-cli deploy
agents-cli publish gemini-enterprise
```

---

## Best Practices Summary

✅ **DO:**
- Use Markdown for all agent definitions
- Route through coordinator_agent
- Test extraction accuracy before production
- Maintain audit logs for compliance
- Use Gemini Embedding 2 for vectors
- Implement hybrid search (vector + SQL)
- Monitor extraction confidence scores
- Version control all configurations

❌ **DON'T:**
- Call agents directly (use coordinator)
- Store unencrypted sensitive data
- Skip extraction validation
- Use single-source retrieval
- Ignore extraction confidence < 0.7
- Manually handle multimodal data (let Gemini do it)
- Deploy without running eval suite

---

## Additional Resources

- Agents CLI is available at https://github.com/google/agents-cli and provides unified programmatic backbone for the Agent Development Lifecycle on Google Cloud
- Subagents can be bundled as part of Gemini CLI extensions using agent definition Markdown files (.md) in an agents/ directory
- Gemini's context window supports up to 1 million tokens for Pro models - enough for full-day transcripts, hundreds of PDFs, or multi-hour video

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** May 2026
