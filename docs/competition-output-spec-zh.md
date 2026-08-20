# 数模竞赛输出规范（完整打包文档）

> 面向数学建模竞赛的成品输出契约。目标是把「论文必须诚实、完整」这句话翻译成全流程可检查的规则：能力验收、建模假设、代码与结果、图表、最终论文合规。
>
> 配套技能：`capability-contract-builder`、`output-standards-auditor`，以及 `model-assumptions-builder`、`figure-table-planner`、`robustness-checker`、`model-code-analyzer` 和两个代码评审器中增强的规则。

## 1. 目的

竞赛队伍翻车，多数不是因为不会模型，而是流程缺陷：

- 题目要的是 X，队伍做成了 Y；
- 论文里写了一个数字，仓库里没有任何脚本产出过它；
- 截止前修了 bug，论文里却还是旧数字；
- 图规划了没生成，或生成了没嵌入；
- 摘要写在结果之前，于是只能编数值。

本规范的存在，就是让上面每一种失败都能被机械地检测出来。它从不替人做建模判断，只把一条声明所需的证据变得显式、可查。

## 2. 工作区产物契约

每个产物只有一个权威路径。同一文件出现两份，就会产生版本漂移。

| 阶段 | 产物 | 最低要求 | 消费方 |
|---|---|---|---|
| 解析 | `planning/parse/problem_parse.json` | 结构完整 | 分类、假设、方法卡 |
| 分类 | `planning/classification/problem_classification.json` | 结构完整 | 能力合同、方法筛选 |
| 能力合同（可选） | `planning/capability_checklist.json` | 结构完整 | 假设、代码计划、评审、论文 |
| 符号表 | `planning/symbol_table.md` | 非空 | 所有建模/写作步骤 |
| 假设 | `planning/model_assumptions.md` | 非空 | 方法卡、探针、稳健性 |
| 方法 | `methods/Qx/qx_method_card.md` | 非空 | 代码计划、评审、写作 |
| 决策账本 | `methods/Qx/qx_decisions.jsonl` | 追加式 | 每道 gate |
| 风险探针 | `methods/Qx/probes/risk_probe_summary.json` | 7 个字段 | G2 |
| 代码计划 | `code/Qx/qx_code_plan.md` 或 `code/matlab/Qx/...` | 非空 | 生成器、评审 |
| 评审 | `code/Qx/reviews/qx_<lang>_review.json` | 5 项命名检查（可加 `capability_contract`） | G3 |
| 运行 | `results/Qx/experiments/roundN/run_summary.json` | 非空 | 结果报告、稳健性、写作 |
| 稳健性 | `robustness/Qx/qx_robustness_summary.json` | 非空 | G4 |
| 冻结 | `results/Qx/reports/frozen_numbers.json` | 不可手改 | 写作、全部审计 |
| 论文 | `paper/main.tex` + `paper/sections/*.tex` | 主文件 ≥ 5KB、章节 ≥ 3 | 编译、审计 |
| 输出审计 | `paper/audits/output_spec_report.md` | 命名检查 | G6 前置 |

防止静默失败的命名规则：

- 图名必须以 `fig_` 或 `tikz_` 开头；不带前缀的名字对账时会静默漏掉；
- 每问结果统一 `figures/problem_N_results.json`，汇总为 `figures/all_results.json`；
- 历史版本（`results_v1.json`、`results_old.json`）必须清掉，不得与当前文件并存；
- `data_raw/` 只读，清洗后的数据放 `data_clean/`。

## 3. 能力合同

参数密集型题目（约 20 条以上可量化条件）或含多项可验证能力的题目，应构建 `planning/capability_checklist.json`：

```json
{
  "schema_version": 1,
  "problem_id": "2026A",
  "n_subproblems": 4,
  "capabilities": [
    {
      "id": "Q2-C1",
      "subquestion": "Q2",
      "name": "硬约束进入求解器",
      "judge": "machine",
      "criterion": "题面声明的容量/预算/时间窗约束属于优化模型的一部分",
      "machine_check": "constraint",
      "falsifiable_check": "约束在求解器模型内部声明（非事后配平），且最终解满足全部约束；任何越界即判不成立",
      "source_sentence": "S7"
    }
  ]
}
```

规则：

- 写「题目真正要求的能力」，不是「你打算做的事」；
- 能被确定性闸机核验的写 `machine`，否则写 `semantic`；
- 每条 semantic 项和非 delivery 的 machine 项都必须有代码真能证伪的 `falsifiable_check`；
- 题面每个「决策/目标/机制」句都要被至少一条能力项的 `source_sentence` 认领；
- 每个子问题至少拆 1 条能力项；
- 清单不是摆设：建模认领 ID，代码计划写 `validate_capability()` 断言，评审跑 `capability_contract` 检查，论文只能声明已通过的能力。

## 4. 建模加固

### 假设预检

在定稿假设前，用最简单子问题快速验算：

1. 列出所有模糊表述，每条至少给出两种合理解释；
2. 对影响最大的 1–2 个歧义点，把两种解释各算一遍（手算/表格/几行代码）；
3. 检查问题递进性：后续子问题必须对新约束/资源产生可见响应；如果结果几乎不变，说明假设可疑；
4. 记录选定解释、被否解释和理由。

如果选择会改变队伍能声明什么，用一张选择卡请人拍板，不要静默定案。

### 升级机制处理

当题面暗含对经典模型的升级（可充电 → 多趟路径；时间窗 → 访问时刻区间；鲁棒性 → 多场景对比）：

1. 逐条审视解析/分类中所有升级提示；
2. 默认采用——可实现机制不是可选项；
3. 只有给出理由才能拒绝：物理/业务不可行、数据矛盾、或求解规模限制并给出明确误差上界。

缺参数不是跳过理由。做法是：做出显式且有理有据的假设 → 写入假设清单 → 标记进灵敏度分析。若采用简化版升级，必须保留其核心机制并说明简化了什么。

## 5. 代码与结果规则

### 反降维

实现必须兑现获批方法，而不是换成更好写的替代品：

- 禁止用 ID/文件名/行号当标签（代理标签）；
- 禁止用同一批数据派生的特征预测由该数据派生的标签（循环论证）；
- 禁止用字符串/词频匹配冒充语义能力；
- 禁止只打分不执行声称的下游动作；
- 每条 `falsifiable_check` 都变成运行时断言，不过即中断；删断言、降阈值蒙混过关属于违规。

能力真做不到时，走人类决策路径降级声明——绝不允许用代码注释掩盖。

### 数据自检

全精度结果照常写盘，但智能体只读摘要：

- 禁止 `Read`/`cat` 整个结果 JSON；
- 审计脚本用全精度重算，只输出结论：`PASS`/`FAIL`、越界数、最大误差、最多 5 条越界定位；
- 图与表必须由落盘数据生成，禁止画图脚本里硬编码数字。

### 约束闭环审计

存在硬约束时：

1. 从最终结果文件重算全部约束——不信任优化器自报的 `constraints_ok`；
2. 用同一脚本审计所有对比基线；自动扫描含 `baseline`、`naive`、`greedy`、`就近`、`等权`、`不调整`、`lower_bound` 的键，漏审即 FAIL；
3. 违反约束的基线要么修好，要么在论文中显式标注「不可行/仅作理论下界」；
4. 留下凭证：

```text
<!-- AUDIT_OK source=results.json rechecked_at=<timestamp> n_constraints=N -->
```

无硬约束时记录 `n_constraints=0` 并附一句话说明，而不是省掉凭证。

## 6. 图表清单（FIGURE_MANIFEST）

每张规划图都要注册进机器可读区块，让生成与审计能把「规划」和「产物」逐条对账：

```text
<!-- BEGIN FIGURE_MANIFEST -->
**Data figures**
- fig_q2_residual_diag [4-panel] — 残差诊断 — competition#5 — 章节: Q2 验证
- fig_q3_pareto — Pareto 前沿 — competition#8 — 章节: Q3 求解
**TikZ figures**
- tikz_feasible_q2 — 约束可行域 — 章节: Q2 模型
<!-- END FIGURE_MANIFEST -->
```

清单规则：

- ID 一律 `fig_`/`tikz_` 前缀；
- 每条写明具体图表类型、证据来源（配方编号或 `custom`）、目标章节；
- 同一种图表类型最多出现 3 次；
- TikZ 只画按坐标定义的几何结构（可行域、相平面、受力分解、网络拓扑）；函数曲线和分布一律是数据图；
- 组合图显式标注（`[2-panel]`/`[4-panel]`），panel 不超过 4 个且宽度可读；
- 感知/重构类题目，真实样本前后对比图排在指标图之前；
- 数量参考：数据图 12–20 张是竞赛常见区间，3 张为硬底线；按赛题复杂度规划，不凑数。

## 7. 论文输出规范

### 输出格式

- 默认用 LaTeX 输出：`paper/main.tex` + `paper/sections/*.tex` +
  `paper/refs.bib`，编译为 PDF。
- Markdown 只是中间草稿格式，交接给论文手前必须转成 `.tex`。
- 默认不产出 Word/`.docx`；只有赛制明确要求时才允许生成。
- 赛制提供官方模板时必须使用官方模板；没有官方模板时，用内置
  `templates/paper/` 骨架创建 `paper/main.tex` 并继续。不得停下来等模板，
  也不得把 Markdown 当作最终交付物。

### 结构

竞赛论文保持标准骨架（摘要 → 问题重述 → 假设 → 符号 → 各问建模求解 → 灵敏度/检验 → 评价推广 → 参考文献 → 附录代码）。统计建模论文按内容设计章节，但章名必须具体，核心分析章约占全文 40–50%。

### 摘要

- 摘要最后写，等所有章节和 `RESULTS.md` 就绪；先写摘要等于编数字。
- 每个子问题独占一段；一个自然段内禁止出现两个及以上「针对问题」。
- 摘要里每个数字都必须在正文中原样出现。
- 篇幅参考：多数中文竞赛 400–600 字；统计建模 500–700 字；丰满模式（如华为杯）1500–2200 字、关键词 8–12 个。

### 页数口径

- 统一按 900 中文字符/页估算。
- 只统计 `paper/sections/`；摘要、目录、参考文献、附录代码不计。
- 代码块不进正文（放附录），否则字符估算虚高、实际正文单薄。
- 任何子问题章节低于约 4 页（约 3500 字符）必须扩充。

### 参考文献

- BibTeX 必须真实检索获取，禁止凭记忆编造。
- 首次引用编号全局严格递增；多引用合并必须升序。
- 中文竞赛模板用上标引用，命令随模板走（`\upcite` 还是 `\cite`）。
- 引用 key 用描述式命名（`作者_年份_主题`），元数据未定前加 `TODO__` 前缀。

### 数字可追溯

- 论文中每个关键数字都能在 `frozen_numbers.json` 或当前结果 JSON 里找到。
- 需要约束审计的结果摘要带有 `AUDIT_OK` 凭证。
- 无历史结果文件残留。
- 可疑「完美值」必须给出解释：R²/accuracy > 0.999、误差为 0、p 值 = 0、提升约 10 倍以上。

### 占位符

章节与摘要中不允许残留 `TODO`、`待补充`、`[论文标题]` 等模板哨兵。

## 8. 合规预检

`output-standards-auditor` 在 `submission` 模式下运行以下命名检查，并产出 `paper/audits/output_spec_report.md`：

| 检查项 | 通过条件 |
|---|---|
| `artifact_contract` | 规范文件存在且达到最小体量；命名契约成立；无历史版本残留 |
| `figure_manifest` | 每张规划图存在且已嵌入；没有「已嵌入但磁盘无文件」的图；每条都有类型、来源、章节 |
| `page_estimate` | 单一密度口径；只算正文；正文无代码块；没有过薄的子问题章节 |
| `abstract_format` | 摘要最后写；按问分段；数字与正文一致 |
| `number_traceability` | 数字可溯源到冻结/当前产物；审计凭证齐全；无未解释的完美值 |
| `reference_contract` | 引用真实；首次编号递增；模板引用命令正确 |
| `placeholder_freedom` | 章节与摘要无占位符 |
| `format_compliance` | 匿名、目录、中英摘要、符号表 longtable、中文模板无 `babel[english]`、正文无代码块；赛制规则以当年官方文件为准 |

该报告是前置检查：供 G6 三审计（一致性、完整性、QA）消费，绝不替代它们。`FAILED` 阻断终稿组装。

## 9. 技能落地映射

| 规则 | 技能 |
|---|---|
| 能力清单 | `capability-contract-builder` |
| 假设预检与升级处理 | `model-assumptions-builder` |
| 反降维代码计划 | `model-code-analyzer` |
| `capability_contract` 评审检查 | `python-code-reviewer`、`matlab-code-reviewer` |
| 约束闭环审计 | `robustness-checker` |
| 图表清单 | `figure-table-planner`、`math-figure-generator` |
| 输出前置审计 | `output-standards-auditor` |
| 路由 | `workflow-orchestrator` |

## 10. 边界

- 本规范只做机械检查。它不选方法、不解释数字、不发明贡献；这些都通过决策账本留给人类。
- 赛事的 AI 使用与格式规则逐年变化且各赛不同。提交前务必核对当年官方规则；本仓库不编码任何赛事的权威政策。
- 输出审计通过不等于论文可以提交。G6 三个终审才是最终结论。
