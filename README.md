# LocalAI — Sovereign On-Premise Agentic AI Workbench

LocalAI is a self-hosted, air-gapped agentic AI workbench built for organizations that handle confidential knowledge work — refineries, PSUs (Public Sector Undertakings), defense manufacturing units, and government offices — where sending data to a third-party cloud AI service is not an option.

The entire system runs on your own infrastructure. Model inference, document processing, and code execution all happen inside your network boundary, with no dependency on external APIs.

---

## Why LocalAI

Most AI copilots route your documents, code, and internal data through a cloud provider's servers. For regulated or classified environments, that's a non-starter. LocalAI solves this by pairing a Python automation layer with **Ollama**, a closed, locally-hosted model runtime:

- **Zero external calls** — every inference request stays on `localhost` / your internal network. There is no outbound path to a third-party AI vendor for LocalAI to leak through.
- **Closed-loop model serving** — Ollama loads open-weight models directly onto your hardware. There's no API key, no telemetry callback, and no vendor endpoint in the request path, so there's no channel for a data breach to travel through.
- **Data never leaves the premises** — documents, prompts, and generated outputs are processed and stored locally. This makes LocalAI suitable for air-gapped or network-isolated deployments.
- **Verifiable, not just claimed** — the built-in network audit monitor continuously proves this guarantee rather than asking you to trust it blindly.

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                   Sovereign Web Workbench                │
│                  (localhost:8000, Python)                │
├─────────────────────────────────────────────────────────┤
│  Task Router  →  Local Model Layer (Ollama, closed)      │
│  RAG Engine   →  Local Vector Store                      │
│  OCR Pipeline →  PyMuPDF / Pytesseract / OpenCV / PIL     │
│  Doc Generator→  .docx / .xlsx / .pptx                    │
│  Code Sandbox →  Isolated execution + safety checks       │
│  Network Audit→  Real-time egress monitor (0 external)    │
└─────────────────────────────────────────────────────────┘
```

Python is the automation backbone throughout — it orchestrates task routing, drives the ingestion and OCR pipelines, generates deliverables, and manages the sandboxed execution environment.

## Key Features

### Local Model Routing
Automatically routes tasks to the right local open-weight model served through Ollama:
- `llama3.1:latest` — general reasoning and drafting
- `qwen2.5-coder:7b` — code generation and review
- `mightykatun/qwen2.5-math:7b` — quantitative/technical calculations
- `llama3.2:latest` — lightweight general tasks
- `phi3:latest` — fast, low-resource inference

Because Ollama is a closed, self-contained runtime, model weights and inference execution stay entirely on-device — there's no round trip to a cloud model provider for any of these routes.

### Multimodal & OCR
- PDF text extraction for digital-native documents
- Scanned PDF page rendering via **PyMuPDF**
- OCR via **Pytesseract**, **OpenCV**, and **PIL** for scanned/image-based documents

### Local RAG Knowledge Base
On-premise vector embedding and document ingestion for SOPs, technical manuals, and internal knowledge — indexed and queried entirely within your local environment, so sensitive procedural documents never need to be uploaded anywhere.

### Deliverable Generation
Automated compilation of business-ready outputs:
- `.docx` — Approval Notes
- `.xlsx` — Inspection Matrices
- `.pptx` — Board Decks

### Code Execution Sandbox
Isolated execution environment for running and testing generated code, with automated tests and safety assertion checks before any output is trusted or surfaced.

### Network Sovereignty Guarantee
A real-time network audit monitor that continuously verifies **zero external cloud AI calls** are made — turning "your data stays private" from a policy statement into something you can watch and confirm live.

## Security & Data Privacy

- **No cloud dependency**: Ollama runs models locally, so there is no external API in the loop that could be compromised, subpoenaed, or breached.
- **Air-gap ready**: designed to run on networks with no internet egress at all.
- **Auditable by design**: the network monitor gives a continuous, real-time record of outbound traffic (or the lack of it), so compliance teams can verify sovereignty rather than take it on faith.
- **Local storage only**: documents, embeddings, and generated deliverables are written to disk on your own infrastructure.

## How to Run

Launch the application via the terminal:

```bash
localai start
```

Or using Python directly:

```bash
python localai.py start
```

Then access the Sovereign Web Workbench at:

```
http://localhost:8000
```

## Requirements

- Python 3.x
- [Ollama](https://ollama.com) installed locally, with the models listed above pulled (`ollama pull llama3.1:latest`, etc.)
- PyMuPDF, Pytesseract, OpenCV, and PIL for the OCR pipeline

---

*Built for environments where "the model never left the building" isn't a nice-to-have — it's the whole point.*
