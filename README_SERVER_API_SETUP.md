# Remote Server API Architecture (Ollama)

## The Objective
To execute massive data generation runs without hitting paid API quotas (e.g., Google Gemini's 250 requests/day limit), we converted our private Linux GPU server (`cs-aiwk2-pc`) into a free, open API endpoint. 

This architecture allows the local Mac to act as the "Orchestrator" (running the Python scripts, managing the files, and parsing the logic) while silently beaming the heavy LLM inference tasks across the network to the server's massive Nvidia GB10 Blackwell GPU.

## The Setup Guide

### Step 1: Open the Server Port
By default, Ollama is locked to `localhost` (127.0.0.1). To allow the Mac to send requests, you must restart Ollama on the server and tell it to listen to all network interfaces (`0.0.0.0`).

If Port 11434 is blocked by another user or a ghost process, you can easily spin up a custom port (e.g., 11437):
```bash
# Run this on the Linux GPU Server
OLLAMA_HOST=0.0.0.0:11437 ollama serve
```

### Step 2: Download the "Teacher" Model
While the server is running, ensure you have pulled the massive open-source model you want to use as your AI engine. We used Qwen due to its strict adherence to formatting:
```bash
ollama pull qwen2.5:72b-instruct
```

### Step 3: Point the Mac to the Server
On the local Mac laptop, open the `GraphGen-v.1/.env` file. We use the `openai_api` backend because Ollama has native OpenAI compatibility, which entirely bypasses any bugs in custom Ollama Python wrappers.

Update the `.env` to look exactly like this:
```env
# Bypass Google/OpenAI and point to our private server
SYNTHESIZER_BACKEND=openai_api
SYNTHESIZER_MODEL=qwen2.5:72b-instruct
SYNTHESIZER_BASE_URL=http://100.64.54.72:11437/v1
SYNTHESIZER_API_KEY=dummy-key
```

### The Result
When you run `bash run_partition.sh` on the Mac, it seamlessly sends the GraphRAG communities to the server. The server's Blackwell GPU processes the data at maximum utilization (~46GB VRAM, 96% Compute) and beams the generated Q&A flashcards directly back to the Mac's hard drive!