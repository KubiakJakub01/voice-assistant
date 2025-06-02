# Voice Assistant

A voice assistant for gastronomy applications, specifically built for "Poligon Smaków WAT" restaurant. This assistant utilizes OpenAI's Realtime API for speech-to-text (STT) and text-to-speech (TTS) capabilities, combined with the `openai-agents` SDK for intelligent, agent-based conversation handling.

## Table of Contents
- [Voice Assistant](#voice-assistant)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Architecture](#architecture)
    - [System Components](#system-components)
    - [Interaction Flow](#interaction-flow)
  - [Technologies Used](#technologies-used)
  - [Project Structure](#project-structure)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Backend Server](#running-the-backend-server)
    - [Running the Frontend](#running-the-frontend)
  - [Future Development](#future-development)

## Project Overview

This project implements a voice assistant for a restaurant, designed to enhance customer interaction by automating common tasks. Built with Python and FastAPI, it leverages WebSocket for real-time voice communication. The core of the system is an agent-based architecture featuring specialized AI agents:
*   `Triage Agent`: Directs user queries to the appropriate specialist.
*   `Information Agent`: Provides details about the restaurant and menu.
*   `Order Agent`: Handles food and drink orders.
*   `Reservation Agent`: Manages table bookings.

The assistant uses Large Language Models (LLMs) for Natural Language Processing (NLP) and a set of custom tools (`agent_tools`) for interacting with a simulated restaurant database (e.g., searching the menu, checking order status, making reservations). The result is a functional prototype capable of engaging in natural conversation, understanding user intent, and performing key restaurant operations.

## Features

The voice assistant supports the following functionalities:

1.  **Information Provision:**
    *   Answer questions about the menu (available dishes, prices, ingredients) using tools like `find_menu_item_by_name` and `query_restaurant_database`.
    *   Provide details about the restaurant, such as opening hours, location, and contact information, managed by the `Information Agent` using the `query_restaurant_database` tool.
2.  **Order Taking:**
    *   Allow customers to place orders for menu items, handled by the `Order Agent` with the `place_order` tool.
    *   Check the status of a previously placed order using the `get_order_status` tool.
3.  **Reservation Management:**
    *   Enable customers to book a table for a specific date and time, managed by the `Reservation Agent` using the `make_reservation` tool.
    *   Process dates provided in natural language (e.g., "tomorrow at 7 PM") using the `convert_natural_date_to_iso` tool.
4.  **General Dialogue Handling:**
    *   Recognize the user's intent and route the conversation to the most appropriate agent, orchestrated by the `Triage Agent`.
    *   Manage basic conversation flow and context.

## Architecture

The system employs a modular architecture to ensure flexibility and a clear separation of concerns.

### System Components

1.  **User Interface (Client):** (Assumed) A frontend application (web or mobile) that captures user's voice, streams audio to the backend via WebSocket, and plays back the assistant's voice responses.
2.  **Backend Server (FastAPI):** Built with Python and the FastAPI framework (`server/server.py`). It manages:
    *   WebSocket connections (`/ws` endpoint) for real-time, bidirectional communication.
    *   Core application logic and coordination of other components.
    *   A RESTful API (prefix `/api`, defined in `app/routers.py`) for potential alternative interactions or system management.
3.  **Voice Processing Pipeline (`VoicePipeline`):** Integrated within the server (`server/server.py`), this pipeline handles all voice data:
    *   **Speech-to-Text (STT):** Converts incoming audio streams from the user into text.
    *   **Text-to-Speech (TTS):** Converts textual responses from AI agents into an audio stream sent back to the client.
    *   Supports audio streaming for fluid interaction.
4.  **AI Agent System:** The decision-making core, primarily defined in `app/agent_config.py` (agent definitions) and `prompts/agents_prompts.yml` (agent instructions). It uses an LLM (e.g., `gpt-4o-mini`) and consists of:
    *   **`Triage Agent`:** The main dispatcher, analyzing initial user queries and handing off to specialized agents.
    *   **`Information Agent`:** Provides information about the restaurant (menu, hours, etc.) using the `query_restaurant_database` tool.
    *   **`Order Agent`:** Manages food/drink orders (`place_order` tool), checks order status (`get_order_status`), and searches menu items (`find_menu_item_by_name`).
    *   **`Reservation Agent`:** Handles table reservations (`make_reservation` tool) and converts natural language dates (`convert_natural_date_to_iso`).
    *   Agents utilize a predefined set of tools (functions in `app/agent_tools.py`) for specific actions and data retrieval. A "handoff" mechanism allows seamless conversation transfer between agents.
5.  **Database (Simulated):**
    *   Data structures for menu items, orders, and reservations are defined in `app/models.py`.
    *   CRUD (Create, Read, Update, Delete) operations are handled by functions in `app/crud.py`.
    *   For the prototype, this is typically an internal database (e.g., SQLite), initialized by the `server/create_db_tables.py` script.

### Interaction Flow

1.  The user issues a voice command to the client application.
2.  The client streams the audio data via WebSocket to the FastAPI server.
3.  The server's `VoicePipeline` converts the audio to text (STT).
4.  The transcribed text is passed to the `Triage Agent`.
5.  The `Triage Agent` (or a subsequently assigned specialized agent) processes the query using the LLM. If necessary, it invokes tools from `agent_tools.py` which may interact with the database via `crud.py`.
6.  The agent's textual response is sent to the `VoicePipeline`.
7.  The `VoicePipeline` converts the text to speech (TTS) and streams the audio response back to the client via WebSocket.
8.  The client plays the voice response to the user.

## Technologies Used

*   **Backend:** Python (3.11.4), FastAPI, Uvicorn
*   **AI & NLP:** OpenAI GPT-4o-mini (or other configured LLM), OpenAI Realtime API for STT/TTS, `openai-agents` SDK
*   **Database:** SQLite (for the simulated database)
*   **Dependency Management:**
    *   Backend (Python): Poetry (`pyproject.toml`), `uv` (`uv.lock`, `Makefile` for sync)
    *   Frontend: npm
*   **API & Communication:** WebSocket, REST
*   **Version Control:** Git
*   **Frontend:** (Assumed to be a JavaScript/TypeScript based application, e.g., React, Vue, Angular, Svelte, managed with npm)

## Project Structure

```
voice-assistant/
├── frontend/                   # Frontend application (assumed structure)
│   ├── ...
│   └── package.json
├── server/                     # Backend FastAPI application
│   ├── app/                    # Core application logic
│   │   ├── agent_config.py     # AI agent configurations
│   │   ├── agent_tools.py      # Tools callable by agents
│   │   ├── crud.py             # Database CRUD operations
│   │   ├── models.py           # SQLAlchemy ORM models / Pydantic models
│   │   ├── routers.py          # API route definitions
│   │   └── settings.py         # Application settings
│   ├── data/                   # (Potentially for initial data or other data files)
│   ├── prompts/                # Prompts and instructions for AI agents
│   │   └── agents_prompts.yml
│   ├── .python-version         # Specifies Python version (e.g., 3.11.4)
│   ├── .venv/                  # Virtual environment (if created by Poetry/uv)
│   ├── create_db_tables.py     # Script to initialize database schema
│   ├── pyproject.toml          # Project metadata and dependencies (Poetry)
│   ├── server.py               # Main FastAPI application, WebSocket endpoint, VoicePipeline
│   └── uv.lock                 # Pinned dependencies for uv
├── raport/                     # Project report documents
│   └── img/
│       └── raport.tex          # LaTeX source of the project report
├── .gitignore
├── Makefile                    # Automation for setup and running tasks
└── README.md                   # This file
```

## Setup

### Prerequisites

*   Python 3.11.4 (as specified in `server/.python-version`)
*   `uv` (Python package installer: `pip install uv`)
*   Node.js and npm (for the frontend part)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd voice-assistant
    ```

2.  **Set up frontend and backend dependencies:**
    This command will install frontend dependencies using `npm` and backend dependencies using `uv`.
    ```bash
    make sync
    ```
    Alternatively, to set up manually:
    *   **Backend (`server/` directory):**
        ```bash
        cd server
        uv sync  # Installs dependencies from uv.lock / pyproject.toml
        cd ..
        ```
    *   **Frontend (`frontend/` directory):**
        ```bash
        cd frontend
        npm install
        cd ..
        ```

3.  **Initialize the Database (Backend):**
    The system uses a simulated database (e.g., SQLite). To create the necessary tables:
    ```bash
    cd server
    python create_db_tables.py
    cd ..
    ```

## Usage

### Running the Backend Server

The backend server is a FastAPI application. To start it:

1.  Navigate to the `server` directory:
    ```bash
    cd server
    ```
2.  Run the server script:
    ```bash
    python server.py
    ```
    This will typically start the server on `http://0.0.0.0:8000` (or `http://localhost:8000`). The console output will confirm the address and port.

### Running the Frontend

The frontend application (assumed to be in the `frontend/` directory) can be started using the Makefile target:

1.  From the project root directory:
    ```bash
    make serve
    ```
    This command executes `cd frontend && npm run dev`, which usually starts a development server for the frontend. The frontend will then connect to the backend server.

Ensure the backend server is running before starting the frontend.

## Future Development

Potential enhancements and future directions for this project include:

*   **Real-World Integration:** Connect with actual restaurant Point of Sale (POS) systems, online reservation platforms, and inventory management software.
*   **Advanced Conversational AI:** Implement more sophisticated context and memory management for longer, more natural dialogues (e.g., recalling past orders).
*   **Personalization:** Allow the assistant to remember regular customers' preferences (favorite dishes, common booking times) for a tailored experience.
*   **Multilingual Support:** Extend the assistant's capabilities to support multiple languages.
*   **Expanded Agent Toolkit:** Add new tools for functionalities like online payment processing, integration with food delivery platforms, or customer feedback collection.
*   **Continuous Learning:** Develop mechanisms for the system (or its administrators) to analyze conversations and identify areas for improving prompts or adding new intent handling.
*   **Richer User Interface:** Create a dedicated client application with a more visually rich interface, such as displaying the menu with images or an interactive reservation calendar.
