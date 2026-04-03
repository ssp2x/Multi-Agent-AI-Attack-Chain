#!/bin/bash
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  EP11 Multi-Agent Chain — Setup          ║"
echo "║  OpenAI GPT-4o | Lab Use Only            ║"
echo "╚══════════════════════════════════════════╝"
echo ""

python3 --version 2>/dev/null || { echo "[!] Python 3 required."; exit 1; }
echo "[OK] Python 3 found"

echo "[-->] Installing openai library..."
pip install openai --quiet --break-system-packages 2>/dev/null || pip install openai --quiet
echo "[OK] openai installed"

mkdir -p multi_agent_chain
echo "[OK] Output directory ready"

echo ""
echo "[OK] Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set your OpenAI API key:"
echo "     Mac/Linux:   export OPENAI_API_KEY='sk-...'"
echo "     Windows CMD: set OPENAI_API_KEY=sk-..."
echo "     PowerShell:  \$env:OPENAI_API_KEY='sk-...'"
echo ""
echo "  2. Run the agent chain:"
echo "     python3 agent_chain.py"
echo ""
echo "  3. Visualize results:"
echo "     python3 chain_visualizer.py"
echo ""
echo "Get API key: https://platform.openai.com/api-keys"
echo ""
