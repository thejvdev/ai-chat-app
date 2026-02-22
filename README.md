[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)](https://react.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-000000?logo=shadcnui&logoColor=white)](https://ui.shadcn.com/)

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/Alembic-5A9E3F?logoColor=white)](https://alembic.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![NGINX](https://img.shields.io/badge/NGINX-009639?logo=nginx&logoColor=white)](https://nginx.org/)

[![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![SearXNG](https://img.shields.io/badge/SearXNG-1F6FEB?logo=searxng&logoColor=white)](https://docs.searxng.org/)
[![Unstructured](https://img.shields.io/badge/Unstructured-4B5563?logoColor=white)](https://unstructured.io/)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC244C?logoColor=white)](https://qdrant.tech/)

# AI Chat Application

This repository contains my **AI-powered web app**. It’s still under active development, but there is already a working **alpha** version.

## Auth Service

**Responsibility:** Access control and identity management.

- **Authentication:** JWT implementation (Access & Refresh tokens) using asymmetric encryption **RS256**.
- **Security:** Tokens are stored exclusively in **HttpOnly cookies** to mitigate XSS attacks.
- **User Management:** Handles user registration, login, and profile management in **PostgreSQL**.

## Chat Service

**Responsibility:** Chat business logic and data persistence.

- **Persistence:** Stores chat structure, metadata, and full message history.
- **Data Integrity:** Uses **Alembic** for database schema versioning and migrations.
- **Orchestration Logic:** Receives client requests, validates them, and coordinates interactions with the **LLM Service** to generate responses.

## LLM Service

**Responsibility:** Intelligent request orchestration, context management, and response generation.

- **LLM Runtime:** Direct integration with **Ollama** for local text generation.
- **Orchestrator Agent:** Acts as the intelligent core, analyzing user intent and selecting the optimal processing strategy:

  - **Deep Research:**  
    Executes a comprehensive pipeline including data collection via the **SearXNG API**, dynamic RAG over retrieved web pages (parsing, chunking, reranking), and synthesis of the final response based on verified findings.

  - **Knowledge Base:**  
    Works with local documents through a persistent RAG pipeline.

  - **Direct Response:**  
    Generates answers directly using the model’s internal weights (**Llama 3.1**) when additional context is not required.

- **RAG Pipeline:**  
  Built on **Unstructured** for intelligent document parsing and chunking, combined with vectorization and semantic search in **Qdrant**.  
  To minimize hallucinations and maximize accuracy, a reranking stage filters and prioritizes only the most relevant text segments before they are fed into the LLM.

## Infrastructure & Data Layer

- **Gateway (NGINX):** Acts as an API Gateway, routing external requests to the appropriate microservices.
- **Data Storage:** Hybrid persistence model — relational **PostgreSQL** for structured data and vector-based **Qdrant** for AI context storage.
- **Containerization:** The entire stack is deployed with **Docker**, ensuring service isolation and consistent environments.

## Author

Created by [Denys Bondarchuk](https://github.com/thejvdev). Feel free to reach out or contribute to the project!
