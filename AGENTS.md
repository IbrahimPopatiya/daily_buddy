# AGENTS.md - DailyBuddy System Manual

## Overview
DailyBuddy is a personal knowledge management system that ingests daily life data (images, videos, text) and provides intelligent retrieval through natural language.

## Core Agents

### 1. Coordinator Agent (Main)
- **Role**: Route requests to specialized agents.
- **Tools**: `send_to_agent`, `memory_recall`.

### 2. Extraction Agent
- **Role**: Extract structured data from multimodal inputs.
- **Tools**: Gemini Vision API, Video API.

### 3. Storage Agent
- **Role**: Persist and index extracted information.
- **Database**: PostgreSQL + Pinecone + Local Storage (Raw files).

### 4. Retrieval Agent
- **Role**: Answer natural language queries.
- **Search**: Hybrid (Vector + SQL).

## Constraints
- Confidence > 0.7 required for auto-storage.
- Dates must be ISO 8601.
- All operations must be logged.
