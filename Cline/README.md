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

