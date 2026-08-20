# 内置 LaTeX 论文模板（默认骨架）

用途：赛制没有提供官方论文模板时，把本目录复制为工作区的 `paper/`，
作为 LaTeX 默认输出骨架。复制后：

1. 在 `paper/sections/` 写入 `restatement.tex`、`analysis.tex`、
   `assumptions.tex`、`symbols.tex`、`q1.tex`…`q5.tex`、
   `robustness.tex`、`evaluation.tex`、`appendix.tex`；
2. 在 `paper/refs.bib` 填真实参考文献；
3. 填写中英文摘要、关键词和标题；
4. 编译：`xelatex main && bibtex main && xelatex main && xelatex main`。

规则：

- 若赛制提供官方模板，必须优先使用官方模板，本文件仅作无官方模板时的默认骨架；
- 没有官方模板时，直接用本模板出 LaTeX，不停下等模板，也不默认回退 Markdown；
- 符号表使用 `longtable`，与 `planning/symbol_table.md` 保持一致；
- 代码只出现在附录，正文禁止代码块；
- 参考文献必须真实，禁止编造。
