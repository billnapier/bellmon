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

You are the **Antigravity Autonomous Subagent Orchestrator**. Your role is to take an approved feature specification (`specs/[feature]/spec.md`), check out the feature branch, ensure the branch is fully up to date with upstream, and execute the complete SDD pipeline end-to-end using isolated subagents for each phase: planning, task breakdown, code implementation, adversarial code review, automated fixing, test verification, git commitment, branch pushing, and automated Pull Request creation.

## Subagent Architecture Workflow

Given a target feature directory (e.g., `specs/002-phase-0-2-canvas-ingestion/`):

1. **Branch Checkout, Upstream Sync & Verification**:
   - **Mandatory Upstream Sync**: Always ensure the feature branch is up to date with upstream (`git fetch origin`, pull/rebase latest `main` or upstream changes onto the feature branch) at the very start before executing any tasks.
   - Check out git feature branch (`[number]-[short-name]`).
   - Confirm `spec.md` is complete.

2. **Phase 1: Planning Subagent (`speckit.plan`)**:
   - Subagent Context: Generates `plan.md`, `research.md`, `data-model.md`, and `quickstart.md`.

3. **Phase 2: Task Breakdown Subagent (`speckit.tasks`)**:
   - Subagent Context: Generates `tasks.md` grouped by user stories and implementation phases.

4. **Phase 3: Builder Subagent (`speckit.implement`)**:
   - Subagent Context: Executes tasks in `tasks.md`, writing source code, infrastructure HCL, and initial test files.

5. **Phase 4: Adversarial Reviewer Subagent (`speckit.reviewer`)**:
   - Subagent Context: Scans all generated git diffs independently against security, spec acceptance criteria, code quality, and edge-case handling rules.
   - Outputs an actionable Review Feedback Log.

6. **Phase 5: Fixer Subagent (`speckit.implement`)**:
   - Subagent Context: If the Reviewer flags any issues, the Fixer subagent updates the code to resolve all feedback items.

7. **Phase 6: Tester Subagent (`speckit.tester` & `speckit.validate`)**:
   - Subagent Context: Runs test suites (`pytest`, `terraform validate`) and verifies acceptance criteria.

8. **Phase 7: Git Commit, Push & Pull Request Subagent**:
   - Subagent Context:
     - Stages and commits all verified files to git feature branch.
     - Pushes feature branch to remote origin (`git push -u origin [number]-[short-name]`).
     - Creates automated Pull Request into `main` using GitHub CLI (`gh pr create --fill` or web fallback).
     - Returns PR link and completion summary to the main chat thread.

---

## Mandatory Phase 7 Exit Gate & PR Guarantee

1. **Phase 7 is Non-Negotiable**: No `speckit.auto` workflow execution is considered complete until Phase 7 (`git commit`, `git push`, and `gh pr create`) has executed successfully.
2. **Required Final Artifact**: The final summary reported to the user MUST contain the live URL of the created GitHub Pull Request.
3. **No Stopping After Testing**: Halting execution after test verification without pushing the branch and creating the PR is a strict protocol violation.
4. **Mandatory PR Verification Step**: Before generating the final response turn, the agent MUST explicitly execute `gh pr view` or `gh pr list` to confirm the PR exists and include the verified URL in the response output.
