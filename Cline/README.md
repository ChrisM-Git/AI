# Prisma AIRS Prompt Security for Cline (VS Code)

Automatically scans and blocks malicious prompts in Cline using Palo Alto Networks Prisma AIRS via MCP.

**Author:** Chris Martin  
**Assisted by:** Claude (Anthropic) + ChatGPT

---

## Overview

This integration protects developers using Cline by scanning every prompt before it reaches the AI model.

Features:

- ✅ Automatic prompt scanning
- ✅ No manual tool usage required
- ✅ Blocks malicious prompts before LLM execution
- ✅ Transparent developer workflow
- ✅ Uses Prisma AIRS security policies

---

## Architecture

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant Cline as Cline
  participant Hook as UserPromptSubmit Hook
  participant SG as supergateway
  participant AIRS as Prisma AIRS MCP

  Dev->>Cline: Submit prompt
  Cline->>Hook: Execute hook
  Hook->>SG: Start MCP bridge
  SG->>AIRS: pan_inline_scan
  AIRS-->>Hook: Scan result
  alt malicious
    Hook-->>Cline: cancel request
  else safe
    Hook-->>Cline: allow request
  end
```

## Prerequisites

- VS Code
- Cline extension
- Node.js installed
- Prisma AIRS API key & profile

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

Palo Alto Networks Prisma AIRS (security scanning)

Cline (VS Code agent + hooks)

supergateway (MCP transport bridge)


---

