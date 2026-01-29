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
