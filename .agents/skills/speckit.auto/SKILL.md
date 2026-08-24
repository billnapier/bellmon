---
name: speckit.auto
description: Autonomous end-to-end pipeline execution of a feature specification (spec.md -> plan.md -> tasks.md -> implementation -> code review -> fix loop -> tests -> validation -> git push -> pull request) using subagents with zero manual intervention.
version: 1.3.0
depends-on:
  - speckit.plan
  - speckit.tasks
  - speckit.implement
  - speckit.reviewer
  - speckit.tester
  - speckit.validate
---

## Role

You are the **Antigravity Autonomous Subagent Orchestrator**. Your role is to take an approved feature specification (`specs/[feature]/spec.md`), check out the feature branch, and execute the complete SDD pipeline end-to-end using isolated subagents for each phase: planning, task breakdown, code implementation, adversarial code review, automated fixing, test verification, status tracking update, git commitment, branch pushing, and automated Pull Request creation.

> [!CRITICAL]
> **IRONCLAD AUTOMATION RULE**: You MUST execute ALL 7 PHASES sequentially without stopping early. Stopping after code generation or unit testing without staging, committing, pushing, and opening a Pull Request is a STRICT PROTOCOL VIOLATION.

---

## Mandatory Phase Checklist & Execution Sequence

When executing `speckit.auto`, you MUST follow and verify all 7 phases in sequence:

```
[ ] Phase 0: Branch Checkout & Verification
[ ] Phase 1: Planning (plan.md, research.md, data-model.md, quickstart.md)
[ ] Phase 2: Task Breakdown (tasks.md)
[ ] Phase 3: Builder & Implementation (Source code + tests)
[ ] Phase 4: Adversarial Code Review (code_review.md)
[ ] Phase 5: Fixer & Feedback Remediation (Apply review fixes)
[ ] Phase 6: Test Execution & Validation (pytest test suite)
[ ] Phase 7: Git Commit, Push & PR Creation (git add/commit/push + GitHub PR)
```

---

## Detailed Phase Requirements

1. **Phase 0: Branch Checkout & Verification**
   - Check out or verify git feature branch (`[number]-[short-name]`).
   - Confirm `specs/[feature]/spec.md` exists and is complete.

2. **Phase 1: Planning Subagent (`speckit.plan`)**
   - Subagent Context: Generates `plan.md`, `research.md`, `data-model.md`, and `quickstart.md` inside `specs/[feature]/`.

3. **Phase 2: Task Breakdown Subagent (`speckit.tasks`)**
   - Subagent Context: Generates `tasks.md` grouped by user stories and implementation phases.

4. **Phase 3: Builder Subagent (`speckit.implement`)**
   - Subagent Context: Executes all tasks in `tasks.md`, writing source code, configuration, and unit test files.

5. **Phase 4: Adversarial Reviewer Subagent (`speckit.reviewer`)**
   - Subagent Context: Scans all generated git diffs against security, spec acceptance criteria, code quality, and edge-case handling rules.
   - Deliverable: Generates `specs/[feature]/code_review.md` with explicit approval status (`APPROVE` or `NEEDS_REVISION`).

6. **Phase 5: Fixer Subagent (`speckit.implement`)**
   - Subagent Context: If `code_review.md` flags any issues or recommendations, immediately update the code to resolve all feedback items.

7. **Phase 6: Tester Subagent (`speckit.tester` & `speckit.validate`)**
   - Subagent Context: Runs the full pytest test suite (`/home/napier/a/bellmon/.venv/bin/pytest`) and verifies all acceptance criteria are met.

8. **Phase 7: Git Lifecycle, Status Update & Pull Request Creation (MANDATORY EXIT GATE)**
   - Subagent Context:
     - Update `specs/STATUS.md` to reflect 100% completion of the feature and updated overall project completion percentage.
     - Stage all new/modified files (`git add .`).
     - Commit with conventional commit message (`git commit -m "feat([feature]): ..."`).
     - Push feature branch to origin (`git push -u origin [feature-branch]`).
     - Create Pull Request into `main` using GitHub CLI (`gh pr create --fill`) or GitHub MCP tool (`mcp_github-mcp-server_create_pull_request`).
     - **REQUIRED FINAL RESPONSE**: Report the live GitHub Pull Request URL and full pipeline execution summary to the user.

---

## Anti-Patterns & Guardrails

> [!WARNING]
> **PREVENTING FORGOTTEN STEPS**:
> - ❌ **NEVER STOP AFTER TESTS PASS**: Passing tests (Phase 6) is NOT the end of `speckit.auto`. You MUST proceed directly to Phase 7.
> - ❌ **NEVER SKIP CODE REVIEW**: `specs/[feature]/code_review.md` MUST be generated before testing and committing.
> - ❌ **NEVER LEAVE UNCOMMITTED CHANGES**: Run `git status` in Phase 7 to verify zero untracked or unstaged files remain.
> - ❌ **NEVER RETURN WITHOUT A PR URL**: Any response ending `speckit.auto` that lacks a Pull Request link is incomplete.

