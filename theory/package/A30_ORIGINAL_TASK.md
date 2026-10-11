# A30 — Strong-TAP Open Theory Research
## Maxwell-Observable, Material-Representable Stratified Priors for Electromagnetic Inverse Scattering

**任务：独立理论研究 + 现有证据裁决 + 至多三个决定性实验 specification。**
**不是：默认训练大模型、扩大当前候选 bank、继续 OM/current selection，或重复 E1 的六步 TV。**

## 0. 数据和前置条件

先认真读取冻结 GitHub 材料，不能只从下方数字推断；区分 2D scalar TM 与未来 3D vector Maxwell 的证明范围。

- A29（主入口）：https://github.com/migodam/a29-material-hypothesis-coverage/blob/5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4/A29_DECISION.md
- A29 结果 `results/a29/COVERAGE_GATE.json`、`COVERAGE_CASES.csv`、`COVERAGE_CANDIDATES.csv`、`src/a29/proposals.py`、`research/delegated/a29_audit/COVERAGE_FAILURE_ATTRIBUTION.md`。
- A29 Release： https://github.com/migodam/a29-material-hypothesis-coverage/releases/tag/a29-v0.1.0 ，包含 `A29_RAW_EVIDENCE.zip` 的全部候选及 offline truth 数组。
- A28： https://github.com/migodam/a28-maxwell-material-information/blob/c7819fa142bb70f9920835e8e91ba145f15ed8e3/E1_DECISION.md ，理论 `theory/a28/A28_RESEARCH_REPORT_ZH.md`。
- A27 commit `325cc8a5f99d686ce1b1570296f94b0df1e90141`；A26 commit `2603f3bd16c48e48587fedc4363975779def17f5`；A25 commit `59d8cc57c9da99ccb7978febc308193c43d6f3e5`，这些项目可通过 A29 的 README / source manifest 追溯。
- 如可访问 A12/A17 论文、报告和代码，核对 frozen-GN exact update-space / current-exchange theorem 的所有假设，不要把 local GN step improvement 写成 nonlinear reconstruction superiority。

### 既有证据，作为待审查的实验事实

1. **A27**：online feedback 后处理在复杂材料上物质收益小，仍然有明显 data residual gain；约 96.2% 材料剩余误差落在当地定义的 weak spectral subspace，约99.97%数据梯度位于 strong directions。后两项不证明 Bayesian 不可恢复。
2. **A28-E1**：复杂三家族 full F 6-step TV 相对 N3 的 paired material improvement **1.01%**，CI **[-0.76%,2.57%]**；F 相对 L 6-step **0.40%**，CI跨零；全 F 数据残差改善 **27.33%**；smooth 家族正向改善 **16.23%**。固定结构反事实多数在 F 下可分，在 L 下亦可分；L-on-F 错判很大部分可由**事后使用 F 候选响应的中心/中点校准**解释，校准不是可部署结果。当前有限 bank 的 posterior ESS≈1，κ moment identity 数值成立但材料增益为负；实际 BP 的固定候选白化判别能量大部分保留。A28 历史发生至少807/768状态的预算违例，不得抹去。
3. **A29**：完整新 pool 实际每 case 58–91 个（平均67.625），复杂三家族 hard offline oracle 对 N3 **+2.1468%**，CI [1.2755%,3.1322%]；合法12-candidate 小池 **+2.0919%**；simple-only +1.3639%，geometry/template-only -1.9097%，不能通过预冻结10% coverage gate。smooth 的 full oracle **+55.78%**，其8/8条件由 TRAIN template 获胜，复杂家族0/24由 template 获胜。2688 two-level contrast recipes 因 median=peak=1.2 全部去重，固定相位数据生成限制了结论适用范围。A29 **新增full-wave 0/512，未运行任何F vs calibrated-L selection**，亦未训练网络、未打开 locked test。
4. **A29.1 诊断（注意证据级别）**：已从仓库公开 `fixed_material_comparators_plot_data.csv` 逐像素重算四个 metadata 固定 weak-background 示例：在仅包含 N3、full-pool hard oracle、small-pool hard oracle 三张图像的 convex hull 上，shell hard/convex +0.1235%/+0.1235%，asymmetric +0.5079%/+0.5079%，mixed-scale +0.2123%/+0.2123%，smooth +68.2414%/+74.4672%（相对各自 N3 的 material-L2）。smooth 最佳配比约 N3 0.09231 / full 0.68651 / small 0.22118，额外降低 hard Oracle L2 约19.60%。**这不是所有候选的 convex hull，不是32条件统计，也不是 Maxwell 选择结果。** 完整 A29.1 需从 Release 原数组执行 `a29_1_convex_diagnostic.py`，产生 `A29_1_CASES.csv`、`A29_1_SUMMARY.json`、`A29_1_DECISION.md`。若尚未执行，必须显式标记 FULL A29.1 NOT_RUN；不得把四例写成最终门槛。

## 1. 核心科学问题（请允许推翻本任务框架）

**What class of material representations can simultaneously (i) approximate complex topology/quantitative contrast, (ii) make the Maxwell-measurable degrees of freedom inferable, (iii) regularize truly weak directions through justified prior information, and (iv) admit affordable inference?**

研究的本体不是“如何找最好生成器”，而是 **representation capacity × Maxwell identifiability × decision risk**。

物理固定基准：

\[
L_\chi=I-M_\chi G,\quad c_s=M_\chi(e_s^{\rm inc}+Gc_s),\quad F_s(\chi)=Sc_s.
\]

求解域为合法被动复材料，需区分固定相位 synthetic regime 与独立实虚对比度、未知background/gains的真实情形。若证明需要额外条件，必须逐一列出。

## 2. 几何对象：真的应该叫“流形”吗？

首先检验单一光滑低维流形假设是否与 shell、多连通空腔、component birth/death、尖角、piecewise contrast 相矛盾。考虑：

\[
\mathcal M=\bigcup_{\tau\in\mathcal T}\mathcal M_\tau,
\quad \chi=D_\tau(z_\tau,q),
\]

其中 \(\tau\) 表示 topology/物理类型，\(z_\tau\) 连续几何坐标，\(q\) 材料定量参数；对 topology jump 使用跨层 finite secants，而非强行使用同一 tangent chart。比较（不要未经实验预选）：SDF/level set + piecewise material，multiscale sparse wavelets + topology atoms，mixture/atlas of local charts，injective flow/VAE material manifold，训练中断开的 material-only decoder，Gaussian/random field prior。

须解释 A29 的 geometry/template coverage FAILURE，并给出可度量的 *representation bias*，不是只画网络框图。

## 3. 必须亲自推导 / 检查反例的理论问题

**T1. 表示和识别之间的定量分解。** 定义 \(e_{\mathcal M}(\chi)=\inf_{u\in\mathcal M}\|u-\chi\|_W\)。如果 \(\mathcal M\) 是并集而不是一个 smooth manifold，解释 topology 跨层的 coverage、训练有限样本泛化和 nearest-chart 偏差；建立具有噪声和近似误差项的 reconstruction error bound，严格区分 *hard candidate oracle*、\(\operatorname{conv}(\mathcal C)\) oracle、continuous-chart oracle、true posterior Bayes risk。验证 convex hull 混合可能是非流形/非期望拓扑的材料。

**T2. Full-wave restricted secant identifiability。** 由 Maxwell 方程导出导数
\[
J_\chi[\delta\chi]=S L_\chi^{-1}M_{e_\chi}\delta\chi
\]
（源分辨张量和复实微分要正确）以及 finite-secant identity
\[
F(\chi_2)-F(\chi_1)=SL_{\chi_2}^{-1}M_{\chi_2-\chi_1}e_{\chi_1}.
\]
定义噪声白化的全局/分层受限割线常数，并严格讨论它和局部 \(J_\chi D'(z)\) 的差异、有限幅度非线性、高对比 resonance / reciprocity / passivity、低维先验如何改善条件性而不是创造数据。是否存在可检测且低成本的 witness 支持某个 topology transition？寻找反例：局部 rank 满但跨 topology 同像；full F/linear L 分别 rank 好但候选均偏离真值；先验能通过相关性恢复 local weak modes。

**T3. 几何上正确的 material-information / design metric。** \(H_z=D'(z)^*J_\chi^*\Sigma_n^{-1}J_\chi D'(z)\) 与 latent 度量、parameterization invariance、material risk \(W\)、prior covariance 的结合。避免仅以数据 FIM trace 或场残差定义“有用信息”。提出可用于 sensor/frequency selection 或训练采样的决策指标，并给出何时这些指标与Bayes material risk一致、不一致的数学条件。

**T4. Maxwell-conditioned conditional risk。** 材料 posterior mean 与 Maxwell data-consistency solution 通常不重合；source-resolved current/field covariance \(\kappa\) 的闭合恒等式仅在真实非退化 posterior 才可能有材料价值。设计能被驳倒的 conditional risk 测试，而不是制造一个训练目标来验证本理论。

**T5. One-anchor calibrated linearization。** 审计 \(\widetilde F(\chi)=F(\hat\chi)+L(\chi)-L(\hat\chi)\) 的绝对 forward bias、finite secant error、likelihood ranking error 的可估上界；不能把使用任意候选 F 真值的事后校准伪装为单锚点可部署算法。给出 F 相对该 baseline 真正必要的充分条件/反例和成本界。

**T6. 可靠的小样本先验。** TRAIN仅64 independent parents；训练和验证不能把同parent的noise/background看成独立几何。比较 topology/geometry parameter model vs 64样本学大型 flow/diffusion 的显式风险。对未知相位、sensor noise/clock/gain和3D vector Maxwell 的扩展只给条件，不声称已有验证。

## 4. 文献与 novelty audit（必须查 2026 新论文）

先认真核查至少：
- Khorashadizadeh et al. **Deep Injective Prior for Inverse Scattering**, IEEE TAP 2023, DOI 10.1109/TAP.2023.3312818（已经做 material manifold prior、MAP/posterior sampling）。
- Sun et al. **Latent Manifold Projection for Plug-and-Play Generative Priors in Electromagnetic Inverse Scattering**, IEEE TAP 2026 Early Access, DOI 10.1109/TAP.2026.3722905（已经做 learned manifold + alternating physics/projection）。
- SOM/TSOM/SOM-Net 原始算法和2025–2026 physics-guided score/diffusion/flow；goal-oriented Bayesian inverse problems、Bayesian experimental design、restricted secant/RIP、multilevel set/shape reconstruction 经典文献。

明确列出 **已有结论 / 小变体 / 可能真正新 / 不成立**。单纯“物理迭代+投影到流形”“CNN加physics loss”“把反馈嵌入diffusion”不能作为新颖贡献。

## 5. 最小数值验证设计：控制实验优先

先完成 0 full-wave 的 A29.1 完整候选 hull 诊断（若 Release 数据可用）；报告32 case、12 complex parents paired CI、full vs small hull Oracle、L MAP/mean（不是校准 posterior）、edge/IoU/topology、数值优化 KKT。若 hull 仍不能改善，必须承认 finite candidate family 的边界并转研究 continuous/stratified representation。

之后只设计至多三项可证伪实验，其中第一项应尽量不训练或只有极小 TRAIN-only 表示拟合：
1. **Coverage and topology audit**：同参数量、同TRAIN64、同开发集比较手工物理几何 atlas、稀疏wavelet、level set 和小decoder；offline truth Oracle仅测表达能力，不能用于生成在线候选。候选/局部优化的参数量、真实多连通支持与contrast自由度分开报告。
2. **Restricted secant and prior-vs-data audit**：对真正能表达结构的材料状态估计F/L/one-anchor校准模型的白化 finite-secant 材料判别、tangent singular values、cross-topology ambiguity；生成/验证噪声独立，不把多pair当多parent。
3. **Minimal recovery pilot, ONLY IF 1–2 positive**：measurement-only material inference，BP+ordinary learned/handcrafted prior 为强对照；Full F必须在材料质量与成本上胜过单锚点 calibrated L，主指标复杂三家族 material ΔNRMSE、edge、support，完整 inference wall-time；不能只看 residual。

预算 RTX4060 8GB；不启动大规模训练或GPU campaign，先提供精确 experiment protocol/GO–NO-GO gates，且所有真实 Maxwell fixture、失败和预处理均预约计费。locked test 新协议冻结前禁止打开。

## 6. 结果输出与最终裁决

产出：
1. 一份中文主理论报告（专业英文术语保留）及公式推导，明确数学假设、定理/反例/proof sketch、与 A12–A29 的对应关系，重点比较三种最强研究路线。
2. 一份不超过三个实验的复现级 specification，包含对照、数值阈值、统计单元、最大计算预算、终止条件。
3. 单独一段 **Strong-TAP novelty verdict**：哪条路线值得做、哪条退役、哪些命题已被既有论文覆盖；若不足以形成原创理论，必须明确 NO-GO。不要用宏大架构替代可证明机制。

**先检查事实与理论缺口，再构建研究假设；绝不预设“流形+Maxwell”一定会成功。**
