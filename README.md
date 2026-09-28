# Smart Recipe Concierge 🍳

Smart Recipe Concierge is an agentic AI assistant built with the **Google Agent Development Kit (ADK)**, **Gemini 2.5 Flash**, **Firestore**, **Google Cloud Storage**, and **A2UI v0.8**. It provides pantry management, recipe discovery, missing ingredient calculations, AI image generation, Python sandbox execution, and rich UI display cards.

![Smart Recipe Concierge Demo](./demo.gif)

---

## 🌟 Key Features

- **🧺 Pantry & Recipe Management (Firestore Backend)**
  - Stores and queries personal pantry inventory (`pantry_items`) and saved recipes (`recipes`) in Google Cloud Firestore.
  - Calculates missing vs. available ingredients automatically before cooking (`check_pantry_recipe_availability`).

- **🔍 Public Recipe Discovery**
  - Searches online culinary databases using **TheMealDB API** (`search_public_recipes`).

- **🎨 Multimodal Dish Image Generation (Imagen 3 / Gemini)**
  - Generates realistic dish imagery using `gemini-3.1-flash-lite-image` (`generate_dish_image`).
  - Automatically uploads generated images to a public Google Cloud Storage bucket (`smart-recipe-concierge-qwiklabs-gcp-03-7698bbba51cd`) and returns shareable public URLs.

- **💻 Agent Platform Code Execution**
  - Safe Python execution in a cloud sandbox using `AgentEngineSandboxCodeExecutor` for complex calculations, scaling recipes, or math.

- **📱 A2UI Rich Card Display**
  - Formats responses using `A2uiSchemaManager(version="0.8")` and an `after_model_callback` for native card rendering in `adk web` and custom frontends.

- **⚡ FastAPI Proxy & Cloud Run Frontend**
  - A lightweight FastAPI proxy in `./frontend` that authenticates via Application Default Credentials and communicates over the **A2A (Agent-to-Agent)** protocol to Agent Runtime on GCP.

---

## 🏗️ Architecture

```
Browser (Chat UI)
      │
      ▼
FastAPI Proxy (frontend/main.py)
      │  (A2A Protocol)
      ▼
Agent Runtime / Agent Engine (Gemini 2.5 Flash)
 ├── Firestore Database (pantry_items, recipes)
 ├── Cloud Storage Bucket (dish images)
 ├── TheMealDB API (public recipe search)
 ├── AgentEngineSandboxCodeExecutor (Python sandbox)
 └── A2UI v0.8 Schema Manager (Rich Display Cards)
```

---

## 🚀 Quick Start

### 1. Local Agent Execution

Install dependencies and run the agent locally with `agents-cli`:

```bash
uv sync
agents-cli run "What items do I have in my pantry?"
```

### 2. Local Agent Playground

Launch the interactive ADK playground on port `8080`:

```bash
agents-cli playground --host 0.0.0.0 --port 8080 --reload_agents
```

### 3. Frontend Chat Server

To run the frontend proxy server locally:

```bash
cd frontend
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/us-east1/reasoningEngines/<id>"
export AGENT_DIRECTORY="app"
uv run python main.py
```

Visit `http://localhost:8080` in your browser.

---

## 🛠️ Tools Reference

| Tool Name | Type | Description |
|---|---|---|
| `get_pantry_items` | Function Tool | Fetch pantry items from Firestore |
| `add_pantry_item` | Function Tool | Add new ingredients to Firestore |
| `get_recipes` | Function Tool | Fetch custom saved recipes |
| `add_recipe` | Function Tool | Save new recipes to Firestore |
| `check_pantry_recipe_availability` | Function Tool | Compare recipe requirements against pantry stock |
| `search_public_recipes` | Function Tool | Query public recipes via TheMealDB API |
| `generate_dish_image` | Function Tool | Generate dish image & upload to GCS bucket |
| `AgentEngineSandboxCodeExecutor` | Code Executor | Execute Python code in Agent Engine sandbox |

---

## 📜 License

Apache 2.0
