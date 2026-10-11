# A29.1 Saved-pool convex capacity diagnosis

**Exploratory, exposed development only. These are OFFLINE convex Oracles, not deployable Maxwell decisions.**

Cases 32, independent parents 16, new Maxwell states 0.

| Method | Complex relative gain vs N3 | 95% parent-bootstrap CI |
|---|---:|---:|
| full_hard_oracle_nrmse | 2.147% | [1.311%, 3.058%] |
| small_hard_oracle_nrmse | 2.092% | [1.219%, 3.020%] |
| full_convex_oracle_nrmse | 13.122% | [11.510%, 14.646%] |
| small_convex_oracle_nrmse | 7.640% | [6.394%, 8.950%] |
| full_L_MAP_nrmse | -3.324% | [-5.700%, -1.075%] |
| small_L_MAP_nrmse | -3.324% | [-5.700%, -1.075%] |
| full_L_mean_nrmse | -3.315% | [-5.703%, -1.081%] |
| small_L_mean_nrmse | -3.315% | [-5.704%, -1.082%] |

## Scientific status
If full convex Oracle still has low coverage, stop finite saved-bank line.
If full convex Oracle improves but L mean does not, this is a selection/information problem.
If L mean succeeds, validate on a new untouched cohort before any full Maxwell spend.
Do NOT retroactively reopen A29 NO_GO; full F has not been run in A29.
All material weights with sum 1 preserve pointwise convex material bounds, but not discrete topology.
All confidence intervals are exploratory: the same 16 development parents have been repeatedly examined.
