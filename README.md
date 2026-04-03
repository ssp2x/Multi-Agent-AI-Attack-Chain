# 🤖 EP11 — Multi-Agent AI Attack Chain

> **⚠️ LAB / EDUCATIONAL USE ONLY — Authorized environments only. Unauthorized use is illegal.**

A multi-agent AI pipeline that simulates a full penetration testing workflow using GPT-4o. Three specialized agents work in sequence — each passing structured context to the next — to produce a complete professional pentest report.

---

## 🏗️ Architecture

```
Agent 1 (Recon Planner)
        │
        ▼  [structured recon JSON]
Agent 2 (Surface Analyst)
        │
        ▼  [A1 + A2 JSON context]
Agent 3 (Report Writer)
        │
        ▼
  final_report.md
```

| Agent | Role | Output |
|-------|------|--------|
| **Agent 1** | Recon Planner | Passive + active recon methodology, tools, commands |
| **Agent 2** | Attack Surface Analyst | Vulnerability mapping, MITRE ATT&CK, CVSS scores |
| **Agent 3** | Report Synthesizer | Full professional pentest report (Markdown) |

---

## 📁 Files

```
├── agent_chain.py        # Main 3-agent GPT-4o chain
├── chain_visualizer.py   # Terminal visualization of chain results
├── setup.sh              # Dependency installer
├── .env                  # API key template (do NOT commit real keys)
└── multi_agent_chain/    # Generated outputs (auto-created)
    ├── agent1_output.json
    ├── agent2_output.json
    ├── final_report.md
    └── full_chain_results.json
```

---

## ⚙️ Setup

### 1. Run setup script

```bash
bash setup.sh
```

This installs the `openai` Python library and creates the output directory.

### 2. Set your OpenAI API key

**Mac / Linux:**
```bash
export OPENAI_API_KEY='sk-...'
```

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-...
```

**PowerShell:**
```powershell
$env:OPENAI_API_KEY='sk-...'
```

Get your API key at: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

> ⚠️ Never commit your real API key to GitHub. The `.env` file is a template only.

### 3. Run the agent chain

```bash
python3 agent_chain.py
```

### 4. Visualize results (optional)

```bash
python3 chain_visualizer.py
```

---

## 🔧 Configuration

Inside `agent_chain.py`, you can switch the model:

```python
MODEL = "gpt-4o"        # Best quality (default)
# MODEL = "gpt-4o-mini" # Cheaper option
```

Before running, update the `target` dict in `main()` with **your own lab's details**:

```python
target = {
    "name":           "YourLabTarget",           # e.g. "VulnLab-WebApp-01"
    "type":           "Web Application Server",  # target type
    "scope":          "Isolated lab VM",         # scope description
    "ip_range":       "YOUR_LAB_IP_HERE",        # e.g. "192.168.x.x"
    "known_services": ["HTTP/80", "HTTPS/443"],  # known open services
    "authorization":  "Lab environment only",
}
```

> Each user must supply their own authorized lab IP. No default IP is provided.

---

## 📊 Sample Output

After running, you'll get:

- **`agent1_output.json`** — Recon plan with passive/active steps, tools, and commands
- **`agent2_output.json`** — Vulnerability assessment with CVSS scores and MITRE IDs
- **`final_report.md`** — Full pentest report including executive summary, findings, attack chain narrative, and remediation roadmap
- **`full_chain_results.json`** — Complete chain data with timestamps

Terminal summary example:
```
[!] Critical: 2   High: 1   Medium: 1
GPT-4o chain complete. All outputs saved.
```

---

## 🛡️ Blue Team Takeaway

> **Break 1 link → entire chain fails.**
> Block Agent 1 recon → Agent 2 incomplete → No report.

This demo is designed to help **defenders** understand how automated attack chains work so they can build better detection and response strategies.

---

## ⚖️ Legal & Ethics

- ✅ Use only in **authorized lab/CTF environments**
- ✅ For **educational and defensive security** purposes only
- ❌ Unauthorized use is **illegal** under cybersecurity laws
- ❌ Do **not** run against systems you don't own or have explicit written permission to test

---

## 📦 Requirements

- Python 3.x
- `openai` Python library (`pip install openai`)
- OpenAI API key with GPT-4o access
