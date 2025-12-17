# Purple Agent (Player0) Performance Summary

## Overview
- **Win Rate**: 85.7%

## Aggregated Metrics (Weighted by Response Count)

| Metric | Mean | Median | Min | Max |
|--------|------|--------|-----|-----|
| **Overall Score** | 0.794 | 0.85 | 0.20 | 0.95 |
| **Action Validity** | 0.953 | 1.00 | 0.00 | 1.00 |
| **Appropriateness** | 0.889 | 0.90 | 0.40 | 1.00 |
| **Clarity** | 0.883 | 0.90 | 0.60 | 1.00 |
| **Completeness** | 0.744 | 0.80 | 0.40 | 1.00 |
| **Creativity** | 0.686 | 0.70 | 0.30 | 0.90 |

## Per-Benchmark Breakdown

### Benchmark 1: custom_eval_2
| Metric | Mean | Median |
|--------|------|--------|
| Score | 0.807 | 0.85 |
| Action Validity | 0.980 | 1.00 |
| Appropriateness | 0.898 | 0.90 |
| Clarity | 0.888 | 0.90 |
| Completeness | 0.751 | 0.80 |
| Creativity | 0.686 | 0.70 |

**Win Rate**: 80%

### Benchmark 2: eval_custom_purple
| Metric | Mean | Median |
|--------|------|--------|
| Score | 0.763 | 0.85 |
| Action Validity | 0.885 | 0.95 |
| Appropriateness | 0.865 | 0.90 |
| Clarity | 0.870 | 0.90 |
| Completeness | 0.725 | 0.75 |
| Creativity | 0.685 | 0.75 |

**Win Rate**: 100%

## Key Insights

1. **Strong Action Validity** (0.953): The purple agent consistently produces valid, executable actions
2. **High Appropriateness** (0.889): Responses are contextually appropriate for the game state
3. **Good Clarity** (0.883): Actions are clearly expressed and understandable
4. **Moderate Creativity** (0.686): Room for improvement in creative/novel strategies
5. **Consistent Winner**: 85.7% win rate against baseline GPT model

## Comparison: Player0 (Purple Agent) vs Player1 (Baseline)

| Metric | Player0 (Purple) | Player1 (Baseline) | Delta |
|--------|------------------|-------------------|-------|
| Score | 0.794 | 0.695 | +0.099 |
| Win Rate | 85.7% | 14.3% | +71.4% |
| Action Validity | 0.953 | 0.841 | +0.112 |
| Creativity | 0.686 | 0.608 | +0.078 |
