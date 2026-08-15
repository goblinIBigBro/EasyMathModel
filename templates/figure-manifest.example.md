# Figure Manifest Example

Append the block below to the figure plan (`methods/Qx/qx_figure_table_plan.md` or the planning document) so downstream generation and the output audit can reconcile plan with products.

```text
<!-- BEGIN FIGURE_MANIFEST -->
**Data figures**
- fig_q1_trend — 多变量时间趋势折线图 — basic#3 — 章节: 问题一数据探索
- fig_q2_residual_diag [4-panel] — 残差诊断（Q-Q/残差-拟合/直方图/时序）— basic#5 — 章节: 问题二模型验证
- fig_q2_pareto — 多目标 Pareto 前沿 — competition#8 — 章节: 问题二求解
- fig_q3_heatmap — 相关系数聚类热力图 — advanced#14 — 章节: 问题三特征分析
- fig_q4_sensitivity — 灵敏度 2×2 组合小图 — custom — 章节: 灵敏度分析
**TikZ figures**
- tikz_feasible_q2 — 线性规划可行域与最优解 — 章节: 问题二模型
- tikz_force_q4 — 受力分解示意 — 章节: 问题四模型
**Tables**
- TABLE_q1_stats — 描述统计表 — 章节: 问题一数据探索
- TABLE_q3_cmp — 多模型指标对比表 — 章节: 问题三模型对比
<!-- END FIGURE_MANIFEST -->
```

Rules:

- every ID starts with `fig_` or `tikz_`; unprefixed names are silently missed by reconciliation;
- every entry names a concrete chart type, an evidence source (recipe ID or `custom`), and a target section;
- the same chart type appears at most three times;
- TikZ is reserved for coordinate-defined geometry (feasible region, phase plane, force diagram, network topology), never for data curves;
- multi-panel figures are explicit (`[2-panel]`/`[4-panel]`), with at most 4 panels;
- perception/reconstruction tasks place a real-sample before/after comparison figure ahead of metric figures.
