# DailyBuddy: Quick Start & Reference

## 🎯 What You're Building

A **personal knowledge management AI system** where:

- User **uploads** documents (warranty photos, receipts, bills, notes)
- System **extracts** structured information using Gemini Vision
- System **stores** it across PostgreSQL + Pinecone + Cloud Storage
- User **queries** with natural language
- System **retrieves** and answers instantly

**Real Example:**
```
Upload: Warranty photo of a cooler
Extract: Product="Cooler X2000", Expires="March 15, 2027"
Store: In database with AI embeddings
Query: "When does my cooler expire?"
Answer: "March 15, 2027" ✓
```

---

## 🏗️ Architecture at a Glance

```
User → Coordinator Agent → {Extraction | Storage | Retrieval} → Databases
                                          ↓
                        {Gemini API | PostgreSQL | Pinecone}
```

**4 Key Agents:**
1. **Coordinator** - Understands intent, routes tasks
2. **Extraction** - Parses images/video to get structured data
3. **Storage** - Saves to 3 places: DB + vectors + files
4. **Retrieval** - Searches and answers questions

---

## ⚡ 30-Minute Setup

### Step 1: Clone & Install (5 min)

```bash
git clone https://github.com/your-org/dailybuddy
cd dailybuddy
pip install -r requirements.txt
```

### Step 2: Configure (5 min)

```bash
cp .env.example .env
# Edit with your keys:
# GEMINI_API_KEY=...
# POSTGRES_URL=postgresql://...
# PINECONE_API_KEY=...
```

### Step 3: Create Agent Definitions (5 min)

Create `.gemini/agents/coordinator.md`:
```markdown
---
name: coordinator_agent
description: Main orchestrator for DailyBuddy
tools: [extraction, storage, retrieval]
---

You are the coordinator. Route uploads to extraction_agent.
Route queries to retrieval_agent.
```

Create similar files for extraction.md, storage.md, retrieval.md

### Step 4: Start & Test (10 min)

```bash
gemini

# In Gemini CLI:
@coordinator_agent I'm uploading a warranty document
# Upload file
# Get confirmation ✓

@coordinator_agent When does my warranty expire?
# Get answer from system
```

### Step 5: Deploy (5 min)

```bash
agents-cli deploy
agents-cli publish gemini-enterprise
```

---

## 📝 Key Markdown Files

### AGENTS.md (Root Level)
```markdown
# AGENTS.md - DailyBuddy System Manual

## Agents
1. Coordinator - Routes requests
2. Extraction - Parses documents  
3. Storage - Persists data
4. Retrieval - Answers questions

## Build Commands
agents-cli build
agents-cli deploy

## Constraints
- Always validate extraction confidence
- Never expose API keys
- Log all operations
```

### .gemini/agents/extraction.md
```markdown
---
name: extraction_agent
---

## Your Job
Extract structured data from:
- Images (receipts, warranties, bills)
- Videos (product demos)
- Text (notes)

Return JSON with:
- extracted_fields: {...}
- confidence: 0-1
- flags: [any issues]
```

### .gemini/agents/storage.md
```markdown
---
name: storage_agent
---

## Your Job
1. Insert into PostgreSQL
2. Create embeddings
3. Index in Pinecone
4. Log audit trail

Ensure all data is:
- Validated
- Tagged
- Categorized
- Audit-logged
```

### .gemini/agents/retrieval.md
```markdown
---
name: retrieval_agent
---

## Your Job
1. Parse question
2. Vector search in Pinecone
3. SQL query in PostgreSQL
4. Combine and rank
5. Synthesize answer

Always cite sources.
```

---

## 💻 Core Python Code (Copy-Paste Ready)

### ExtractionAgent

```python
import google.generativeai as genai
import json

class ExtractionAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def extract_from_image(self, image_path):
        import base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        
        response = self.model.generate_content([
            {"mime_type": "image/jpeg", "data": img_data},
            "Extract all information from this image. Return JSON."
        ])
        
        # Parse response
        json_str = response.text.split('{')[1].split('}')[0]
        return json.loads('{' + json_str + '}')
```

### StorageAgent

```python
import pinecone
from sqlalchemy.orm import Session

class StorageAgent:
    def __init__(self, db, pinecone_key, pinecone_index):
        self.db = db
        self.pinecone_index = pinecone_index
        pinecone.Pinecone(api_key=pinecone_key)
    
    async def store(self, user_id, extracted_data):
        # 1. Save to PostgreSQL
        memory = Memory(
            user_id=user_id,
            extracted_data=extracted_data
        )
        self.db.add(memory)
        self.db.commit()
        
        # 2. Create embedding & index in Pinecone
        embedding = genai.embed_content(
            model="models/embedding-001",
            content=str(extracted_data)
        )['embedding']
        
        index = pinecone.Index(self.pinecone_index)
        index.upsert([(str(memory.id), embedding, {})])
        
        return {"status": "success", "id": str(memory.id)}
```

### RetrievalAgent

```python
class RetrievalAgent:
    def __init__(self, db, pinecone_key, pinecone_index):
        self.db = db
        self.pinecone_index = pinecone_index
        pinecone.Pinecone(api_key=pinecone_key)
    
    async def retrieve(self, user_id, query):
        # 1. Vector search
        q_embedding = genai.embed_content(
            model="models/embedding-001",
            content=query
        )['embedding']
        
        index = pinecone.Index(self.pinecone_index)
        results = index.query(
            vector=q_embedding, top_k=5,
            filter={"user_id": user_id}
        )
        
        # 2. Synthesize answer
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(
            f"User asked: {query}\n\nData: {results}"
        )
        
        return {"answer": response.text}
```

---

## 🗄️ Database (PostgreSQL)

```sql
-- Main table
CREATE TABLE memories (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    content_type VARCHAR(50),  -- warranty, receipt, bill, note
    extracted_data JSONB,
    embedding VECTOR(1536),
    tags VARCHAR[],
    created_at TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_user_memories ON memories(user_id, created_at);
CREATE INDEX idx_type ON memories(content_type);
```

**Pinecone:**
```
Index: "dailybuddy-memories"
Dimension: 1536
Namespace: "user_memories"
Metadata: user_id, content_type, category
```

---

## 🚀 Deployment Commands

```bash
# Local development
gemini

# Build & test
agents-cli build
agents-cli eval run

# Deploy to Google Cloud
agents-cli infra single-project
agents-cli deploy

# Publish for team
agents-cli publish gemini-enterprise

# Monitor
agents-cli logs coordinator_agent --follow
agents-cli metrics
```

---

## 📊 Example Data Flow

### Scenario 1: Upload Warranty

```
User: [Uploads warranty.jpg]
         ↓
Coordinator: "This looks like a document, routing to extraction"
         ↓
Extraction: "Found: Product=Cooler, Expiry=2027-03-15, Confidence=0.98"
         ↓
Coordinator: "Confidence is high, routing to storage"
         ↓
Storage: 
  1. PostgreSQL: INSERT memory
  2. Pinecone: Index vector
  3. Cloud Storage: Save original
  4. Audit: Log this action
         ↓
Coordinator: "✓ Saved! Your cooler warranty expires March 15, 2027"
```

### Scenario 2: Ask Question

```
User: "When does my warranty expire?"
         ↓
Coordinator: "This is a query, routing to retrieval"
         ↓
Retrieval:
  1. Create embedding of question
  2. Search Pinecone (vector similarity) → found warrant doc
  3. Search PostgreSQL (keyword match) → same doc
  4. Extract warranty expiry: "2027-03-15"
         ↓
Coordinator: "Your warranty expires March 15, 2027 (about 2 years from now)"
```

---

## ✅ Validation Checklist

Before going production:

- [ ] All agents defined in `.gemini/agents/` as Markdown
- [ ] AGENTS.md created with system guidelines
- [ ] PostgreSQL tables created with proper indexes
- [ ] Pinecone index created and tested
- [ ] Cloud Storage bucket created
- [ ] Gemini API key configured
- [ ] Extraction confidence threshold set to 0.7
- [ ] Storage agent creates embeddings for all data
- [ ] Retrieval agent uses hybrid search (vector + SQL)
- [ ] Audit logging implemented
- [ ] Error handling for low confidence
- [ ] Tests pass: `agents-cli eval run`
- [ ] Monitoring configured

---

## 🔍 Troubleshooting

| Problem | Fix |
|---------|-----|
| "Agent not found" | Check `.gemini/agents/` folder, verify markdown files |
| "Low confidence extraction" | Review image quality, use better scan |
| "Query returns nothing" | Verify memory was saved, try different search terms |
| "Pinecone error" | Check API key, verify index name |
| "Database connection failed" | Check POSTGRES_URL format |
| "Gemini API error" | Verify API key, check quota |

---

## 📖 Documentation Files Provided

1. **dailybuddy_complete_guide.md** - Full system design, architecture, all details
2. **dailybuddy_code_templates.md** - Complete code for all components
3. **DAILYBUDDY_QUICK_START.md** - This file (quick reference)

---

## 🎓 Next Steps

1. **Read** `dailybuddy_complete_guide.md` for full details
2. **Copy** code from `dailybuddy_code_templates.md`
3. **Create** `.gemini/agents/` markdown files
4. **Setup** PostgreSQL + Pinecone + Cloud Storage
5. **Test** locally with Gemini CLI
6. **Deploy** using `agents-cli`
7. **Monitor** with logs and metrics

---

## 🎯 Success Metrics

Your system is working when:
- ✓ Upload warranty → Extract data successfully
- ✓ Data stored in PostgreSQL + Pinecone
- ✓ Vector search returns relevant documents
- ✓ Natural language query returns correct answer
- ✓ Confidence scores > 0.8 for extractions
- ✓ Latency < 1 second for queries
- ✓ 100% uptime on production

---

**Version:** 1.0  
**Last Updated:** May 2026  
**Status:** Ready to Code

Start with Step 1 above. You have everything needed. 🚀
