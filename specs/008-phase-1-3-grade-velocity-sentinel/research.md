# Research & Technical Decisions: Phase 1.3 Grade Velocity Drop Sentinel

## 1. Historical Snapshot Window Selection

### Problem
Student grade snapshots are recorded daily in Firestore under `CourseState.history` (`date: YYYY-MM-DD`, `percentage`, `letter_grade`). We need to evaluate velocity drop over a $[t-10, t-7]$ day window.

### Solution
- Target baseline window: $[t-10, t-7]$ calendar days prior to evaluation date $t$.
- Primary lookup: Snapshots with date $d$ such that $7 \le t - d \le 10$. If multiple snapshots exist in this range, select the snapshot closest to $t-7$ days (i.e. highest date / most recent within the window).
- Fallback lookup: If no snapshot exists in $[t-10, t-7]$, search $[t-14, t-7]$. Select the snapshot with the largest date $\le t-7$.
- Deferral: If no snapshot exists $\ge 7$ days prior to $t$, the historical baseline is incomplete and evaluation for that course is deferred.

## 2. Delta Calculation Formula

### Formula
$$\Delta = \text{percentage}_{t-\text{prev}} - \text{percentage}_{t-\text{curr}}$$

- Trigger Condition: $\Delta \ge 4.0\%$ (e.g. previous = 93.0%, current = 88.0% $\Rightarrow \Delta = 5.0\% \ge 4.0\%$).
- Precision: Floating point comparisons use standard rounded 2-decimal point precision to avoid floating point representation issues (e.g., `round(prev - curr, 2)`).

## 3. Early-Term Noise Suppression

### Rule
Suppress alerts if `total_graded_points` $< 100$ AND `term_active_days` $< 21$.

### Logic Matrix
| Total Graded Points | Term Active Days | Suppressed? | Reason |
|---|---|---|---|
| 40 (< 100) | 14 (< 21) | YES | Both noise suppression conditions met |
| 150 ($\ge$ 100) | 14 (< 21) | NO | Sufficient point sample ($\ge 100$) |
| 40 (< 100) | 25 ($\ge$ 21) | NO | Sufficient term length ($\ge 21$ days) |
| 150 ($\ge$ 100) | 25 ($\ge$ 21) | NO | Both thresholds satisfied |

## 4. Silent Warming Protocol

### Problem
When a student profile is newly created in the system, historical snapshots do not exist for the past 7 days. Early grade changes during initial sync should not produce velocity drop alerts.

### Solution
- Check the student's total tracking duration (either based on student account registration / `first_synced_at` date or earliest recorded snapshot date).
- If $(\text{current\_date} - \text{tracking\_start\_date}) < 7$ calendar days, the system is in "Silent Warming Mode" and all grade velocity drop alerts are silently suppressed while baselines accumulate.
