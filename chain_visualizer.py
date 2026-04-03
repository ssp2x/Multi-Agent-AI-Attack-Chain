#!/usr/bin/env python3
"""
chain_visualizer.py
Reads the saved JSON outputs and draws a visual chain summary in terminal.
Run this AFTER agent_chain.py finishes.
"""

import json
import os
import sys
from datetime import datetime

RESET  = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
RED    = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; PURPLE = "\033[95m"; CYAN = "\033[96m"; WHITE = "\033[97m"

BASE = "/home/claude/multi_agent_chain"

def load(filename):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def box(title, lines, color, width=66):
    print(f"\n{color}{BOLD}┌{'─'*(width-2)}┐")
    print(f"│  {title:<{width-4}}│")
    print(f"├{'─'*(width-2)}┤{RESET}")
    for line in lines:
        # pad or truncate to fit
        display = line[:width-4]
        print(f"{color}│{RESET}  {display:<{width-4}}{color}│{RESET}")
    print(f"{color}└{'─'*(width-2)}┘{RESET}")

def arrow(label="context passed"):
    print(f"\n{'':>20}{YELLOW}{BOLD}{'▼':^10}{RESET}")
    print(f"{'':>18}{DIM}{label:^14}{RESET}")
    print(f"{'':>20}{YELLOW}{BOLD}{'▼':^10}{RESET}\n")

def main():
    print(f"\n{CYAN}{BOLD}{'═'*66}")
    print(f"  EP11 — MULTI-AGENT CHAIN VISUALIZER")
    print(f"  Reading saved agent outputs...")
    print(f"{'═'*66}{RESET}\n")

    a1    = load("agent1_output.json")
    a2    = load("agent2_output.json")
    chain = load("full_chain_results.json")

    if not all([a1, a2, chain]):
        print(f"{RED}[!] Run agent_chain.py first to generate outputs.{RESET}")
        sys.exit(1)

    # ── Agent 1 box ──────────────────────────────────────
    a1_lines = []
    passive       = a1.get("passive_recon", {})
    active        = a1.get("active_recon",  {})
    passive_steps = passive.get("steps", [])[:3]
    passive_tools = passive.get("tools", [])[:5]
    active_cmds   = active.get("commands", [])[:2]

    a1_lines.append("Passive Recon Steps:")
    for s in passive_steps:
        a1_lines.append(f"  • {s[:58]}")
    a1_lines.append("")
    a1_lines.append(f"Tools: {', '.join(passive_tools)[:56]}")
    a1_lines.append("")
    if active_cmds:
        a1_lines.append("Sample commands:")
        for cmd in active_cmds:
            a1_lines.append(f"  $ {cmd[:58]}")
    a1_lines.append("")
    ctx = a1.get('next_agent_context', '')[:44]
    a1_lines.append(f"next_agent_context: {ctx}")

    box("🔍  AGENT 1 — RECON PLANNER", a1_lines, PURPLE)
    arrow("recon JSON →")

    # ── Agent 2 box ──────────────────────────────────────
    a2_lines = []
    vectors  = a2.get("attack_vectors", [])
    sev_map  = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

    a2_lines.append(f"Attack Vectors Found: {len(vectors)}")
    a2_lines.append("")
    for v in vectors[:5]:
        sev   = v.get("severity", "?").lower()
        icon  = sev_map.get(sev, "⚪")
        name  = v.get("name", "Unknown")[:32]
        mitre = v.get("mitre_id", "")
        cvss  = v.get("cvss_score", "")
        a2_lines.append(f"  {icon} {name:<33} {mitre}  CVSS:{cvss}")

    a2_lines.append("")
    top = a2.get("top_priority", "")[:50]
    a2_lines.append(f"Top Priority: {top}")
    a2_lines.append("")
    ctx2 = a2.get('next_agent_context', '')[:44]
    a2_lines.append(f"next_agent_context: {ctx2}")

    box("💣  AGENT 2 — SURFACE ANALYST", a2_lines, RED)
    arrow("A1 + A2 JSON →")

    # ── Agent 3 box ──────────────────────────────────────
    report_path = os.path.join(BASE, "final_report.md")
    report_text = ""
    if os.path.exists(report_path):
        with open(report_path) as f:
            report_text = f.read()

    word_count = len(report_text.split()) if report_text else 0
    line_count = len(report_text.splitlines()) if report_text else 0

    sections_found = []
    for sec in ["Executive Summary", "Detailed Findings", "Attack Chain", "Remediation", "Conclusion"]:
        if sec.lower() in report_text.lower():
            sections_found.append(sec)

    a3_lines = [
        f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Words: {word_count}   |   Lines: {line_count}",
        "",
        "Sections found in report:",
    ]
    for s in sections_found:
        a3_lines.append(f"  ✓ {s}")
    a3_lines.append("")
    a3_lines.append("Output: final_report.md  +  full_chain_results.json")

    box("📋  AGENT 3 — REPORT SYNTHESIZER", a3_lines, GREEN)

    # ── Chain stats ───────────────────────────────────────
    print(f"\n{CYAN}{BOLD}{'─'*66}")
    print(f"  CHAIN EXECUTION SUMMARY")
    print(f"{'─'*66}{RESET}")

    ts = chain.get("run_timestamp", "")
    print(f"  {WHITE}Run timestamp :  {CYAN}{ts}{RESET}")
    print(f"  {WHITE}Agents ran    :  {GREEN}3 / 3  ✓{RESET}")
    print(f"  {WHITE}Total vectors :  {RED}{len(vectors)}{RESET}")

    critical = sum(1 for v in vectors if v.get("severity","").lower() == "critical")
    high     = sum(1 for v in vectors if v.get("severity","").lower() == "high")
    print(f"  {WHITE}Critical      :  {RED}{critical}{RESET}")
    print(f"  {WHITE}High          :  {YELLOW}{high}{RESET}")
    print(f"  {WHITE}Report file   :  {DIM}final_report.md{RESET}")

    print(f"\n{CYAN}{'═'*66}{RESET}\n")
    print(f"{GREEN}{BOLD}  🛡️  BLUE TEAM TAKEAWAY:{RESET}")
    print(f"  Break 1 link → entire chain fails.")
    print(f"  Block Agent 1 recon → Agent 2 incomplete → No report.\n")

if __name__ == "__main__":
    main()
