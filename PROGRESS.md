# Progress

Track your progress through the masterclass. Update this file as you complete modules - Claude Code reads this to understand where you are in the project.

## Convention
- `[ ]` = Not started
- `[-]` = In progress
- `[x]` = Completed

## Modules

### Module 1: App Shell + Observability

#### Phase 1: Project Scaffolding
- [x] Frontend: React + Vite + TypeScript + Tailwind + shadcn/ui
- [x] Backend: Python + FastAPI + venv
- [x] Folder structures created
- [x] .env.example files created

#### Phase 2: Database Schema
- [x] threads table with RLS
- [x] messages table with RLS
- [x] SQL migrations created

#### Phase 3: Authentication
- [x] Backend JWT middleware
- [x] Frontend Supabase client
- [x] AuthContext provider
- [x] LoginForm component
- [x] SignupForm component
- [x] AuthGuard component

#### Phase 4: Thread Management
- [x] Thread CRUD API endpoints
- [x] Get messages endpoint
- [x] ThreadList component
- [x] ThreadItem component
- [x] useThreads hook

#### Phase 5: OpenAI + Observability
- [x] LangSmith service with wrapped OpenAI client
- [x] OpenAI Responses API service
- [x] SSE streaming chat endpoint

#### Phase 6: Chat UI
- [x] MessageBubble component
- [x] MessageList component
- [x] TypingIndicator component
- [x] ChatInput component
- [x] ChatContainer component
- [x] useChat hook with SSE

#### Phase 7: Final Integration
- [x] MainLayout component
- [x] ChatPage component
- [x] App.tsx with AuthGuard

#### Validation
- [x] Supabase connection verified (URL + anon key configured)
- [x] User signup flow working
- [x] User login flow
- [x] Chat with OpenAI Responses API (gpt-4o-mini)
- [x] Verify LangSmith traces appear in dashboard
- [x] Test RLS policies block cross-user access

**Module 1 Complete!**

### Module 2: LLM Provider Abstraction Layer

#### Phase 1: Foundation
- [x] Core config.py with Pydantic settings
- [x] Updated .env.example with provider variables
- [x] Marked openai_thread_id as deprecated in thread.py

#### Phase 2: LLM Module Setup
- [x] Provider configuration (llm/config.py)
- [x] Message types (llm/types.py)
- [x] Module exports (llm/__init__.py)

#### Phase 3: LLM Client
- [x] Unified LLM client with Chat Completions streaming
- [x] LangSmith tracing via wrap_openai

#### Phase 4: Integration
- [x] Updated chat.py to use new LLM service
- [x] Removed Responses API dependencies

#### Phase 5: Cleanup
- [x] Deleted openai_service.py
- [x] Deleted langsmith_service.py
- [x] Added pydantic-settings to requirements.txt

#### Validation
- [x] Config imports and settings validated
- [x] LLM module imports validated
- [x] Provider config returns correct values
- [x] Chat router imports validated

**Module 2 Complete!**

### Module 3: RAG Document Ingestion + Retrieval

#### Phase 1: Database Schema
- [x] Enable pgvector extension
- [x] documents table (id, user_id, filename, storage_path, status, created_at)
- [x] chunks table (id, document_id, content, embedding, metadata)
- [x] RLS policies for documents and chunks
- [x] match_chunks function for vector similarity search

#### Phase 2: File Storage
- [x] Supabase Storage bucket for documents
- [x] Storage RLS policies (users can only access their own files)

#### Phase 3: Document Upload API
- [x] POST /api/documents/upload endpoint
- [x] GET /api/documents to list user's documents
- [x] GET /api/documents/{id} to get document details
- [x] DELETE /api/documents/{id} to delete document
- [x] POST /api/documents/{id}/process to trigger processing

#### Phase 4: Ingestion Pipeline
- [x] Chunking logic (split documents into overlapping chunks)
- [x] Embedding generation (OpenAI text-embedding-3-small via OpenRouter)
- [x] Store chunks with embeddings in pgvector

#### Phase 5: Documents UI
- [x] FileUpload component with drag-and-drop
- [x] DocumentItem component with status display
- [x] DocumentList component
- [x] DocumentsPage with upload and list
- [x] useDocuments hook with Realtime subscription
- [x] AppLayout with navigation between Chat and Documents

#### Phase 6: Retrieval Integration
- [x] Retrieval service with vector similarity search
- [x] Context formatting for LLM prompts
- [x] Chat router integration with RAG context
- [x] Updated LLM client to accept optional context

#### Validation
- [ ] Upload a document and verify it appears in the list
- [ ] Verify document processing creates chunks
- [ ] Ask a question related to uploaded documents
- [ ] Verify response uses document context

**Module 3 In Progress - Code Complete, Pending Validation**
