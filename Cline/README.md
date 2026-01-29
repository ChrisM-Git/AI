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

Prerequisites

VS Code

Cline extension

Node.js installed

Prisma AIRS API key & profile

