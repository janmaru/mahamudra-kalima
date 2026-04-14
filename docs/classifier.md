# Task Classifier

Kalima classifies each Claude Code turn into one of **13 task categories**. This classification is fully **deterministic** — no LLM calls, no fuzzy matching.

## How Classification Works

For each message, analyze:
1. **Tools used** — read_file, write_file, execute_command, etc.
2. **Keywords in user text** — "refactor", "debug", "test", etc.
3. **Patterns** — file edits + bash runs = testing/debugging

Return the best-matching category.

## 13 Categories

### 1. Coding

**Triggers**:
- Tool: `write_file`, `edit_file`
- Keywords: none required (tools define it)

**What it is**: Any code file creation or modification. Includes variable renames, adding functions, fixing typos.

**One-shot**: High. Either the code works first try or needs a test/debug retry.

### 2. Debugging

**Triggers**:
- Keywords: "debug", "fix", "error", "bug", "crash", "wrong", "issue", "not working"
- **AND** one of: `execute_command`, `read_file`, `write_file`

**What it is**: Responding to broken code. Fix and verify.

**One-shot**: Variable. Depends on issue complexity.

### 3. Feature Dev

**Triggers**:
- Keywords: "add", "create", "implement", "build", "new feature", "capability"
- **AND** tool use (read/write/execute)

**What it is**: Building something new (not fixing). More scope than a quick edit.

**One-shot**: Lower. Features often need iteration.

### 4. Refactoring

**Triggers**:
- Keywords: "refactor", "simplify", "clean", "optimize", "remove", "consolidate", "rename"
- **AND** `write_file`

**What it is**: Improving existing code without changing behavior.

**One-shot**: Medium-high. Refactors are often mechanical.

### 5. Testing

**Triggers**:
- Tool: `execute_command`
- Command contains: `pytest`, `vitest`, `jest`, `test`, `npm test`, `cargo test`, etc.

**What it is**: Running test suites. Verifying code works.

**One-shot**: Not tracked (test turns don't contribute to one-shot rate).

### 6. Exploration

**Triggers**:
- Tools: `read_file`, `grep_code`, `web_search`
- **NO** edits (`write_file`) in same turn

**What it is**: Reading code, searching, researching. Understanding a codebase.

**One-shot**: Not applicable (passive).

### 7. Planning

**Triggers**:
- Tool: `enter_plan_mode`, `task_create`, or explicit plan keywords
- Or: Keywords: "plan", "design", "architecture", "approach", "strategy"
- **AND** no code edits

**What it is**: High-level thinking before implementation. Roadmapping, design docs.

**One-shot**: Not tracked (planning turns are preparation).

### 8. Delegation

**Triggers**:
- Tool: `spawn_agent`, `create_agent`, `run_background_task`

**What it is**: Delegating work to sub-agents or background processes.

**One-shot**: Not tracked (delegated work is counted separately).

### 9. Git Ops

**Triggers**:
- `execute_command` with: `git commit`, `git push`, `git merge`, `git pull`, `git rebase`, `git checkout`

**What it is**: Version control operations.

**One-shot**: Not tracked (deterministic operations).

### 10. Build/Deploy

**Triggers**:
- `execute_command` with: `npm build`, `npm run build`, `docker build`, `pm2`, `docker-compose`, `kubectl`, `terraform`, `npm run deploy`

**What it is**: Building, containerizing, or deploying applications.

**One-shot**: Variable.

### 11. Brainstorming

**Triggers**:
- Keywords: "brainstorm", "what if", "how would", "design", "think about", "consider", "explore idea"
- **NO** tool use (pure text)

**What it is**: Ideation and discussion without code changes.

**One-shot**: Not tracked (conversational).

### 12. Conversation

**Triggers**:
- **NO** tools used
- Pure text exchange

**What it is**: Q&A, explanation, discussion. No code or actions.

**One-shot**: Not tracked (conversational).

### 13. General

**Fallback** for anything else.
- Tool use that doesn't fit categories 1-12
- `skill` tool invocations, MCP servers, uncategorized commands

**One-shot**: Not tracked.

## One-Shot Success Rate

Tracks edit-heavy tasks: **Coding**, **Debugging**, **Feature Dev**, **Refactoring**, **Testing** (in some cases).

**Definition**: Percentage of edits that succeeded without immediate retry.

**Detection**:
```
Pattern: Edit → Run/Test → Edit  = RETRY DETECTED

Pseudo-code:
edit_turns = count(turns with write_file)
retry_turns = count(patterns where Edit → Bash → Edit or Edit → Read → Edit)
one_shot_rate = (edit_turns - retry_turns) / edit_turns * 100
```

**Example**:
```
Turn 1: Edit parser.py          (Coding)
Turn 2: Run pytest              (Testing)
Turn 3: Edit parser.py again    (Coding) ← RETRY
Turn 4: Run pytest              (Testing)
Turn 5: All green               (Conversation)

Edits: 2 turns
Retries: 1 detected
One-shot: 50% (1 success, 1 retry)
```

## Edge Cases

### Multiple categories in one turn

Classify by **primary** activity:
- Edit file + run test = **Coding** (edit takes priority)
- Read file + ask question = **Exploration** (reading is primary)
- Git commit + deploy = **Git Ops** (git takes priority)

### Ambiguous keywords

Example: "refactor the debug logic"
- Keywords: "refactor" (primary) + "debug"
- Trigger: Refactoring (refactor takes priority)

### No tools, no keywords

→ **Conversation**

### Multiple test frameworks

```python
if any(cmd in execute_command for cmd in ["pytest", "vitest", "jest", ...]):
    return "Testing"
```

## Classifier Rules (Pseudocode)

```python
def classify(message: Message) -> str:
    tools = message.tool_uses
    text = message.user_text.lower()
    
    # Check patterns in priority order
    if "write_file" in tools:
        if any(kw in text for kw in ["refactor", "simplify", "rename"]):
            return "Refactoring"
        return "Coding"
    
    if any(kw in text for kw in ["debug", "fix", "error"]):
        if tools:
            return "Debugging"
    
    if any(kw in text for kw in ["add", "create", "implement"]):
        if tools:
            return "Feature Dev"
    
    if "execute_command" in tools:
        if any(test_cmd in message.command for test_cmd in ["pytest", "vitest"]):
            return "Testing"
        if any(cmd in message.command for cmd in ["git commit", "git push"]):
            return "Git Ops"
        if any(cmd in message.command for cmd in ["npm build", "docker build"]):
            return "Build/Deploy"
    
    if any(kw in text for kw in ["plan", "design", "architecture"]):
        if not "write_file" in tools:
            return "Planning"
    
    if "spawn_agent" in tools:
        return "Delegation"
    
    if all(kw in text for kw in ["read_file", "grep"]) and "write_file" not in tools:
        return "Exploration"
    
    if any(kw in text for kw in ["brainstorm", "what if"]) and not tools:
        return "Brainstorming"
    
    if not tools:
        return "Conversation"
    
    return "General"
```

## Extending the Classifier

To add a new category:

1. Define triggers (tools + keywords)
2. Add case in `classifier.py`
3. Add test case in `test_classifier.py`
4. Update this doc

---

See [architecture.md](architecture.md) for overall design.
