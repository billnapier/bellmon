# Implementation Plan: Academic & Workload Sentinel

**Branch**: `002-academic-sentinel` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-academic-sentinel/spec.md`

## Summary

The Academic & Workload Sentinel (Bellmon) provides zero-touch automated monitoring for high school academic performance. The implementation ingests REST data from Canvas LMS and PowerSchool SIS, correlates cross-system missing work flags, enforces a mandatory 36-hour grace period on digital submissions to protect student autonomy, alerts on rolling 7-day grade velocity drops ($\ge 4.0\%$), and generates a Sunday evening HTML planning digest highlighting workload clumping ($\ge 2$ major assessments in 48h).

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: `httpx` (async HTTP), `jinja2` (HTML digest templates), `google-cloud-firestore` (state store), `pytest`  
**Storage**: Google Cloud Firestore (or local SQLite for CLI)  
**Infrastructure as Code**: Terraform 1.5+  
**CI/CD Pipeline**: GitHub Actions + Guardian (`https://github.com/abcxyz/guardian`)  
**Testing**: `pytest` (unit & integration)  
**Target Platform**: Google Cloud Run (Scheduled Serverless Container) / Local CLI  
**Project Type**: Single python application / CLI background sentinel  
**Performance Goals**: Complete sync run for enrolled courses within $< 15$ seconds  
**Constraints**: 100% false-positive suppression on paper turned-in work; 36-hour grace period enforcement before P0 parent alerts; 100% IaC declared via Terraform & Guardian deployment  
**Scale/Scope**: Serverless execution per student / observee account  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance Status | Implementation Strategy |
| :--- | :--- | :--- |
| **Principle 1: Student Autonomy & Grace Periods** | PASS | Enforce mandatory 36-hour buffer on `online_upload` missing items before firing parent alert. |
| **Principle 2: Cross-System Noise & False-Positive Elimination** | PASS | Suppress alerts whenever PowerSchool score $> 0$ or `isCollected: true`. |
| **Principle 3: Proactive Grade Velocity Drop Tracking** | PASS | Calculate rolling 7-day $\Delta = \text{Grade}_{t-7} - \text{Grade}_{current} \ge 4.0\%$ and isolate impacting item. |
| **Principle 4: Zero-Touch Push & Digest Delivery** | PASS | Deliver P0 alerts via Pushover / NTFY webhooks and P1 Sunday digest via email. |
| **Principle 5: Workload Clumping Radar** | PASS | Highlight $\ge 2$ major assessments due within 48h window in Sunday HTML digest. |
| **Principle 6: IaC & Automated CI/CD Deployment** | PASS | Define infrastructure using Terraform (`terraform/`) and automate deployment via GitHub Actions + Guardian (`abcxyz/guardian`). |

## Project Structure

### Documentation (this feature)

```text
specs/002-academic-sentinel/
├── plan.md              # Implementation Plan
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # API and JSON contracts
│   └── sync-schema.json
├── checklists/          # Validation checklists
│   └── requirements.md
└── tasks.md             # Actionable task list
```

### Source Code & Infrastructure (repository root)

```text
src/
├── harvesters/          # Canvas & PowerSchool API clients
├── engine/              # Missing work matrix & velocity rules evaluator
├── storage/             # Firestore state store & idempotency ledger
├── router/              # Pushover / NTFY & HTML email dispatchers
└── cli/                 # Command line runner & entry points

terraform/               # Infrastructure as Code (Principle 6)
├── main.tf              # Cloud Run service & Provider config
├── variables.tf         # Environment variables & inputs
├── scheduler.tf         # Cloud Scheduler cron jobs (5 PM weekdays, 6 PM Sun)
├── firestore.tf         # Firestore database & index definitions
├── iam.tf               # Service account bindings & IAM policies
└── outputs.tf           # Terraform output definitions

.github/workflows/       # Automated CI/CD Pipeline (Principle 6)
├── guardian-plan.yml    # PR trigger: Guardian terraform plan & comment
└── guardian-apply.yml   # Merge trigger: Guardian terraform apply

tests/
├── unit/                # Evaluator & harvester unit tests
├── integration/         # Cross-system matrix & grace period integration tests
└── contract/            # Schema validation tests
```

**Structure Decision**: Single Python application layout paired with root `terraform/` IaC definitions and `.github/workflows/` Guardian CI/CD workflows.

## Complexity Tracking

*No constitution violations. System design adheres strictly to all 6 principles.*

