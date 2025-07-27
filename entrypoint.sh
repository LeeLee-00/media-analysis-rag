#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Retrieve llama3.2-vision model..."
ollama pull llama3.2-vision:11b
echo "🟢 Done!"
echo "🔴 Retrieve llama3 model..."
ollama pull llama3:8b
echo "🟢 Done!"


# Wait for Ollama process to finish.
wait $pid