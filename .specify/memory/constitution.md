<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (Added Principle 6: IaC & Automated CI/CD Deployment)
- List of modified principles:
  - Added Principle 6: Infrastructure as Code & Automated CI/CD Deployment
  - Updated Governance Section 3: Compliance review to check Principles 1 through 6
- Added sections:
  - Principle 6: Infrastructure as Code & Automated CI/CD Deployment
- Removed sections: None
- Templates requiring updates:
  - ✅ `.specify/memory/constitution.md` updated
  - ✅ `.specify/templates/plan-template.md` (Constitution Check aligns with 6 principles)
- Follow-up TODOs: None
-->

# Bellmon (Bellarmine Monitor) Project Constitution

**Version:** 1.1.0  
**Ratification Date:** 2026-08-20  
**Last Amended Date:** 2026-08-20  

---

## Pre-Amble

This Constitution defines the non-negotiable architectural principles, operational standards, and governance rules for **Bellmon (Bellarmine Monitor)**. All specifications, implementation plans, and tasks MUST adhere strictly to these principles.

---

## Core Principles

### Principle 1: Student Autonomy & Grace Periods
Overdue digital assignments MUST apply a mandatory 36-hour grace period buffer before dispatching push notifications to parents. This window empowers students to self-advocate, submit pending work, or resolve records directly with teachers without immediate parent micro-management.

### Principle 2: Cross-System Noise & False-Positive Elimination
The rule engine MUST cross-reference Canvas LMS submission flags against PowerSchool SIS gradebook records. Physical paper submissions and teacher-graded in-class work MUST be automatically suppressed (i.e. if PowerSchool score $> 0$ or `isCollected: true`), ensuring parents only receive notifications for verified missing items.

### Principle 3: Proactive Grade Velocity Drop Tracking
Alerting MUST NOT wait for formal report cards or end-of-term deficits. The system MUST monitor rolling 7-day course grade trajectories and trigger urgent warnings when a course grade drops by $\ge 4.0\%$, isolating the exact newly entered assignment causing the velocity loss.

### Principle 4: Zero-Touch Push & Digest Delivery
The system MUST operate unattended without requiring parents or students to manually log into portals or check dashboards. All actionable insights MUST be pushed directly to mobile devices via P0 push channels (Pushover / NTFY) or delivered in a scheduled P1 Sunday evening planning digest.

### Principle 5: Workload Clumping Radar
The system MUST analyze forward-looking 7-day schedules to identify workload clumping—defined as $\ge 2$ major assessments (Exams, Projects, Midterms, or points $\ge 50$) due within any rolling 48-hour window—and prominently highlight these clusters in the Sunday digest.

### Principle 6: Infrastructure as Code & Automated CI/CD Deployment
All infrastructure resources MUST be provisioned and managed as code using Terraform. Deployment and environment updates MUST be executed via GitHub Actions CI/CD workflows utilizing Guardian (https://github.com/abcxyz/guardian) for secure, policy-enforced Terraform plan and apply execution.

---

## Governance & Amendment Procedure

1. **Source of Law**: This constitution is the supreme governing document for Bellmon. Any feature specification, architecture design, or pull request violating these principles MUST be rejected or amended.
2. **Amendment Procedure**:
   - Proposed amendments MUST be documented with clear rationale and impact analysis.
   - Version bumps follow Semantic Versioning (`MAJOR.MINOR.PATCH`):
     - **MAJOR**: Backward-incompatible principle removals or redefinitions.
     - **MINOR**: Addition of new principles or major expansion of governance scope.
     - **PATCH**: Typos, wording clarifications, or non-semantic refinements.
3. **Compliance Review**: All implementation plans (`plan.md`) MUST include an explicit "Constitution Check" section verifying alignment with Principles 1 through 6.
