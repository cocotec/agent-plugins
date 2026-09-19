# Cocotec agent plugins

This is a plugin marketplace containing plugins to integrate the [Popili](https://cocotec.io/popili) language and MCP
servers into coding agents, enabling them to typecheck, navigate and formally verify Coco programs.

| Plugin        | Channel                     |
| ------------- | --------------------------- |
| `popili`      | Stable releases             |
| `popili-beta` | Beta and release candidates |

Install only one as both channels declare the same MCP and language server names.

## Install

```bash
# Claude Code
claude plugin marketplace add cocotec/agent-plugins
claude plugin install popili@cocotec

# Codex CLI
codex plugin marketplace add cocotec/agent-plugins
codex plugin add popili@cocotec

# GitHub Copilot CLI
copilot plugin marketplace add cocotec/agent-plugins
copilot plugin install popili@cocotec
```

The plugin runs `popili`, so it needs the Popili CLI on your `PATH`; get it from
[cocotec.io/downloads](https://cocotec.io/downloads/). Under Claude Code you can point at a specific file with
`POPILI_PATH` instead.

| Client          | MCP | LSP                                 |
| --------------- | --- | ----------------------------------- |
| Claude Code     | ✅  | ✅                                  |
| Codex           | ✅  | n/a — Codex has no LSP support      |
| GitHub Copilot  | ✅  | ✅                                  |

Each plugin ships both an [Agent Plugins 1.0](https://agent-plugins.org/specification) manifest and
a Claude Code one.
