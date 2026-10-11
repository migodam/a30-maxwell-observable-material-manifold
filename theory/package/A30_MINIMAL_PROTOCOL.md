# A30 — 最小可证伪实验协议

状态：SPECIFICATION_ONLY。没有启动真实 Maxwell 实验、训练或 locked evaluation。日期：2026-10-10。

本协议与 A29 冻结协议不同。它不改写 A29 NO_GO，也不假定现有四例 hull 诊断代表 32 条件。

## 1. 共同冻结规则

使用 A29 commit `5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4` 的 TRAIN64 和已经暴露的 16 development parents。开发父样本编号为 250065–250080；每 parent 保留 weak/ring 两个原指定条件，共 32。复杂主终点为 shell/asymmetric_piecewise/mixed_scale 的 12 parents，smooth 的 4 parents 单列。任何缺行、失败或背景缺失都保留，不能用剩余成功行凑完整统计。

统计先在每 parent 内平均两背景的材料误差，再计算 `(baseline-candidate)/baseline`，最后等权平均 parent。与原诊断连续性使用 2000 次 parent bootstrap、seed 291011，报告完整 parent gains；所有区间为 exploratory，不是新的独立验证。新实验超参数先写配置再读取评分，不根据某个家族成功与否补跑候选。

数据路径使用白名单，禁止从整个硬盘 glob 搜索 locked payload；缺失缓存必须停止，不调用真实 solver 自动补齐。候选生成、prior 参数和在线动作不可读 truth。离线容量 oracle 与最终评分在独立函数/进程入口读取 truth，并在输出标明 OFFLINE。

共同材料损失包括 Δχ NRMSE、固定质量坐标的平方误差、实虚误差；结构包括原 support IoU、exact four-neighbor edge F1。原支撑阈值为 `0.25*max(abs(truth-background))`，仅离线评分可用。新增 digital topology 使用 4-connected foreground、8-connected background；报告 components、holes、Euler characteristic，以及 0.15/0.25/0.35 三个离线阈值的敏感性。只有 0.25 是原指标的连续性主口径。栅格计数不是连续 topology 证书。

不得以固定增量复相位的训练分布宣称任意复材料泛化。表示可以允许实虚独立变化，但当前标签不能验证独立相位分布的准确恢复。

## 2. 硬预算

目标硬件 RTX4060 8GB；不启动大型网络训练。后两实验合计最多 **512 次真实物理 state-evaluation 调用**，不是 512 个 unique χ：失败、重试、timing repeat、真实 8×8 fixture、不同精度/分辨率实际后端都计入。另记录 unique material states，不能以 LU 缓存抹掉新的 RHS 成本。

分阶段预算：实验一 0；实验二 192；实验三 320。每次调用先预约，再执行；预算耗尽只允许保存证据，不允许以“最后一个 test”绕过。整个提案另建议设置 GPU occupied wall ≤3600 s、host CPU charged time ≤7200 s、complex RHS 总量 ≤16384 的执行上限；这些是本提案的保守资源筛选约定，不是本轮已用资源，也不是性能预测。具体环境导入/启动也计费。

峰值 GPU 内存必须实测；建议 allocated ≤7 GiB，并监控 reserved/process memory 的余量。不得只按矩阵理论大小推断 8GB 必然足够。OOM、原生库失败和验证失败都保留。

缓存已包含完整响应时读取不新增 full-wave state，但加载与运算时间计费。缓存仅有 LU、又计算新的 forward/adjoint RHS 时，按对应动作计费。缺缓存不允许默认 fallback。

## 3. 实验一：完整 hull 与连续表示容量，0 全波

### 3.1 首先完成 A29.1

前置文件：

```
results/a29/OFFLINE_TARGETS.npz
results/a29/COVERAGE_CASES.csv
results/a29/pools/<all 32 case ids>.npz
src/a26/metrics.py   # 原 morphology 实现；缺失须显式标注
```

将原 Release 解压到独立 A29 目录，不修改原 arrays。执行：

```
OPENBLAS_NUM_THREADS=1 python a29_1_convex_diagnostic.py --self-test
OPENBLAS_NUM_THREADS=1 python run_a29_1_guarded.py --root /path/to/a29 --out /path/to/a29_1
python a30_topology_supplement.py --root /path/to/a29 --results /path/to/a29_1
```

guard 只接受完整 32 条件及 16 个原 parents；验证 baseline、small pool 和原 hard scores。原脚本执行 SLSQP + FW，保存 full/small weights 和 gap。令达到的 error 为 e，gap 为 g，则报告最优 error 区间 `[sqrt(max(0,e²-2g)),e]`。目标 gap≤1e−8；超限保留为 uncertified，不能说得到精确 oracle。这个区间是浮点数值证书，不是 interval-arithmetic proof。

报告 full/small hard、full/small hull、原 saved L 的 MAP/mean、ESS 和 morphology；均值权重来自 data-dependent bank，所以称 weighted estimator，不称 calibrated posterior。这里没有运行 full F 或 single-anchor calibration。

### 3.2 材料表示对照

在同一总 intrinsic 参数预算 16/32/64 上比较：

1. analytic topology-indexed atlas：固定相区连接关系内的 B-spline/法向边界系数 + 每区独立复 contrast；
2. 可微 cell-average 或平滑 level-set：几何与材料幅值自由度分别计数；
3. W-正交多尺度 sparse representation：使用相同坐标/系数预算，公开最佳 s-term tail 与实际约束拟合的差；
4. 单 chart 对照：TRAIN-only PCA/小型解析连续形变 chart，不训练新的大型 decoder。

同一对照内不得给某方法额外真实先验 topology 或额外参数。TRAIN64 用于尺度、范围、模板/坐标构建；不能将 development truth 用来创建在线 chart。允许 development truth 在 offline oracle 拟合中求最佳参数，明确这只测试容量。

每对象每表示最多 8 个预先生成的起点，每起点最多 100 个材料目标迭代；保存每条轨迹的最优值与停止原因。非凸失败不能当作全局容量上限。硬候选/凸 hull 有独立意义，不能强行与 manifold oracle 排成同一个包含关系。

### 3.3 Gate 与解释分支

如果 full hull 的最优 error 下界已经否定 complex ≥10% headroom，则当前 bank 混合路线停止；若达到解有 ≥10% gain、parent 区间下端>0 且结构不恶化，则该 bank 至少存在容量，不以 hard gate 再次否定它。

如果 hull 好、L mean 也好，先保留廉价方案，不自动转生成器/Maxwell。若 hull 好、L mean 差，优先研究权重/似然与 prior，不声称材料表示仍缺失。如果 hull 差而 continuous achieved oracle 明显好，才把 continuous/stratified representation 作为主容量修复。

进入实验二要求：一个合法、TRAIN-only 构造的表示在 complex 的 achieved offline error 相对 N3 至少改善 10%，parent CI 下端>0；三个 complex 家族不能有明显整体负向，且 edge/IoU 不能靠严重拓扑涂抹换取。此门槛是开发筛选，不是测量可部署证据。未过则停止物理付款并区分 optimizer failure 与 representation failure。

## 4. 实验二：bounded compensation 与 Maxwell 识别，≤192 状态调用

### 4.1 每条件的冻结材料状态

每条件最多 5 个状态：一个 measurement-only anchor；一对按预冻结规则产生的 nominal topology/shape 对；一对在合法 bounded geometry/complex-contrast 邻域内完成补偿优化的 endpoints。32×5=160，另留 32 次给真实 fixtures、失败、必要重复和证书核验。状态恰好重复时可缓存复用；不得用节省的预算挑选新成功样本。

补偿先用便宜的 anchor 模型/小型凸子问题求解，而不是让完整 F 无限制迭代。真实 F 只计算预约 endpoints 与必要 anchor。完整非线性集合距离未被全局求解时，分别报告可行点 upper witness 和有证明前提的 lower certificate。

拓扑变化选择规则在实验前固定：由 BP/N3 和 TRAIN-only 几何规则提出一个优先变化；不能按 truth 选择“最容易区分的孔”。没有合法变化是记录中的失败/不适用，不事后补成有利条件。离线 truth-centered positive control 可以另列，但不并入在线主统计，也不新增无限状态。

### 4.2 分解与对照

比较以下逐层变化：固定 pair；仅允许 region contrast 补偿；允许 contrast + 连续边界补偿；再加入有明确 prior 的仪器/background nuisance 敏感性。当前实际数据的背景已知，不应把新增自由 nuisance 的困难结果冒充原实验；该组是 robustness 对照。

对每层计算 raw whitened d、unbounded projected d、bounded d_lin、Maxwell+decoder remainder b，以及 `[max(0,d_lin-b),d_lin+b]`。记录 unconstrained 最优补偿是否超出物理范围。对所有被宣称有效的证书验证实际端点误差；浮点误差容差事先登记。任何错误证书先触发诊断，不删除该样本。

F/L 比较同时拆成：one-anchor offset、Jacobian slope difference、非补偿反馈投影、compensator subspace rotation。single-anchor calibrated L 必须使用实际 `F(anchor)+L(candidate)-L(anchor)`，不得偷偷使用任意 candidate 的 F 中点校准。

### 4.3 独立噪声

固定候选几何与响应后，使用独立 Gaussian draws 做二元检验校准，最多每对 1000 draws，不增加 full-wave state。它只测固定 bank 条件下的检测，不测每个噪声 realization 重新生成候选后的端到端性能；必须分开标注。统计单位仍是 parent，不是 noise draw 或 pair。

### 4.4 Go/No-Go

机制预注册目标：至少 6/12 complex parents 出现 materially consequential 的合法 pair（例如 material distance ≥0.1×原 Δχ 尺度），nominal d≥3，但可行 compensated d≤1，且不是由超出 TRAIN/物理范围的巨大 nuisance 实现。阈值 3/1 是筛选约定；不把它叫全局可识别/不可识别的普遍常数。

若此目标失败，判定“补偿是主要遗漏机制”的证据不足，不用新名字继续扩 bank。若 nominal/compensated 都清晰而容量足够，应考虑 optimization/decision 问题；这不证明物理不可识别。

证书是否有计算价值单独设 gate：在至少一半合法 complex 条件上，区间足够窄以作出预先指定的分离/歧义判别；验证中不出现超容差的 false certificate；证书计时不能比其节省的完整 F 计算更贵。缺 uniform resolvent/curvature 上界的结果只可称 heuristic witness。

满足材料容量和机制/证书 gate 后才进入实验三。若只得到相似于经典 Schur complement 的通用现象，没有 Maxwell-specific 增量，则理论新颖性继续 HOLD。

## 5. 实验三：最小材料恢复和选择性物理，≤320 状态调用

共同起点、同一个通过容量 gate 的表示、同一 TRAIN-only prior、同一个 stopping rule。比较 N3；普通 shape/level-set 或 sparse regularization；表示+L；表示+single-anchor calibrated L；表示+always-F；表示+certificate-guided F。普通基线不可故意缩小容量或使用劣质优化器。

固定最多两次 nonlinear outer updates，禁止无限 line search。每条件为所有比较臂合计预留最多 8 个正常物理 state calls，32×8=256；64 次只用于预注册数值验证、失败和 matched timing，不用来扩模型。可采用以下保守分账：共享 anchor 1、calibrated-L 终点 F 审核 1、always-F 两个 trial states 2、adaptive-F 至多两个 trial states 2、普通 L/形状对照的终点审核最多 2。拒步或预算不够时保留当前输出，不暗中增加 full calls。需要更多物理外迭代才能公平求解时，本 pilot 应标 INCONCLUSIVE_UNDER_BUDGET，而不是声称所有该方法失败。

每个方法分别报告实际在线 raw-to-image 时间、setup/首图/驻留 warm、额外科研 audit 时间及二者合计。科研审核可以不属于部署算法，但不能从研究资源账本中消失。共享 anchor 对真实部署应按每张图的实际成本计入，不能在多臂对照中均摊后宣称快。

### 成像 gate

主终点 complex parent-relative ΔNRMSE gain 相对 N3 ≥10%，bootstrap 下端>0；至少两个 complex 家族平均正向，且没有可靠的 edge/IoU 整体退化。同时报告固定平方材料风险、每个 parent、无修正/拒步/失败数。smooth 结果不能替代主 gate。

### 物理增量 gate

F 相对同表示、同先验的 one-anchor calibrated L 建立 ≥5% paired 材料改善且区间下端>0，才支持“这里完整非线性显著改善材料”的主张。

或者，adaptive-F 对 always-F 的材料误差相对增加不超过 2%，在线 full-wave calls 至少下降 50%，且实际端到端延迟不变差，才支持有用的物理成本门控。2% 应按预先给定的 paired noninferiority 口径报告；样本不足时保留 INCONCLUSIVE。

如果表示有效而 full F 没有额外资格，保留表示结果、放弃 feedback-specific 论文主张。如果 topology 证书有效但无成像/成本效益，最多是诊断结果，不把算法优越性写进标题。

## 6. 交付字段

保存冻结 config、TRAIN-only prior/atlas 描述、case/parent whitelist、每次实际物理调用预约与 receipt、forward/adjoint/JVP RHS、原始和规范化材料 arrays、每一对的 nominal/compensated endpoints、uniform bound 的来源、失败记录、raw-to-image timing 和全部评分。

输出至少包含：CAPACITY_CASES、COMPENSATION_PAIRS、CERTIFICATE_AUDIT、RECOVERY_CASES、PARENT_STATISTICS、COST_LEDGER、FAILURE_LEDGER、FINAL_DECISION。缺数据时写明确 NOT_RUN，不生成虚假的 32-condition SUMMARY。

所有新 experiment 均保持 locked evaluation 关闭。需要确认性论文证据时另行冻结真正未接触的验证设计，不能通过重复读取本 development 集获得。