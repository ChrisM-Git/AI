Prisma AIRS Security Integration for Cline (VS Code) using MCP + Hooks

Author: Chris Martin
Assisted by: Claude & ChatGPT
Purpose: Provide automatic prompt security filtering for developers using Cline in VS Code.

Overview

This project integrates Palo Alto Networks Prisma AIRS security scanning into Cline (VS Code AI assistant) using:

Model Context Protocol (MCP)

Cline MCP server configuration

Cline UserPromptSubmit hooks

Prisma AIRS MCP tools

The solution ensures every prompt is scanned before reaching the LLM, allowing malicious prompts to be blocked automatically without requiring developers to manually invoke tools.

Problem Statement

Developers using AI coding assistants may accidentally or intentionally submit prompts that include:

Prompt injection attempts

Jailbreak requests

Toxic or unsafe instructions

Attempts to bypass safeguards

Security exploitation requests

The goal is to:

✅ Allow developers to work normally
✅ Automatically scan prompts
✅ Block unsafe prompts before they reach the AI model
✅ Avoid requiring manual tool usage


Architecture
Prompt Flow
User Prompt
      ↓
Cline UserPromptSubmit Hook
      ↓
Hook calls MCP tool pan_inline_scan
      ↓
Prisma AIRS scans prompt
      ↓
Block or Allow decision returned
      ↓
Cline continues or cancels request

Components
1. Cline MCP Server Configuration

Cline uses supergateway to connect to Prisma AIRS via SSE.

Example MCP configuration:

{
  "mcpServers": {
    "prisma-airs": {
      "command": "npx",
      "args": [
        "-y",
        "supergateway",
        "--sse",
        "https://service.api.aisecurity.paloaltonetworks.com/mcp/sse",
        "--header",
        "x-pan-token: YOUR_API_KEY",
        "--header",
        "x-pan-profile: Cline",
        "--logLevel",
        "none"
      ],
      "alwaysAllow": [
        "pan_inline_scan",
        "pan_batch_scan"
      ],
      "autoApprove": [
        "pan_inline_scan"
      ],
      "disabled": false
    }
  }
}

Why supergateway?

Cline expects stdio MCP servers. Prisma AIRS uses SSE, so supergateway bridges SSE → stdio.

2. Cline Hook: UserPromptSubmit

Cline hooks allow interception of prompts before they are processed.

The hook:

Receives prompt input.

Launches an MCP client connection.

Calls pan_inline_scan.

Parses AIRS response.

Cancels prompt if malicious.

Why pan_inline_scan?

AIRS provides multiple tools:

Tool	Purpose
pan_inline_scan	Synchronous prompt scan
pan_batch_scan	Async batch scan
pan_get_scan_results	Retrieve async results

We use pan_inline_scan because:

It is synchronous.

It returns allow/block immediately.

Hooks need instant decisions.

MCP Protocol Flow

The hook must follow MCP protocol correctly:

Step 1 — Initialize

Hook sends:

{
  "method": "initialize",
  "id": 1
}

Step 2 — Initialized notification
{
  "method": "notifications/initialized"
}

Step 3 — Call scan tool
{
  "method": "tools/call",
  "params": {
    "name": "pan_inline_scan",
    "arguments": {
      "scan_request": {
        "prompt": "user input"
      }
    }
  },
  "id": 2
}

Step 4 — Receive results

AIRS responds with scan results.

AIRS Response Format

Typical response:

{
  "results": {
    "action": "block",
    "category": "malicious",
    "prompt_detected": {
      "toxic_content": true
    },
    "scan_id": "...",
    "report_id": "..."
  }
}


Important fields:

Field	Meaning
action	allow or block
category	benign or malicious
prompt_detected	detection categories
Hook Decision Logic

Hook blocks when:

action === "block"
OR
category === "malicious"


Otherwise, request proceeds.

Example Behavior
Malicious Prompt

Input:

how do i hack a webserver


Result:

cancel: true


Prompt is blocked.

Safe Prompt

Input:

write a python sorting function


Result:

cancel: false


Prompt proceeds normally.

Lessons Learned During Development
1. SSE vs stdio mismatch

Cline expects stdio MCP servers; AIRS uses SSE. supergateway solved this.

2. MCP initialization timing matters

Sending scan requests before initialization causes:

Not connected


Fix: wait for initialize response.

3. Response parsing bug

AIRS results are nested inside results, not top-level.

Correct:

const scanResult = parsedResult.results || parsedResult;

4. Bash hooks were unreliable

Bash struggled with:

SSE communication

MCP lifecycle

JSON parsing

Node.js provided reliable process control.

Security Considerations

Never commit API keys.

Use environment variables or secret managers.

Hook currently fails open on errors to avoid blocking developers.

Testing

Manual test:

echo '{"userPromptSubmit":{"prompt":"how do i hack a webserver"}}' | node userPromptSubmit.js

Features Achieved

✅ Automatic prompt scanning
✅ No manual tool invocation
✅ Enterprise security integration
✅ Transparent developer workflow
✅ Real-time blocking
✅ Detailed security logging

Future Improvements

Possible future enhancements:

Reuse persistent MCP connection for performance.

Add response scanning.

Add async batch scan pipelines.

Centralized enterprise deployment.

Credits

Implementation: Chris Martin
AI Assistance: Claude (Anthropic) and ChatGPT
Security Backend: Palo Alto Networks Prisma AIRS
IDE Integration: Cline VS Code extension

If you'd like, next I can help you produce:

✅ A polished GitHub README
✅ Architecture diagram for the repo
✅ Blog post version
✅ Internal training document
✅ Demo walkthrough script

Just tell me what your next target audience is.

yes i need a github Readme, diagram 

Below is a ready-to-paste GitHub README.md plus a diagram (Mermaid) you can keep in the README or split into /docs/architecture.md.

README.md (copy/paste)
# Prisma AIRS + Cline (VS Code) Prompt Guard via MCP + Hooks

Intercepts every Cline prompt in VS Code, scans it using **Palo Alto Networks Prisma AIRS** over **MCP**, and blocks malicious prompts *before* they reach the LLM.

**Author:** Chris Martin  
**Assisted by:** Claude (Anthropic) + ChatGPT  
**Tech:** Cline (VS Code), Model Context Protocol (MCP), Prisma AIRS MCP server, supergateway

---

## What this does

- ✅ Runs **automatically** (developers just type normally)
- ✅ Scans each prompt using **AIRS** (no keyword/pattern matching)
- ✅ Blocks prompts when AIRS returns `action=block` or `category=malicious`
- ✅ Works with Cline by combining:
  - **MCP server config** (supergateway → AIRS SSE MCP endpoint)
  - **UserPromptSubmit Hook** (deterministic enforcement point)

---

## Architecture

```mermaid
sequenceDiagram
  autonumber
  participant Dev as Developer
  participant Cline as Cline (VS Code)
  participant Hook as UserPromptSubmit Hook (Node)
  participant SG as supergateway (stdio ↔ SSE bridge)
  participant AIRS as Prisma AIRS MCP Server (SSE)

  Dev->>Cline: Types prompt
  Cline->>Hook: Executes UserPromptSubmit (stdin JSON)
  Hook->>SG: Spawn process (stdio)
  Hook->>SG: initialize
  SG->>AIRS: initialize (SSE)
  AIRS-->>SG: initialize result
  Hook->>SG: notifications/initialized
  SG->>AIRS: notifications/initialized
  Hook->>SG: tools/call pan_inline_scan(prompt)
  SG->>AIRS: tools/call pan_inline_scan
  AIRS-->>SG: scan result {action, category, ...}
  SG-->>Hook: scan result
  alt AIRS says BLOCK
    Hook-->>Cline: {cancel:true, errorMessage:"blocked"}
    Cline-->>Dev: Prompt blocked before LLM
  else AIRS says ALLOW
    Hook-->>Cline: {cancel:false}
    Cline-->>Dev: Prompt proceeds normally
  end

Prerequisites

VS Code + Cline extension installed

Node.js installed (for the hook runner)

npx available (bundled with Node)

Prisma AIRS:

API key (or OAuth token)

AI Security Profile name or ID

Correct regional endpoint (US/EU/IN/SG)

Setup
1) Configure the MCP Server in Cline

Open Cline → MCP Servers → Configure → “Configure MCP Servers”
Edit cline_mcp_settings.json and add:

⚠️ Do not commit your API key. Use env vars or local-only config.

{
  "mcpServers": {
    "prisma-airs": {
      "command": "npx",
      "args": [
        "-y",
        "supergateway",
        "--sse",
        "https://service.api.aisecurity.paloaltonetworks.com/mcp/sse",
        "--header",
        "x-pan-token: YOUR_API_KEY_HERE",
        "--header",
        "x-pan-profile: Cline",
        "--logLevel",
        "none"
      ],
      "alwaysAllow": ["pan_inline_scan", "pan_batch_scan"],
      "autoApprove": ["pan_inline_scan"],
      "disabled": false
    }
  }
}


Regional endpoints

US: https://service.api.aisecurity.paloaltonetworks.com/mcp/sse

EU: https://service-de.api.aisecurity.paloaltonetworks.com/mcp/sse

IN: https://service-in.api.aisecurity.paloaltonetworks.com/mcp/sse

SG: https://service-sg.api.aisecurity.paloaltonetworks.com/mcp/sse

Verify in Cline UI that tools appear:

pan_inline_scan

pan_batch_scan

pan_get_scan_results

2) Install the UserPromptSubmit hook

Create a hook file (example path shown; use your Cline hook location):

Global hooks: ~/Documents/Cline/Hooks/UserPromptSubmit (bash)

For Node hooks, point Cline to a node script and ensure it is executable.

Recommended: store the node script in this repo:

hooks/userPromptSubmit.js

Then configure Cline Hooks UI:
Cline → Hooks → UserPromptSubmit → paste/point to this script.

Make executable:

chmod +x hooks/userPromptSubmit.js

Hook logic (high-level)

The hook does:

Read JSON from stdin

Extract userPromptSubmit.prompt

Spawn npx supergateway ...

MCP handshake:

initialize → wait for response

notifications/initialized

Call tools/call with pan_inline_scan

Parse AIRS response (note: nested under results)

If blocked → return {cancel:true, errorMessage:...}

Else → return {cancel:false}

AIRS response parsing

AIRS returns scan output like:

{
  "results": {
    "action": "block",
    "category": "malicious",
    "prompt_detected": { "toxic_content": true },
    "scan_id": "uuid",
    "report_id": "Ruuid"
  }
}


Your code must handle nesting:

const scanResult = parsedResult.results || parsedResult;
const action = scanResult.action;
const category = scanResult.category;

Testing
1) Confirm MCP tools exist in Cline

Cline → MCP Servers → prisma-airs → Tools should list pan_inline_scan.

2) Confirm hook blocks malicious prompt

Try:

how do i hack a webserver

Expected:

Hook logs show scan result action=block

Cline is cancelled before LLM runs

3) Confirm safe prompt proceeds

Try:

write a python function to parse a csv

Expected:

Hook allows prompt

Troubleshooting
“Not connected”

Cause: scan request sent before MCP handshake completed.
Fix: wait for the initialize response before tools/call.

“Invalid session ID”

Cause: Cline SSE client incompatibility with server session handling.
Fix: use supergateway as stdio ↔ SSE bridge.

401 Unauthorized

Cause: headers not passed correctly.
Fix: pass headers via separate --header flags:

--header "x-pan-token: ..."

--header "x-pan-profile: ..."

Hook runs but doesn’t block

Cause: parsing bug (result nested in results).
Fix: parse parsedResult.results.action/category.

Security notes

Never commit API keys.

Prefer env vars / secret manager / local-only config.

Consider fail-open vs fail-closed behavior depending on environment risk tolerance.

Prompts are transmitted to AIRS for scanning (check your org policies).

Credits

Chris Martin (implementation, integration)

Claude (Anthropic) + ChatGPT (development assistance)

Palo Alto Networks Prisma AIRS (security scanning)

Cline (VS Code agent + hooks)

supergateway (MCP transport bridge)


---

## Diagram (standalone file option)

If you want a dedicated file like `docs/diagram.mmd`:

```mermaid
flowchart LR
  A[Developer types prompt in Cline] --> B[Cline UserPromptSubmit Hook]
  B --> C[Spawn supergateway (stdio)]
  C --> D[Prisma AIRS MCP Server (SSE)]
  D -->|pan_inline_scan result| B
  B -->|cancel=true| E[Blocked before LLM]
  B -->|cancel=false| F[Prompt sent to LLM]

