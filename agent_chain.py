#!/usr/bin/env python3
"""
EP11 — Multi-Agent AI Attack Chain Demo
=======================================
LAB / EDUCATIONAL USE ONLY
Authorized environments only. Unauthorized use is illegal.

Architecture:
  Agent 1 (Recon Planner)   → structured recon methodology
  Agent 2 (Surface Analyst) → attack surface + risk mapping
  Agent 3 (Report Writer)   → full pentest-style report

Uses OpenAI GPT-4o API with streaming.
Each agent receives the previous agent's output as context.
"""

import openai
import json
import time
import sys
import os
from datetime import datetime

# ── ANSI colors ──────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"

# ── Model config ─────────────────────────────────────────────
MODEL = "gpt-4o"          # Best quality + speed balance
# MODEL = "gpt-4o-mini"   # Cheaper option — uncomment to switch

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_agent_chain")

def banner(text, color=BLUE, width=70):
    line = "=" * width
    print(f"\n{color}{BOLD}{line}")
    print(f"  {text}")
    print(f"{line}{RESET}\n")

def section(agent_num, title):
    colors = {1: PURPLE, 2: RED, 3: GREEN}
    c = colors.get(agent_num, CYAN)
    print(f"\n{c}{BOLD}{'-'*60}")
    print(f"  AGENT {agent_num} -- {title}")
    print(f"{'-'*60}{RESET}")

def typing_effect(text, delay=0.012):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def stream_response(client, system_prompt, user_prompt, agent_num):
    """Stream GPT-4o response with real-time output."""
    colors = {1: PURPLE, 2: RED, 3: GREEN}
    color  = colors.get(agent_num, CYAN)

    print(f"{color}{'.'*60}{RESET}")
    print(f"{DIM}Streaming Agent {agent_num} response (GPT-4o)...{RESET}\n")
    print(f"{color}", end='', flush=True)

    full_response = ""

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=1500,
        temperature=0.3,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end='', flush=True)
            full_response += delta.content

    print(f"{RESET}\n")
    print(f"{color}{'.'*60}{RESET}")
    return full_response

def ethics_reminder():
    print(f"\n{RED}{BOLD}{'#'*60}")
    print("  ETHICS REMINDER")
    print("  -------------------------------------------------------")
    print("  * Lab/CTF environments ONLY")
    print("  * Unauthorized use = ILLEGAL (Cyber Security Act 2023)")
    print("  * This demo = educational understanding for DEFENDERS")
    print(f"{'#'*60}{RESET}\n")
    time.sleep(1.5)

def save_output(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"{DIM}[OK] Saved: {path}{RESET}")

def parse_json_response(raw, agent_num):
    """Robust JSON parsing — handles GPT markdown fences."""
    clean = raw.strip()

    # Strip markdown code fences if present
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                clean = part
                break

    try:
        data = json.loads(clean)
        print(f"{GREEN}[OK] Agent {agent_num} JSON parsed successfully{RESET}")
        return data
    except json.JSONDecodeError:
        # Last resort: find JSON object
        import re
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
                print(f"{YELLOW}[~] Agent {agent_num} JSON extracted from response{RESET}")
                return data
            except Exception:
                pass
        print(f"{YELLOW}[~] Agent {agent_num} stored as raw text{RESET}")
        return {"raw_output": raw}

# ============================================================
#  AGENT SYSTEM PROMPTS
# ============================================================

AGENT1_SYSTEM = """You are a senior penetration testing reconnaissance specialist.
You ONLY operate in authorized lab environments.

When given a target, produce a STRUCTURED JSON recon plan with EXACTLY this schema:
{
  "target_summary": "brief description of target",
  "passive_recon": {
    "steps": ["step1", "step2", "step3", "step4"],
    "tools": ["tool1", "tool2", "tool3", "tool4", "tool5"],
    "data_points": ["what to collect 1", "what to collect 2", "what to collect 3"]
  },
  "active_recon": {
    "steps": ["step1", "step2", "step3"],
    "tools": ["nmap", "nikto", "gobuster"],
    "commands": [
      "nmap -sV -sC -p- 192.168.247.136 -T4",
      "nikto -h http://192.168.247.136",
      "gobuster dir -u http://192.168.247.136 -w /usr/share/wordlists/dirb/common.txt"
    ]
  },
  "risk_indicators": ["indicator1", "indicator2", "indicator3"],
  "next_agent_context": "one sentence telling Agent 2 what to focus on"
}

CRITICAL RULES:
- Output ONLY valid JSON
- No markdown code fences (no backticks)
- No explanation text before or after JSON
- Pure JSON only — nothing else"""

AGENT2_SYSTEM = """You are a senior vulnerability assessment specialist.
You ONLY work in authorized penetration testing engagements.

Given a recon report from Agent 1, produce a STRUCTURED JSON assessment:
{
  "attack_surface_summary": "brief overall assessment",
  "attack_vectors": [
    {
      "name": "vulnerability name",
      "category": "Injection|Authentication|Exposure|Misconfiguration|RCE",
      "mitre_id": "T1190",
      "severity": "Critical",
      "cvss_score": 9.8,
      "description": "what it is and why it matters",
      "detection_method": "exactly how blue team detects this in logs/monitoring",
      "defender_action": "specific technical fix or mitigation step"
    }
  ],
  "attack_chain_narrative": "Step by step: how attacker chains findings for maximum damage",
  "top_priority": "single most critical finding name",
  "next_agent_context": "brief summary for Agent 3 report writer"
}

RULES:
- Include 3-5 attack_vectors based on the recon data
- Do NOT provide working exploit code
- Output ONLY valid JSON — no markdown fences, no extra text"""

AGENT3_SYSTEM = """You are a senior penetration testing report writer.
You synthesize multi-agent security data into professional reports.

Given Agent 1 (recon) and Agent 2 (vulnerability assessment) outputs, write a full report:

# PENETRATION TEST REPORT

## Executive Summary
3-4 sentences. Non-technical. For CISO. State total findings, severity counts, business risk.

## Scope & Methodology
What was tested. Recon approach used. Assessment method.

## Risk Summary Table
| Finding | Severity | CVSS | Priority |
|---------|----------|------|----------|
(list all Agent 2 findings, sorted by CVSS descending, P1=Critical, P2=High, P3=Medium)

## Detailed Findings
For EACH attack vector from Agent 2:
### [Finding Name] -- [Severity]
- **Description:** clear explanation
- **Evidence from Recon:** reference specific Agent 1 data
- **MITRE ATT&CK:** technique ID and name
- **Impact:** what attacker achieves if exploited
- **Defender Action:** specific remediation steps

## Attack Chain Narrative
How attacker combines all findings step by step. Use Agent 2 narrative, expand it.

## Remediation Roadmap
### Immediate -- 0-30 Days (Critical)
### Short Term -- 30-60 Days (High)
### Long Term -- 60-90 Days (Medium + Hardening)

## Conclusion
2-3 sentences. Overall posture. Recommended next steps.

Be specific. Be actionable. Reference actual finding names throughout."""

# ============================================================
#  MAIN CHAIN EXECUTION
# ============================================================

def run_chain(target_info, client):

    results = {
        "run_timestamp": datetime.now().isoformat(),
        "model_used": MODEL,
        "target": target_info,
        "agent_outputs": {}
    }

    # ── AGENT 1: RECON PLANNER ────────────────────────────
    section(1, "RECON PLANNER")
    time.sleep(0.5)

    typing_effect(f"  Target: {target_info['name']}", delay=0.015)
    typing_effect(f"  Scope:  {target_info['scope']}", delay=0.015)
    typing_effect(f"  Type:   {target_info['type']}", delay=0.015)
    print()

    agent1_prompt = (
        f"Authorized lab penetration test target:\n"
        f"- Target Name: {target_info['name']}\n"
        f"- Target Type: {target_info['type']}\n"
        f"- Scope: {target_info['scope']}\n"
        f"- IP Range: {target_info['ip_range']}\n"
        f"- Known Services: {', '.join(target_info.get('known_services', ['Unknown']))}\n"
        f"- Authorization: Lab environment only\n\n"
        f"Generate complete reconnaissance plan as JSON."
    )

    agent1_raw  = stream_response(client, AGENT1_SYSTEM, agent1_prompt, 1)
    agent1_data = parse_json_response(agent1_raw, 1)

    results["agent_outputs"]["agent1"] = agent1_data
    save_output(agent1_data, "agent1_output.json")

    print(f"\n{PURPLE}{BOLD}[--->] Agent 1 complete. Passing context to Agent 2...{RESET}")
    time.sleep(2)

    # ── AGENT 2: SURFACE ANALYST ───────────────────────────
    section(2, "ATTACK SURFACE ANALYST")
    time.sleep(0.5)

    agent2_prompt = (
        f"You are receiving reconnaissance data from Agent 1.\n"
        f"Analyze the attack surface based on this recon output.\n\n"
        f"=== AGENT 1 RECON OUTPUT ===\n"
        f"{json.dumps(agent1_data, indent=2)}\n"
        f"=== END AGENT 1 OUTPUT ===\n\n"
        f"Target scope: {target_info['scope']}\n"
        f"Known services: {', '.join(target_info.get('known_services', []))}\n\n"
        f"Produce vulnerability assessment JSON now."
    )

    agent2_raw  = stream_response(client, AGENT2_SYSTEM, agent2_prompt, 2)
    agent2_data = parse_json_response(agent2_raw, 2)

    results["agent_outputs"]["agent2"] = agent2_data
    save_output(agent2_data, "agent2_output.json")

    print(f"\n{RED}{BOLD}[--->] Agent 2 complete. Passing ALL context to Agent 3...{RESET}")
    time.sleep(2)

    # ── AGENT 3: REPORT WRITER ────────────────────────────
    section(3, "REPORT SYNTHESIZER")
    time.sleep(0.5)

    agent3_prompt = (
        f"You are the final stage of a multi-agent pentest pipeline.\n"
        f"Synthesize both outputs into a complete professional report.\n\n"
        f"=== AGENT 1 -- RECON REPORT ===\n"
        f"{json.dumps(agent1_data, indent=2)}\n"
        f"=== END AGENT 1 ===\n\n"
        f"=== AGENT 2 -- VULNERABILITY ASSESSMENT ===\n"
        f"{json.dumps(agent2_data, indent=2)}\n"
        f"=== END AGENT 2 ===\n\n"
        f"Target: {target_info['name']}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        f"Model: {MODEL}\n\n"
        f"Generate the complete penetration test report now."
    )

    agent3_output = stream_response(client, AGENT3_SYSTEM, agent3_prompt, 3)
    results["agent_outputs"]["agent3_report"] = agent3_output

    # Save markdown report
    report_path = os.path.join(OUTPUT_DIR, "final_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Multi-Agent AI Pentest Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {MODEL}\n")
        f.write(f"**Target:** {target_info['name']}\n")
        f.write(f"**Environment:** {target_info['scope']}\n\n---\n\n")
        f.write(agent3_output)
    print(f"{DIM}[OK] Saved: {report_path}{RESET}")

    save_output(results, "full_chain_results.json")
    return results, agent3_output


def main():
    banner("EP11 -- MULTI-AGENT AI ATTACK CHAIN", RED, 70)
    banner(f"MODEL: {MODEL} | FOR EDUCATIONAL / LAB USE ONLY", YELLOW, 70)

    ethics_reminder()

    target = {
        "name":           "VulnLab-WebApp-01",
        "type":           "Web Application Server",
        "scope":          "Isolated lab VM -- educational demo only",
        "ip_range":       "192.168.247.136",
        "known_services": ["HTTP/80", "HTTPS/443", "SSH/22", "MySQL/3306"],
        "authorization":  "Lab environment -- AI Bisoye EP11 demo",
    }

    print(f"{CYAN}{BOLD}Target Configuration:{RESET}")
    for k, v in target.items():
        val = v if not isinstance(v, list) else ', '.join(v)
        print(f"  {DIM}{k:20}{RESET} {WHITE}{val}{RESET}")
    print()
    print(f"{DIM}Model in use: {CYAN}{MODEL}{RESET}\n")

    # ── Get OpenAI API key ──
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print(f"{RED}[!] OPENAI_API_KEY not set.{RESET}")
        print(f"{DIM}")
        print(f"  Mac/Linux :  export OPENAI_API_KEY='sk-...'")
        print(f"  Windows   :  set OPENAI_API_KEY=sk-...")
        print(f"  PowerShell:  $env:OPENAI_API_KEY='sk-...'")
        print(f"{RESET}")
        print(f"  Get API key: https://platform.openai.com/api-keys")
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    print(f"{GREEN}[OK] OpenAI API key loaded{RESET}")
    print(f"{YELLOW}[-->] Starting 3-agent GPT-4o chain...{RESET}\n")
    time.sleep(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_time = time.time()
    results, _ = run_chain(target, client)
    elapsed = time.time() - start_time

    banner("CHAIN COMPLETE -- SUMMARY", GREEN, 70)
    print(f"{WHITE}Model used:       {CYAN}{MODEL}{RESET}")
    print(f"{WHITE}Time elapsed:     {CYAN}{elapsed:.1f}s{RESET}")
    print(f"{WHITE}Agents executed:  {CYAN}3 / 3  [OK]{RESET}")
    print(f"\n{WHITE}Files generated:{RESET}")
    print(f"  {DIM}multi_agent_chain/agent1_output.json{RESET}      -- Recon plan")
    print(f"  {DIM}multi_agent_chain/agent2_output.json{RESET}      -- Vuln assessment")
    print(f"  {DIM}multi_agent_chain/final_report.md{RESET}          -- Full report")
    print(f"  {DIM}multi_agent_chain/full_chain_results.json{RESET} -- All chain data")
    print()

    agent2  = results["agent_outputs"].get("agent2", {})
    vectors = agent2.get("attack_vectors", []) if isinstance(agent2, dict) else []
    if vectors:
        critical = sum(1 for v in vectors if v.get("severity","").lower() == "critical")
        high     = sum(1 for v in vectors if v.get("severity","").lower() == "high")
        medium   = sum(1 for v in vectors if v.get("severity","").lower() == "medium")
        print(f"{RED}[!] Critical: {critical}   {YELLOW}High: {high}   {WHITE}Medium: {medium}{RESET}")

    print(f"\n{GREEN}{BOLD}GPT-4o chain complete. All outputs saved.{RESET}\n")
    ethics_reminder()


if __name__ == "__main__":
    main()
