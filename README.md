[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-000000?logo=shadcnui&logoColor=white)](https://ui.shadcn.com/)

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![NGINX](https://img.shields.io/badge/NGINX-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![Ollama](https://img.shields.io/badge/Ollama-000000?logo=ollama&logoColor=white)](https://ollama.com/)

# AI Chat Application

This repository contains my **AI-powered web app**. It’s still under active development, but there is already a working **alpha** version.

## Architecture

- **Frontend:** Next.js web UI  
- **Backend:** microservices (Auth Service + Chat Service)  
- **Gateway:** NGINX (API Gateway / reverse proxy)  
- **Data/LLM:** PostgreSQL + Ollama  
- **Infra:** Docker (containerized services for local development)

## Auth

Authentication is handled by a dedicated **Auth Service**.  
I use **JWT** for both **access** and **refresh** tokens, signed with **RS256** (asymmetric keys) and stored in **HttpOnly cookies**.  
Requests are authorized via the access token, and sessions are renewed using the refresh token.

For LLM responses via Ollama, I use **Llama 3** (**8.03B parameters**).

## Roadmap

- Improve UI/UX and overall performance
- Build a stronger answer pipeline with **web search** + **document reading** using an **Agentic AI** approach

> [!NOTE]
>
> Run Llama 3 locally with care — it can be **memory-intensive**.

## Author

Created by [Denys Bondarchuk](https://github.com/thejvdev). Feel free to reach out or contribute!
