# SecondMind

SecondMind is a local-first personal AI memory assistant built with Django and Ollama. It lets a user chat with an AI that remembers important details, retrieves relevant memories, and can forget specific memories on request.

This project is designed for privacy-conscious, offline-friendly personal memory workflows and is a strong fit for experimentation, learning, and Hacktoberfest contributions.

## Why this project?

People often repeat preferences, facts, and personal context across conversations. SecondMind stores those details as memories and retrieves the most relevant ones before generating a response.

Instead of depending on a cloud-only AI memory system, this project keeps the memory workflow local-first and easy to extend.

## Features

- Local-first memory storage using Django models
- Semantic retrieval of relevant memories
- AI chat flow with Ollama-powered models
- Memory recall and deletion APIs
- Simple browser-based interface
- Extensible architecture for future AI and UX features

## Tech stack

- Python
- Django
- SQLite
- Ollama
- HTML/CSS/JS frontend templates

## Project structure

```text
secondmind/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── memory/
│   ├── admin.py
│   ├── agent.py
│   ├── llm.py
│   ├── models.py
│   ├── retrieval.py
│   ├── tools.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── index.html
│   └── new_index.html
├── .env.example
├── db.sqlite3
├── manage.py
├── requirements.txt
├── README.md
└── tests/
```

## Core workflow

1. User sends a message to the chat endpoint.
2. The app retrieves the most relevant memories from the local memory store.
3. The LLM uses those memories as context.
4. If needed, the AI can call tools to store or forget memory entries.
5. The response is returned through the Django API.

## API endpoints

- GET /api/health/ — health check
- POST /api/chat/ — send a message to the assistant
- GET /api/memories/ — list all stored memories
- POST /api/memories/ — add a new memory
- DELETE /api/memories/<id>/ — delete a memory
- POST /api/recall/ — retrieve relevant memories for a query

## Local setup

### 1. Clone the repository

```bash
git clone https://github.com/RathnamS089/secondmind.git
cd secondmind
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install django python-dotenv
```

If you want to add more project dependencies later, update `requirements.txt` and install from it.

### 4. Start Ollama

Install and run Ollama locally, then pull the models used by the project:

```bash
ollama serve
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

### 5. Configure environment variables

Copy the sample environment file:

```bash
cp .env.example .env
```

The default configuration is:

```env
LLM_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:1.5b
EMBED_MODEL=nomic-embed-text
RECALL_THRESHOLD=0.35
```

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Start the app

```bash
python manage.py runserver
```

Then open:

```text
http://localhost:8000
```

## Contribution ideas

This project is a good candidate for Hacktoberfest contributions because it is simple to explore and easy to extend. Potential ideas include:

- improving the UI/UX
- adding better memory categorization
- improving retrieval quality
- adding tests
- creating a more polished dashboard
- adding user authentication
- supporting export/import of memories

## Hacktoberfest dev post

This project is my Hacktoberfest contribution: SecondMind — a local-first personal AI memory assistant. The idea behind this project is simple but powerful: help users keep track of meaningful personal context without sending everything to the cloud.

I built this using Django, SQLite, and Ollama so that the app can remember important facts, retrieve the most relevant memories, and respond with context-aware conversations. It is a practical project for exploring AI memory systems, retrieval workflows, and local-first app design.

The project is still open to improvement, and I hope to keep adding features that make it more useful, polished, and beginner-friendly for contributors. Hacktoberfest is a great opportunity to build, learn, and collaborate on ideas that can become real-world tools.

## License

This project currently does not include a formal license file. If you plan to share or distribute it publicly, consider adding a license such as MIT.

## Acknowledgements

- Django
- Ollama
- Open-source contributors and the Hacktoberfest community

