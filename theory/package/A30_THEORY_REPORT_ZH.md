# A30 — Maxwell-Observable Material Manifold Theory
## 中文独立研究报告：从表示覆盖到可补偿结构识别

日期：2026-10-10。定位：开放理论研究、既有证据审计、有限矩阵验证、下一阶段实验规格；不是已经完成的新成像方法论文。

## 0. 独立裁决

**推荐主线：补偿感知的分层材料表示与有限割线识别（compensation-aware stratified material inference）。** 先检验一种空腔、边界或部件变化，能否被合法的其他边界形变、复材料对比度及仪器不确定性补偿；再用有误差界的物理模型决定哪些材料分支需要完整 Maxwell。不要先选 flow、diffusion 或单一生成流形，再为其寻找理由。

**研究投入：有条件 GO，只批准材料容量检查和小规模可证伪诊断。Strong-TAP 原创机制：尚未建立；以现有证据形成强论文的裁决是 NO-GO。** 需要新的不是又一个 Jacobian、后验均值恒等式或投影网络，而是可在真实散射几何中成立、可计算且不空泛的“结构—对比度补偿”识别机制。

只保留一条备选：若稳定的低维形状 atlas 不成立，使用多尺度稀疏材料表示与条件弱方向补全。大型生成网络不作为本轮备选主线。

### 0.1 本轮实际完成与缺口

已读取 A25–A29 的主裁决、A27 机制报告、A29 归因报告、A28 理论相关章节、A29.1 完整任务书及完整分析脚本，并核对原始指标实现。部分较长历史报告仅读取相关章节；没有宣称逐行审计全部历史仓库、账本或源码。A25–A27 的主要证据通过 A29 固定版本保留的历史报告交叉核对。

A29 Release 元数据可读取，确认存在 13,502,709 字节的 `A29_RAW_EVIDENCE.zip`，以及复现输入包；但本环境未取得该二进制包。下载尝试受到网络/DNS、二进制抓取限制阻断。Library 中取得的是任务书、脚本和四例交接包，不是全候选原数组。因此：

**FULL A29.1 = NOT_RUN_MISSING_RAW_INPUTS。32 条件全候选 hull 的结果未知。**

本轮实际执行了原脚本的凸包自检，并执行 17 项独立有限矩阵检查，全部通过。它们使用通用小复矩阵，共 29 次矩阵状态代数求值；真实 Maxwell 几何后端调用为 0，训练更新为 0，locked 数据读取为 0。结果见 `A30_ALGEBRA_CHECKS.json`。小矩阵数值通过不是 Maxwell 成像效果证据。

LaMP 的题名、作者、TAP 2026 记录和 DOI 已核对，但全文未取得。故下文不声称 LaMP 没有某个定理，也不作不受限制的首创声明。文献核查截至本次检索日期，不保证数据库已完整收录 2026 年 10 月全部 Early Access 工作。

## 1. A25–A29 到底排除了什么

| 研究阶段 | 可支持的证据 | 不可推出的结论 |
|---|---|---|
| A25 | 特定 weak 背景、幅度 1.2、TV×0.1、12 步的前瞻开发验证中，F 相对 L 的逐 parent 改善为 10.517%，区间 [6.594%,15.316%]；压缩在新范围的梯度门槛失败；总体 HOLD | 不能说所有复杂材料统一提升至少 10%，也不能说已证明学习、部署或 3D 优势 |
| A26 | 匹配的小 CNN 相对无网络初值改善复杂材料约 23%–24%；N2 feedback 相对 N3 复杂收益 −0.273%，区间跨零，完整延迟约 3.274 倍 | 不能说先验无用；不能归因为所有 Maxwell feedback 无用；没有忠实 SOM-Net 对照 |
| A27 | N3 后一次 F 修正：复杂材料 +1.137%，相对 L 额外 +0.160%，数据残差约改善 25.270% | 小而统计可辨的材料差异不等于严格等效；局部弱谱误差不能视为后验不可恢复证明 |
| A28 E1 | 六步 F/TV：复杂材料相对 N3 +1.01%，区间 [−0.76%,2.57%]，相对 L +0.40%，区间跨零；数据残差改善 27.33%；固定结构对大多可分 | 固定编辑对可分不是整个材料类可识别；后验均值差于 N3 不能当成新 teacher 余量；BP 没有已证实的严重固定候选信息损失 |
| A29 | 12 complex parents、24 条件：full hard oracle +2.1468%，小池 hard oracle +2.0919%；smooth 次指标 +55.7800%；新 F 调用 0/512，选择阶段未运行 | hard oracle 不是 convex-hull oracle；四个 TRAIN 模板失败不是整个 TRAIN64 或连续 SDF 的失败 |

来源：[A25]–[A29]。所有百分比优先使用原报告的逐 parent 相对改善，不能混用“均值的比值”。A26–A29 使用已暴露开发对象，不能把其 bootstrap 区间当独立确认性验证。

A29 更具体的限制是：实际每条件 58–91 个独立候选，平均 67.625；复杂组全局 contrast 缩放后仍保留约 98.3387% 原 normalized MSE；2688 条 two-level recipe 因两个 levels 都是 1.2 而完全重复；复杂组 24 个 hard winner 中，11 个相位投影、6 个部件删除、7 个空腔修改、0 个模板。不能把失败全归于 contrast，也不能说空腔候选全部被禁止。[A29-Audit]

A28 历史状态预算下界为至少 807/768，包含真实小网格 fixture；这是原协议违例，不能被本轮零调用覆盖或消除。[A28-E1]

### 1.1 四例 A29.1 的证据等级

随附四例仅在三张图的 hull 上优化：N3、full-pool hard oracle、small-pool hard oracle。

| 固定 weak-background 例 | hard 改善 | 三图 hull 改善 |
|---|---:|---:|
| shell | 0.1235% | 0.1235% |
| asymmetric | 0.5079% | 0.5079% |
| mixed-scale | 0.2123% | 0.2123% |
| smooth | 68.2414% | 74.4673% |

这四例不是完整 pool，不是 32 条件统计，不是测量选择结果。完整 hull 若显著更好，应转查权重/似然/决策问题；完整 hull 若仍差，才有更有力的理由研究离开现有 bank 的连续表示。原 A29 hard-selection 的冻结 NO_GO 不因此改写。[A29.1-input]

## 2. 统一数学对象与边界

以固定频率的离散 contrast-current 方程为基础。背景、入射场、Green 算子和接收算子暂时已知：

\[
L_\chi=I-M_\chi G,\quad
c_s=M_\chi(e_s^{\rm inc}+Gc_s),\quad
e_s=e_s^{\rm inc}+Gc_s,\quad F_s(\chi)=Sc_s.
\]

\(M_\chi\) 为材料乘法算子，源索引为 \(s\)。在二维标量离散模型中是对角矩阵；各向同性三维矢量离散模型中可写成 \(\mathrm{diag}(\chi)\otimes I_3\)。张量材料时须保留乘法算子次序，不能交换矩阵因子。

**假设 A：** 所考察状态的 \(L_\chi\) 可逆；需要统一稳定性时，另明确假设 \(\sup_\chi\|L_\chi^{-1}\|<\infty\)。被动性本身不等于可使用一个很小的统一 resolvent 上界。共振、弱损耗和非正规性都可能放大常数。

**假设 B：** 复材料用真实实坐标微分。记 \(x=\mathcal R\chi\)，\(W\succ0\) 是材料平方损失度量，\(\Sigma\succ0\) 是实数据噪声协方差。质量权重只计一次：可以保留原像素坐标并使用 \(W\)，也可以先乘质量矩阵平方根并令度量为单位阵。

\[
f(x)=\Sigma^{-1/2}\mathcal R F(\chi),\qquad
A_x=\Sigma^{-1/2}J_x.
\]

若 \(n\sim\mathcal{CN}(0,\sigma^2I)\)，实虚部方差是 \(\sigma^2/2\)，故
\[
\|f(x_2)-f(x_1)\|=\sqrt2\|F(\chi_2)-F(\chi_1)\|/\sigma.
\]

白化使用真实噪声定义，不以整幅噪声的 RMS 范数代替二元检验距离。零噪声需另定误差模型，不能用隐藏 floor 制造统计距离。

物理合法性约束作用在实际材料，而不自动作用在相对背景增量上。比如 \(\operatorname{Im}(\chi-\chi_b)\) 可以为负而实际材料仍被动。未知背景、gain、clock 等应成为额外未知量或有依据的 nuisance prior，不能在结论中悄悄当成已知。

## 3. 从 contrast-current 方程独立推导

### 定理 1：一阶导数、有限割线与二阶余项

在假设 A 下，对合法方向 \(h\)，有
\[
\boxed{J_{\chi,s}[h]=SL_\chi^{-1}M_h e_s
=SL_\chi^{-1}M_{e_s}h.}
\tag{1}
\]

对两个可逆端点 \(\chi_1,\chi_2\)，令 \(h=\chi_2-\chi_1\)，则不要求小扰动的恒等式为
\[
\boxed{c_{2,s}-c_{1,s}=L_2^{-1}M_h e_{1,s}
=L_1^{-1}M_h e_{2,s}.}
\tag{2}
\]
\[
\boxed{F_s(\chi_2)-F_s(\chi_1)-J_{\chi_1,s}h
=SL_2^{-1}M_hG L_1^{-1}M_h e_{1,s}.}
\tag{3}
\]

**证明。** 对 \(L_\chi c_s=M_\chi e_s^{inc}\) 微分，\(D L[h]=-M_hG\)，因此 \(L_\chi Dc_s[h]=M_h(e_s^{inc}+Gc_s)\)。直接相减两个状态，得 \(L_2(c_2-c_1)=M_h e_1\)。交换端点得第二个表示。最后使用 \(L_2^{-1}-L_1^{-1}=L_2^{-1}M_hG L_1^{-1}\)，即得余项。

若 \(R=L_\chi^{-1}\)，二阶导数为
\[
D^2F_s[h,k]=SR\{M_hGRM_k e_s+M_kGRM_h e_s\}.
\tag{4}
\]

这明确区分了材料扰动与源分辨内部场。每个源具有不同 \(e_s\)，但所有源共享同一个 \(h\)。

**范围与原创性：** 式 (1)–(4) 是本轮独立重推导的基础；有限割线和余项已经出现在 A28 理论中，不是 A30 新贡献。这些有限维代数可用于矢量离散系统，但不能不加函数空间、奇异积分和网格稳定性条件就宣布连续三维 Maxwell 定理。

### 定理 2：可检查的 anchor 余项

取 anchor \(a\)，令
\[
K_h=R_aM_hG,\qquad r_{h,s}=R_aM_h e_{a,s}.
\]
则
\[
\Delta c_s=(I-K_h)^{-1}r_{h,s},\quad
\Delta F_s-Sr_{h,s}=S(I-K_h)^{-1}K_h r_{h,s}.
\]

若在某个指定算子范数中可证明 \(\|K_h\|\le q<1\)，则
\[
\|\Sigma^{-1/2}\mathcal R(\Delta F-J_a h)\|
\le \|\mathcal S_w\|\,\|K_h r_h\|/(1-q),
\tag{5}
\]
其中 \(\mathcal S_w\) 为正确堆叠源和实白化后的接收映射。

同一 anchor 的截断传播 \(\sum_{k=0}^{m-1}K_h^k r_h\) 具有尾界
\[
\|\text{data tail}\|\le \|\mathcal S_w\|\,\|K_h^m r_h\|/(1-q).
\]

它允许在材料方向上控制物理误差，但每一次 \(R_a\) 作用仍需计 RHS 成本。不是免费的物理，也不需要重新开展 current basis selection。若上界大或 \(q\ge1\)，结论是证书失效，不是实际模型必然发散。有限 power iteration 通常不能直接提供所需严格算子范数上界。

## 4. 表示容量：四类 oracle 不可混为一谈

对材料类 \(\mathcal K\) 定义
\[
e_{\mathcal K}(\chi)=\inf_{u\in\mathcal K}\|u-\chi\|_W.
\]

有限候选 \(\mathcal C\) 满足
\[
e_{\operatorname{conv}\mathcal C}\le e_{\mathcal C}.
\tag{6}
\]
如果 \(\mathcal C\subset\mathcal M\)，还有 \(e_{\mathcal M}\le e_{\mathcal C}\)，但一般 **不存在** \(e_{\mathcal M}\) 与 \(e_{\operatorname{conv}\mathcal C}\) 的固定顺序。

**反例。** 令 \(\mathcal M\) 为单位圆，\(\mathcal C=\{(-1,0),(1,0)\}\)。目标为圆心时 hull 误差为 0 而 manifold 误差为 1；目标为圆顶时 manifold 误差为 0 而 hull 误差为 1。线性平移和尺度变换可将例子嵌入一个合法材料盒内。

任何只在有限 bank 上加权的材料均值都在其 hull 内。因此 hull oracle 是该类均值估计器的逐对象误差下界；hard oracle 只约束硬选择器。权重更好不能超越 hull，生成器更复杂也不自动扩大有用的材料支持。

凸混合可保持逐点凸 box 和被动性约束，却不保持空腔、部件数、二元材料或同一个形状 stratum。并且 \(F(\sum_iw_i\chi_i)\ne\sum_iw_iF(\chi_i)\) 一般成立。

### 4.1 完整 A29.1 的数值证书

原脚本优化 \(f(w)=\frac12\|\sum_iw_i\chi_i-\chi^*\|^2/\|\chi^*-\chi_b\|^2\)，\(w\in\Delta\)。令达到的 NRMSE 为 \(\hat e\)，Frank–Wolfe gap 为
\[
g=w^T\nabla f(w)-\min_i\nabla_i f(w).
\]
凸性给出
\[
\boxed{\sqrt{\max(0,\hat e^2-2g)}\le e_{\rm hull}^*\le\hat e.}
\tag{7}
\]

这是解释优化器是否已到 oracle 的正确方式。浮点 KKT/FW 数值证书不是区间算术证明。随附 guard 强制完整 32 条件、16 parents、12 complex parents 后才允许输出完整统计。

与此相反，非凸 continuous-chart oracle 的局部拟合结果只是最优误差的上界。它取得低误差能证明“表示至少足够好”；它停在高误差不能证明“表示容量不足”。多起点仍不能自动变成全局容量证书。

### 4.2 有限 bank 和连续坐标的量化区别

若一类材料包含一个有正体积的、度量双 Lipschitz 的 d 维参数块，则 K 个候选的最坏覆盖半径至少按 \(cK^{-1/d}\) 缩放，常数依赖参数块体积和度量失真。证明由 K 个半径 r 的 d 维球不能覆盖更大体积得到。

这不是说 A29 已测出 d，而是解释：增加几十个固定编辑不等于控制连续边界自由度。另一方面，放开大量坐标可能缩小 approximation error，同时使受限割线常数趋近 0；容量与稳定性必须一起测。

## 5. 应不应该称作“流形”

推荐对象为一个有明确奇异边界的材料类并集：
\[
\mathcal M=\bigcup_{\tau\in\mathcal T}\mathcal M_\tau,
\qquad \chi=D_\tau(z,q,u).
\tag{8}
\]

\(\tau\) 描述拓扑/材料相区连接关系；\(z\) 是连续几何；\(q\) 是定量复材料；\(u\) 是受控的多尺度余项。\(\tau\) 不应该直接等于 shell/asymmetric/smooth 等数据集标签。

**必须避免一个错误论证：** 光滑的图像流形并不必然只能生成一种空间拓扑。连续灰度场穿过一个阈值时可以出现或消失空腔。受限的是“固定正则边界、固定连接关系”的形状 chart；其部件接触、出生和消失处往往出现奇异 strata。图像集合的拓扑与图像中物体的空间拓扑不是同一概念。

| 表示 | 真正优势 | 对 A29 失败的可能修复 | 主要风险 |
|---|---|---|---|
| 单一光滑低维 decoder | 坐标少，微分容易 | 若几何及 contrast 真正处于该像空间，可连续修正 | 不能仅凭低维推断容量或可识别；过窄 chart 可能重复 N3 偏差 |
| 分层 atlas | 将 topology transition 与层内形变分开检验 | 可离开固定 offset/rigid template；显式复 contrast | 分支遗漏、图册切换、先验质量和复杂度控制 |
| SDF / level set | 连续边界与多连通支持自然 | A29 有限 SDF offsets 不能代表这类方法上限 | 硬指示函数在 L2 中通常不可按普通方式微分；拓扑未必稳定 |
| 多尺度 sparse prior | 细部与非模板形状可逐尺度表达 | 不受四个 nearest template 限制 | 弱细尺度易被噪声主导；稀疏重建本身不是原创 |
| Injective flow | 生成映射可逆/单射，密度与采样方便 | 需先证明材料像空间覆盖复杂结构 | 生成器单射不等于 Maxwell 在其像上单射；64 parents 不支撑通用大 flow 的充分证据 |
| Learned prior / diffusion | 能描述复杂相关性和多模态 | 足够训练覆盖时可能补全弱方向 | distribution shift、过度自信、物理成本和已有直接先例 |

### 5.1 可证明的几何近似界与一个重要微分陷阱

设 \(\Omega\) 的边界存在受控管状邻域，\(d\) 为 signed distance，\(\|d-\hat d\|_\infty\le\epsilon\)。符号不同仅可能发生在 \(|d|\le\epsilon\) 内。若该管状区域体积不超过 \(C_\partial\epsilon\)，材料 jump 不超过 Q，则
\[
\|Q1_\Omega-Q1_{\hat\Omega}\|_{L^2}
\le Q\sqrt{C_\partial\epsilon}.
\tag{9}
\]
额外的区内 contrast 近似误差按三角不等式加入。这是容量界，不是拓扑等价证书。要保证 topology，至少还需要受控 C1 法向图、特征间隔和正 reach 等更强条件；仅 SDF 的 L∞ 接近不够。

平移阶跃函数 \(1_{x>t}\) 时，L2 距离按 \(\sqrt{|\Delta t|}\) 变化，普通 L2 Fréchet 导数不存在。因此不能把形式上的边界 delta 分布当成常规像素 \(D'(z)\)。实施时应使用可微的 cell-average / 平滑占据函数，或使用正确的形状导数理论；前者的平滑偏差必须单列。正则边界下过渡宽度 ε 对应 L2 偏差通常为 O(√ε)，且缩小 ε 会改变导数条件性。

### 5.2 稀疏多尺度的容量界

在 W-正交基 \(\Psi\) 中，令材料系数绝对值降序为 \(|a|_{(j)}\)，则最佳 s-term 误差满足
\[
e_s^2=\sum_{j>s}|a|_{(j)}^2.
\]
若 \(|a|_{(j)}\le Cj^{-1/p}\)、\(0<p<2\)，由积分比较得
\[
e_s\le \frac{C}{\sqrt{2/p-1}}s^{1/2-1/p}.
\tag{10}
\]

后续 box 投影、拓扑约束或固定稀疏支持可能改变这个最佳逼近对象，应另行评价。TRAIN64 经验协方差秩最多 63；对稀有 topology 的有效样本更少。噪声、背景重复不是独立形状，不能因此提高协方差样本秩或声称已学到稳定稀有先验。

## 6. J_z 的几何含义：表示如何使材料方向可恢复

在固定光滑 stratum 内，记 \(T=D_\tau'(z)\)，并以实坐标写
\[
\boxed{J_z=J_\chi T.}\tag{11}
\]
若 T 满列秩，定义
\[
G_z=T^TWT,\qquad H_z=T^TA_x^TA_xT.
\]
对实际材料长度归一化的可观测性由广义特征问题给出：
\[
\boxed{H_zv=\lambda G_zv.}\tag{12}
\]

等价地，看 \(A_xTG_z^{-1/2}\) 的奇异值。对坐标变换 \(z=\varphi(\theta)\)，两矩阵同时按 \(P^T(\cdot)P\) 变换，广义特征值保持不变。原始 latent Jacobian 的奇异值或 FIM trace 则可被 latent 缩放任意改变。

**解释：** 好的表示不是制造新数据，而是排除不能独立出现的弱材料变化，把它们与测量可支持的几何/定量变化联系起来，同时明确这种联系的误差。

若将材料坐标 W-白化、令 Q 是切空间的正交基，N 为测量 Jacobian 零空间，则
\[
\sigma_{\min}(A_xW^{-1/2}Q)
\ge \sigma_{\min}^{+}(A_xW^{-1/2})
\,\sigma_{\min}(P_{N^\perp}Q).
\tag{13}
\]

第二因子是切空间离零空间的角度量。先验约束改善的是合法切方向的角度，不是完整 ambient Jacobian 的 rank。切空间仍与 N 相交时，一阶下界为零。

### 6.1 局部稳定不是全局识别

令 \(g=f\circ D\)，z0 附近为凸参数球。若 \(\sigma_{\min}(g'(z_0))=s>0\)，且球内 \(\|g'(z)-g'(z_0)\|\le Lr<s\)，则对球内两点
\[
\|g(z)-g(w)\|\ge(s-Lr)\|z-w\|.
\tag{14}
\]

证明是沿线积分后，保留固定矩阵 \(g'(z_0)\) 并界定余项。若 D 的材料 Lipschitz 常数为 b，则受限材料割线常数至少为 \((s-Lr)/b\)。

**只在每一点检查 Jacobian 满秩不足以得到全局结论。** 绕圈映射各点导数非零却可重复覆盖。不同 topology chart 也可能有相同数据像。

完整 1152 维实材料开集连续映射到 512 维实数据，不可能全局单射；固定复相位但任意 576 像素的开集仍受维数限制。然而实际先验可能不是这样的开集，不能用 ambient 维数直接否定低维材料类。

## 7. 有限割线、跨 topology 与恢复误差

对明确的材料类定义
\[
\alpha_\mathcal M=\inf_{u\ne v\in\mathcal M}
\frac{\|f(u)-f(v)\|}{\|u-v\|_W}.
\tag{15}
\]
也可以定义分层 \(\alpha_{\tau\tau'}\)，或任务模量
\[
\omega_{\mathcal K,T}(t)=\sup_{u,v\in\mathcal K,\ \|f(u)-f(v)\|\le t}
\|T(u-v)\|.
\]
后者在不存在统一线性下界时仍有意义。这类受限稳定模量已经在 A28 理论中出现。[A28-Theory]

### 定理 3：容量、噪声、物理近似与求解误差分开

设真值 \(x^*\) 不必在 \(\mathcal M\) 内，最近表示 u 达到误差 e。观测 \(y=f(x^*)+n\)、\(\|n\|\le\varepsilon\)。设 \(\|f(u)-f(x^*)\|\le\beta e\)，\(\alpha_\mathcal M>0\)，近似前向在 \(\mathcal M\) 上误差不超过 η，输出 \(\hat x\in\mathcal M\) 的近似残差至多比最优残差大 δ。则
\[
\boxed{\|\hat x-x^*\|_W
\le e+\frac{2\varepsilon+2\beta e+2\eta+\delta}{\alpha_\mathcal M}.}
\tag{16}
\]

**证明。** 以 u 为可行比较点，近似残差至多 \(\varepsilon+\beta e+\eta\)；再加求解误差 δ、两次模型误差 η 和真噪声 ε，可得 \(\|f(\hat x)-f(u)\|\le2\varepsilon+2\beta e+2\eta+\delta\)。应用受限割线下界并加上 e。

这不是一个必然紧的误差分解，也不保证 α 可低成本认证；但它明确说明扩大模型容量时不能只看 e 下降，必须同时看 α、先验偏差和推理成本。

### 7.1 为什么 topology birth 附近不能许诺统一稳定

若一族 cavity 体积 v→0，并假设对应局部总场、接收 dressed kernel 和 resolvent 在该族内有统一界，则有限割线式给出 \(\|\Delta F\|=O(v)\)，而非零固定 jump 的材料 L2 差异是 \(O(\sqrt v)\)。因此对应材料割线比值可为 \(O(\sqrt v)\to0\)。

这是有显式界假设的薄/小结构论证，不是无条件共振结论，也不是新的小体积散射理论。它说明：要谈均匀 topology 识别，应明确最小体积/厚度、最低 contrast、特征间隔，以及误差容限。任意小空腔的存在性不可能仅凭一个正则 atlas 名字获得稳定性。

### 7.2 二元检测与复合材料识别

两个完全指定、等先验、同协方差 Gaussian 假设的 Bayes error 为
\[
P_e=\Phi(-d/2),\quad d=\|f(x_1)-f(x_0)\|.
\]
所以 d=3 对应约 6.68% 错误率，不是“绝对可识别”。候选数、多维连续 nuisance 和模型偏差都会改变复合检验难度。有限 K 个正确指定假设的并集界至多是 \((K-1)\Phi(-d_{min}/2)\)，通常很松；连续类还需要覆盖复杂度。

反过来，若一对材料相距 D，其数据距离很小，则任何材料估计器的两点平均平方风险至少为 \(D^2\Phi(-d/2)/4\)：将估计器转成最近材料分类器，误分时必有至少 D/2 材料误差。确定性有界噪声下，两个响应中点给出至少 D/2 的最坏误差下界。

**有限矩阵反例。** 令 \(G=g11^T\)、\(S=1^T\)、\(e^{inc}=1\)，则响应为 \(t/(1-gt)\)，只依赖 \(t=\sum_i\chi_i\)。不同材料模式可有完全相同响应，而每个固定模式的幅度 chart 都有非零导数。这是反驳“每个 chart 满秩就能区分 topology”的代数例子，不是真实 Green 几何实验。## 8. 最值得检验的新机制：结构信号会被什么补偿

A28 的一个空腔编辑和它的原图之间距离 d 很大，只说明“固定其余材料”的两个点可分。真正成像时，外轮廓、壳厚、区内实部、损耗、小尺度背景等也未知，它们可能补偿该编辑的测量变化。

应比较两个**材料集合**的距离，而不是两个固定图像的距离：
\[
d_F(U_0,U_1)=\inf_{u_i\in U_i}
\|g_1(u_1)-g_0(u_0)\|,
\quad g_i=f\circ D_{\tau_i}.
\tag{17}
\]

其中 \(U_i\) 是有明确半径、box、最小 feature 和 contrast 范围的合法局部参数集。不能允许任意补偿后再把错误归因于物理不可辨识，也不能只允许固定 contrast 后宣称 topology 已识别。

### 定理 4：有界补偿的有限割线证书

对两个中心，有 \(\delta=g_1(0)-g_0(0)\)，以及
\[
B=[-g_0'(0),\ g_1'(0)].
\]
假设在两个指定邻域内 Taylor 余项分别统一不超过 \(b_0,b_1\)。令
\[
d_{lin}=\inf_{u_i\in U_i}\|\delta+B(u_0,u_1)\|.
\]
则
\[
\boxed{\max(0,d_{lin}-b_0-b_1)\le d_F
\le d_{lin}+b_0+b_1.}
\tag{18}
\]

**证明。** 对每一对允许的 u，真实差向量和线性差向量之间的距离至多 \(b_0+b_1\)。反三角不等式和三角不等式分别取 inf 即得上下界；不需要把局部优化结果假装成全局最优。如果线性问题未精确求解，可以用它的凸对偶下界代替下界中的 \(d_{lin}\)，用任意可行点的目标值代替上界中的 \(d_{lin}\)。

若 U 为 convex box/ellipsoid，\(d_{lin}\) 是小型凸问题。余项来源必须同时包含 Maxwell 曲率与 decoder 曲率：
\[
D^2(f\circ D)[v,w]
=D^2f[D'v,D'w]+Df[D''(v,w)].
\tag{19}
\]

对于足够光滑且 Hessian 范数上界为 M 的参数球，\(b\le Mr^2/2\)。对 affine-material chart，可直接使用式 (5) 的 resolvent 余项；对 level-set chart，不能遗漏平滑占据函数和几何曲率。

完全无界线性补偿给出
\[
d_\perp=\|(I-P_B)\delta\|\le d_{lin}.
\tag{20}
\]
**只有下界方向成立。** 一个很小的 \(d_\perp\) 并不能证明所需 contrast 或边界补偿是合法可达的。应保留 bounded optimization；可行补偿点才提供歧义 witness。

解释上，\(d_{lin}-b\) 很大可以认证这两个指定局部材料集合分离；\(d_{lin}+b\) 很小可以认证存在近数据像材料对。两者之间应输出“未决”，不是强迫输出有信心的 topology。若漏掉第三个 chart，二元证书不代表全局正确。

### 8.1 先验限幅与自由 nuisance 不能混为一谈

在线性化模型 \(r=Bv+n\) 中，若 \(v\sim N(0,C_v)\)，则
\[
\min_v\{\tfrac12\|r-Bv\|^2+\tfrac12v^TC_v^{-1}v\}
=\tfrac12r^TP_{eff}r,
\]
\[
P_{eff}=I-B(B^TB+C_v^{-1})^{-1}B^T
=(I+BC_vB^T)^{-1}.
\tag{21}
\]

这是已有的 Schur/高斯消元关系，不是新方法。它说明 strong prior 会限制可补偿量，自由 nuisance 才对应硬正交投影。比较不同 topology 的**边缘似然**还须保留 \(\frac12\log\det(I+BC_vB^T)\) 以及 chart 先验质量，不能仅比较最高 MAP 分数。

### 8.2 Maxwell feedback 的材料价值应投影到补偿以后

令 \(Q_F=I-P_{B_F}\)、\(Q_L=I-P_{B_L}\)，分别对应 F 和 L 的无界线性补偿诊断。记两个中心的有限差向量为 \(\delta_F,\delta_L\)。则
\[
\big|\|Q_F\delta_F\|-\|Q_L\delta_L\|\big|
\le \|Q_F(\delta_F-\delta_L)\|
+\|Q_F-Q_L\|\,\|\delta_L\|.
\tag{22}
\]

第一项是**无法被补偿消去的反馈变化**，第二项是**补偿子空间的旋转**。在有界、非线性 chart 中，要再加式 (18) 的余项与边界效应。

这一关系给出一个比普通 \(\|F-L\|\) 更有针对性的研究问题：反馈是否改变了材料分支在允许几何/contrast 调整之后的距离？如果 F−L 很大却几乎全在可补偿空间里，传播更准确不一定改善结构恢复。相反，即使总量不大，也可能改变一个临界 topology 的判别。

式 (22) 的投影代数本身简单，不能单独包装为强 TAP 定理。潜在贡献是：由 Maxwell 有限割线和严格误差控制形成**可计算的、有材料意义的补偿证书**，并在真实复杂对象上证明它解释了现有失败且改善推断。若证书总是空泛，或计算证书比直接 F 还贵，这条主线应被否决。

#### 实施时避免循环付费

式 (18) 写成真实中心值/切线的形式便于理论与实验解剖，但不能为了“决定是否计算 F”先为所有 chart 计算完整 F 和完整 Jacobian。

部署上应从一个已付费 anchor a 出发，给整个候选 chart 的近似模型建立统一误差界。令 h_i(u)=D_i(u)−a，B 是所用线性模型的斜率；则
\[
\eta_i\le\sup_{u\in U_i}\|\Sigma^{-1/2}(J_a-B)h_i(u)\|
+\sup_{u\in U_i}\|R_a(h_i(u))\|.
\]
第一项可由 anchor 的少量材料方向作用或 receiver-adjoint 组装得到，第二项用式 (5) 与可证明的 uniform 范数界控制。对任意近似模型都成立的集合距离界为
\[
|\inf\|f(D_1)-f(D_0)\|-\inf\|\tilde f(D_1)-\tilde f(D_0)\||\le\eta_0+\eta_1.
\]

只有这种不预先求解所有真实分支的实现才可能节省状态调用。anchor-adjoint、范数估计、几何优化、所有 RHS 和证书求解必须计入成本；若构造可用 η 的成本已超过直接求解竞争分支，成本 gate 失败。不能将少 state calls 自动当作更低延迟。
### 8.3 一个已经验证的代数例子

独立小例子中原始差向量距离约 10.000005；允许一个合法范围内的线性补偿坐标后，剩余距离为 0.01。它反驳“固定对很容易区分，所以整个结构族也容易区分”。这是二维线性代数检验，不是 A29 实测结果。

## 9. 条件材料风险：恢复什么才算正确

### 9.1 条件弱方向不是独立的“先验部分”

假设材料坐标分成 \((u,v)\)，数据只依赖 u，但先验为
\[
v=Ku+\xi,\quad \xi\perp(u,y),\quad\operatorname{Cov}(\xi)=C_\xi.
\]
则
\[
E[v\mid y]=K E[u\mid y],\qquad
\operatorname{Cov}(v\mid y)=K\operatorname{Cov}(u\mid y)K^T+C_\xi.
\tag{23}
\]

测量可以通过相关性降低 Jacobian 零空间内的 Bayes 风险，但不能消除条件残差 \(C_\xi\)。假如这种相关性在 OOD 中错误，测量也未必能检出错误的弱方向补全。

小例子取 \(v=u+\xi\)、\(\operatorname{Var}(u)=1\)、\(\operatorname{Var}(\xi)=0.04\)、观测噪声方差 0.01，则 v 的先验方差 1.04 降至约 0.049901，而非零。不要说“弱方向完全由先验恢复”，应报告条件方差下限、先验失配和可观测关联。

### 9.2 材料均值、MAP 与数据一致性

对固定 W 的平方材料损失，记 \(\mu=E[x\mid y]\)，有
\[
E[\|a-x\|_W^2\mid y]
=\operatorname{tr}(W\operatorname{Cov}(x\mid y))
+\|a-\mu\|_W^2.
\tag{24}
\]

所以后验均值是这个损失的 Bayes action；任何非零确定性修正都增加其条件平方风险。**这不说明对一个有偏的 N3 修正必然有害。** N3 没有被证明是实际后验均值。

如果动作必须落在某个 topology/material 类，最优受约束动作是该类对 μ 的 W-最近点，通常不是 MAP。若要报告 topology，合理动作可以是 posterior topology probability、单独的结构决策和区内定量值，不必让一张跨分支平均图同时承担所有任务。

此外，A29 的 relative NRMSE 并不是式 (24) 的固定二次损失。平方 normalized loss 若带真值权重 \(w(x)=1/\|x-x_b\|^2\)，其最优解是
\[
a^*=E[w(x)x\mid y]/E[w(x)\mid y],
\]
而非普通均值；未平方 norm 则涉及加权几何中位数。IoU、edge 和 topology 决策更不等价。理论风险和实验评分必须明确对齐或分别报告。

### 9.3 非线性物理一致性的精确区分

对条件均值定义不带复共轭的双线性交叉矩
\[
\kappa_s=E[M_{\chi-\mu_\chi}(e_s-\mu_{e,s})\mid y].
\]
则
\[
\mu_{c,s}=M_{\mu_\chi}\mu_{e,s}+\kappa_s,
\quad
F_s(\mu_\chi)-E[F_s(\chi)\mid y]
=-SL_{\mu_\chi}^{-1}\kappa_s.
\tag{25}
\]

均值材料有它自己的 Maxwell 解；该解不必等于各样本场的平均。进一步，\(E[F(\chi)\mid y]\) 也一般不等于 y，因为 \(E[n\mid y]\) 不必为零。这些等式和小矩阵反例已经在 A28 中研究并验证，当前 bank 的 κ 信号不足以支持新网络。[A28-Theory,A28-E1]

多 topology 后验的总协方差还包含跨 chart 均值项：
\[
\operatorname{Cov}(x\mid y)=E_\tau[\operatorname{Cov}(x\mid\tau,y)]
+\operatorname{Cov}_\tau(E[x\mid\tau,y]).
\]
空腔被均值填平，可能来自真实分支歧义，也可能来自错误先验/表示，不能只看模糊图判断原因。

### 9.4 MAP 必须说明参考测度

在单射 chart 中，若先验给定为 latent density \(p_z\)，相对于 W-诱导材料体积的密度为
\[
p_\mathcal M(D(z))=p_z(z)/\sqrt{\det(D'(z)^TWD'(z))}.
\]

latent MAP 与固定材料体积下的 MAP 不必一致。跨不同维数的 strata 需要指定 mixing mass 和各层测度，并积分得到 topology probability；不能比较未做 Jacobian/体积修正的峰值密度。

A29 bank 由同一测量、N3 和 L 规则构造，对它使用 category-balanced 权重可以定义一个估计器，但不能自动称作经过校准的真实 posterior。把 \(p(\chi\mid BP(y))\) 再乘同一 y 的 likelihood 也可能重复计数信息。TRAIN-only 无条件材料先验、测量仅作初始化/搜索，与 data-dependent prior 要区分。

### 9.5 “材料信息量”应是什么

局部线性 Gaussian 模型下，\(C_{post}=(C_0^{-1}+H_z)^{-1}\)，材料风险为 \(\operatorname{tr}(G_z C_{post})\)。增加一个真实传感观测 \(a z+n\) 的局部风险下降为
\[
\Delta R=\frac{aC_{post}G_zC_{post}a^T}{\sigma_n^2+aC_{post}a^T}.
\tag{26}
\]

这类 goal-oriented Bayesian 指标已有成熟先例。[L6] FIM trace 不等于材料风险下降；先验、材料度量和噪声必须同时出现。且**计算一次完整 F 不等于获取一个新测量**：它改善对既有数据的似然计算，不增加物体向实验提供的信息。不可把式 (26) 当成“支付一次 full-wave 就获得一份信息”的定律。

## 10. BP、single-anchor L 与完整 F：如何付费

### 10.1 不默认 BP 已经丢失数据

对线性特征 \(b=Py\)，正确的诱导噪声距离是
\[
d_{BP}^2=\delta^TP^T(P\Sigma P^T)^\dagger P\delta
=\|P_{\operatorname{range}(\Sigma^{1/2}P^T)}\Sigma^{-1/2}\delta\|^2.
\tag{27}
\]

P 满列秩时，精确算术中的统计信息可以完整保留。但高条件数、有限精度及后续非线性都会影响实际可用性。A28 的能量保留检验只覆盖当时固定对，不能自动认证未来 atlas；它也不支持默认新建 raw-data bypass。[A28-E1]

### 10.2 单锚点值校准不等于切线校准

定义
\[
\widetilde F_a(\chi)=F(a)+L(\chi)-L(a),
\]
当 L 为 affine linear，记其斜率为 B，则
\[
F(a+h)-\widetilde F_a(a+h)
=(J_a-B)h+R_a(h).
\tag{28}
\]

一个 F(a) 只消去值偏差，没有消去一阶斜率偏差。所有 calibrated-L 两点割线仍等于 L 的两点割线；校准可改善错误中心导致的 likelihood ranking，却不凭空产生新的割线信息。

本轮小矩阵中，将步幅减半：真实 J_a 切线误差约缩小 4 倍；只作值校准而斜率不对时约缩小 2 倍。这验证了式 (28) 的一阶/二阶区别。

A28 使用任意候选 F 响应的事后中心/中点校准是诊断，不是实际单锚点结果；A29 没有运行新的 F 与 calibrated-L 成像比较。[A28-E1,A29]

### 定理 5：何时可跳过完整 F

若某候选的白化前向误差有有效界 \(\|f_i-\tilde f_i\|\le b_i\)，真实/近似负 log-likelihood 为
\(\ell_i=\tfrac12\|y-f_i\|^2\)、\(\tilde\ell_i=\tfrac12\|y-\tilde f_i\|^2\)，则
\[
|\ell_i-\tilde\ell_i|\le b_i\|y-\tilde f_i\|+\tfrac12 b_i^2=:B_i.
\tag{29}
\]

因此相同先验下，两候选近似 score gap 大于 \(B_i+B_j\)，可认证两者的 MAP 排序不被前向误差逆转。若要认证整个 bank 的 winner，需要对所有竞争者检验，不只是任意一对。

对连续 chart，有统一模型界 η 时，其最优 data residual 也可被夹在
\[
[\max(0,\tilde r_{min}-\eta),\ \tilde r_{min}+\eta].
\]
前提是 \(\tilde r_{min}\) 有全局有效界；一个非凸局部最优不能直接作排除其他 chart 的下界。

**MAP 排序稳定不等于 posterior mean 稳定。** 若相同固定先验上全支持有 \(|\ell-\tilde\ell|\le B\)，则归一化 posterior density ratio 在 \([e^{-2B},e^{2B}]\) 内；总变差可用保守界 \(\min(1,e^{2B}-1)\) 控制。对 \([0,L_{max}]\) 内的决策损失，使用近似后验 Bayes action 的真实 regret 不超过两倍 \(L_{max}\) 乘总变差。此界可松，但明确指出均值认证需要全支持控制；仅 top-1 margin 不够。

### 10.3 推理策略

先用 BP/N3 初始化和 TRAIN-only 小先验；在有容量的材料表示上用 L 或单锚点 calibrated L 拟合；保留数据与模型误差允许的多个 chart；只对“材料差异大、廉价排序证书未决”的竞争分支细化 F。

不把较大 data residual 自动视为值得付费，也不把证书未通过自动视为 F 有用。证书可能只是太松。完整 F 是否值得，仍由相同表示、先验和计算预算下的材料收益与 raw-to-image 时间裁决。

对 24×24 标量离散模型，L 为 576×576 complex128，单矩阵约 5.3 MB；实 Jacobian 512×1152 约 4.7 MB。可以在同一材料 LU 上复用 8 个 forward RHS，并用 32 个 receiver-adjoint RHS 组装跨源材料 Jacobian，或直接对少量材料坐标做 JVP；需要比较实际 RHS、传输、求解和证书成本。上述存储量不是整个推理内存保证，也不是 3D 扩展成本。

## 11. 文献和原创性审计

下表按可取得的原始论文、作者页面和出版记录归纳。没有取得全文的工作不用于“它没有某项机制”的否定性判断。

| 工作 | 已覆盖内容 | 对 A30 的约束与读取范围 |
|---|---|---|
| Deep Injective Prior for Inverse Scattering，TAP 2023 | 材料低维生成流形、仅材料训练、Maxwell 反演与后验/UQ | 已直接覆盖“材料流形 + 物理 + MAP/采样”；原论文公开文本与作者记录核对 [L1] |
| LaMP: Latent Manifold Projection for Plug-and-Play Generative Priors in Electromagnetic Inverse Scattering，TAP 2026 | 题名与出版记录直接落在 latent manifold/PnP prior 范围 | DOI/作者/题名确认；全文未取得，不宣称它缺少 topology、证书或风险理论 [L2] |
| Learned Regularization for Microwave Tomography，TAP 2026；2025 preprint | Single-Step Diffusion Regularization 与 data-consistency variational/PnP 框架 | “小步扩散先验 + 物理更新”不能作原创；年份按原 arXiv 的 journal reference 修正 [L3] |
| Exploring Scaling Laws in Large Learning Models for Inverse Scattering With Spatial–Temporal Diffusion，TAP 2025 | 多通道 current diffusion、模型/数据 scaling 与不确定性 | current diffusion 不是新的空白；此处核对出版记录及摘要，不宣称全文审计 [L4] |
| SOM / TSOM / FFT-TSOM / SOM-Net | 确定性与歧义 current 分解、两重正则、物理展开和共享材料更新 | 不能把 current/field/material losses 或 physics unrolling 当新贡献；SOM-Net 为 TGRS，不是 TAP [L5] |
| Goal-oriented Bayesian inverse problems；generative compressed sensing | prior/noise/task 联合度量、受限割线恢复与 approximation error | 式 (12)、(16)、(26) 的一般思想不是 A30 首创；随机 sensing 定理不能套成固定 Maxwell 保证 [L6,L7] |
| Bayesian level set；经典 joint shape/contrast inverse scattering | 形状先验、边界演化、可变拓扑和定量材料联合反演 | “SDF + 复 contrast + Bayesian”本身不新 [L8,L9] |
| PnP Latent Diffusion for EM inverse scattering，2025 preprint | 学习材料分布，交替 likelihood/prior 采样，MMSE 输出 | 已覆盖很多“生成后验 + 物理 + 均值”设想；未核实其为 TAP [L10] |
| Physics-Guided Conditional Diffusion Networks，2025 preprint / 2026 OJAP 记录 | 多个条件材料样本 + 前向一致性评价 | 候选生成后以 F 排序已有直接先例；不能冒称 TAP [L11] |
| ScoreField，2026-08 preprint | contrast/current 双 INR 与 score prior，完整散射约束 | 仅把物理场与 score 组合不新；本轮未确认 TAP 接收状态 [L12] |
| FlowDPS（2025 preprint）；FLOWER（ICLR 2026） | flow posterior sampling / 数据可行投影与 flow 轨迹约束 | flow matching + inverse likelihood/投影是现成方向，未据此声称电磁 TAP 首创 [L13,L14] |

检索还发现 2026 年 9–10 月 general inverse-problem flow 相关题名，但其中部分原始页面未成功取得；本报告不据二手摘要认领或排除其具体定理。这也是不给无保留首创结论的原因。

### 11.1 与 A12/A17 的关系

A12/A17 的 frozen GN 或 current-exchange 结论可以通过 A28 已重推导的二次模型误差关系使用：在同一个固定正则、状态、实坐标二次模型、Hessian 正定且无额外活动集变化时，局部 step defect 可精确表达在有限支撑中。这不等于非线性材料恢复优势，也不覆盖 topology jump。

A30 不重开 current shortlist、current basis 或 candidate ranking 搜索；其研究对象是**材料集合中允许出现的有限差异**。本轮没有重新审计 A12/A17 全部历史代码，因此不作更强引用。

### 11.2 原创性分类

**已有结论：** generative MAP/posterior；SDF/level-set shape inversion；prior-whitened FIM；goal-oriented risk；一般受限割线稳定性；数据一致性与 Bayes action 的区别。

**本项目已有：** exact Maxwell finite secant、二阶余项、κ mean closure、弱方向条件先验反例、frozen-GN defect。A30 可独立校验和使用，不可重复计为新贡献。

**小变体：** 将这些公式写成 \(J_\chi D'\)、给 latent 加物理 loss、对当前 bank 做 soft mean、只加一层 manifold projection。即使跑通，也不足以成为强 TAP 机制。

**可能真正有价值、但待验证：** 在复杂材料表示上，构造同时考虑合法 contrast/geometry/nuisance 补偿、Maxwell 有限变化及余项的跨 stratum 识别证书；证明 feedback 只在非补偿信号与补偿空间旋转上影响材料决策，并以此减少实际物理代价或暴露不可恢复结构。

**不成立：** generator 单射推出 Maxwell 单射；局部满秩推出跨 topology 可辨识；hard oracle 是均值上限；posterior mean 必须精确拟合 y；先验补全等于数据直接测得；被动性推出良好统一 resolvent 条件数。

## 12. 最终路线选择

### 主线：补偿感知的分层材料推断

最小表示采用受约束的占据函数、连续边界控制点和分区复 contrast：
\[
\chi=\chi_b+\sum_r q_r m_{\tau,r}(z)+\Psi_{fine}u.
\]
各 m 应组成明确的相区划分或有规定的混合规则，防止重叠相区产生未解释材料；q 的实虚部独立，最后约束实际材料 box。u 是有尺度先验的少量余项，而非任意全网格 escape；额外保留 unknown-chart 报警，不能硬塞成四种数据集家族。

先证明/量化这个表示有容量，再比较未补偿距离和 bounded compensated distance。若前者很大、后者普遍降到噪声尺度，应将不可判别性作为实际机制，并用条件先验/多分支输出控制风险；若补偿后仍分离，应验证算法能从测量而非 truth 选出正确分支。

创新边界是“证书和真实补偿机制”，不是 atlas 本身。完整 F 的独立资格需额外击败单锚点 calibrated L，不能以更低 data residual 替代。

### 唯一备选：多尺度稀疏表示与条件弱方向补全

若复杂边界无法由少量稳定 chart 表达，保留尺度层次和最佳 s-term tail 诊断。把测量敏感的 coarse/structural 坐标与条件细节分布联系起来，使用 shrinkage covariance、区间或小 Gaussian mixture，而不是固定 weak-SVD 输出投影。

核心理论是式 (10) 的表示误差和式 (23) 的条件不可约风险。稀疏先验、wavelet MAP、Gaussian conditional completion 都已有先例，因此它只在建立实际的新材料尺度/补偿机制和风险收益时才具备论文价值。若仅胜过 N3 但没有新机制，应视为工程基线，不升级为强 TAP 主张。

不选择第三条 flow/diffusion 路线：64 个独立训练形状、现有 coverage 失败与已有密集先例，不支持以大模型训练作为当前最有效的判别实验。这不是否定这些模型，而是拒绝在缺乏容量和识别证据时把它们当答案。

## 13. 三个实验与分阶段 Go/No-Go

详细执行规则见 `A30_MINIMAL_PROTOCOL.md`。以下阈值是本提案的工程筛选约定，不是普遍统计/物理常数，也不改写原 A29 gate。

**E0 / 第一个实验：零新增全波的 capacity audit。** 完成原 32 条件 full/small hull，报告 FW gap 区间、L MAP/mean、ESS、edge/IoU；随后在固定参数预算 16/32/64 下比较 analytic atlas、连续 SDF、稀疏基和单 chart。参数/先验仅用 TRAIN64，truth 仅用于离线 best-fit 容量评价。若 hull 已足够好，先做最廉价的权重/选择检验，不强制转 atlas；若连续表示 achieved oracle 仍无 ≥10% complex headroom，暂不支付新的 Maxwell。非凸拟合失败标为优化/容量未分离，不当作全局容量证明。

**E1 / 第二个实验：补偿与物理识别。** 最多 192 个真实后端状态调用，覆盖 32 条件，每条件最多 5 个预先指定材料状态，另留 32 次所有 fixture/失败/重复的预算。比较固定对、合法 bounded contrast/geometry 补偿对、prior-limited nuisance；计算 F、L、single-anchor calibrated L、tangent/finite secant 以及余项。先验与变形规则不得依据本轮 truth 选择。主要检验“原始清晰但补偿后歧义”的机制是否在至少 6/12 complex parents 出现，并检查有效证书是否足够紧；同时报告反例。机制若不成立，则拒绝该主解释，而不是继续扩候选。

**E2 / 第三个实验：只在前两阶段正面后做小重建。** 最多 320 个新增后端调用；与第二实验合计上限 512，包括真实 fixture、timing、失败和审核。相同表示/先验分别配 L、single-anchor calibrated L、always-F 和 certificate-guided F；对照 N3、普通正则形状/稀疏方法。复杂材料 paired gain 至少 10%、区间下端 >0，并且 edge/IoU 无可靠退化，才通过表示成像 gate。F 必须额外建立至少 5% 相对 calibrated-L 的材料优势，或在 always-F 误差增加不超过 2% 的前提下减少至少 50% 在线 F 调用且不增加端到端延迟，才通过物理付费 gate。

对 family 数仅 4 的小组不作过强显著性结论。所有置信区间仍是重复审视后的 exploratory development；未打开 locked evaluation。未来要获得强 TAP 的独立实证，需另行冻结一个未接触的新验证设计，而不是把本轮开发集重新命名。

## 14. Strong-TAP novelty verdict

**现阶段：NO-GO for a Strong-TAP claim；CONDITIONAL GO for the bounded mechanism pilot。**

理由不是“问题很难”或“流形不可能”，而是三个具体缺口：完整 A29.1 hull 未跑；最接近的 LaMP 全文尚未完成对照；核心 compensated-topology 机制尚未在真实 Maxwell 几何中得到独立材料效果与成本证据。

值得下一阶段投入的命题是：**在足够有表达力的材料类中，哪些结构变化在允许其他材料自由度补偿后仍保留测量支持；能否以可计算的 Maxwell 余项证书把这种支持转成可靠的结构决策和更少的物理求值。**

如所得结果只是“拟合一个更好的 decoder，然后投影/做 MAP”，已有论文已经覆盖其主要概念；如证书普遍空泛或 full F 不能胜过合法单锚点对照，应终止相应原创机制主张。若出现跨多个复杂家族的非补偿结构信号、可复现的 compensation failure/repair、可用证书和匹配成本收益，则有形成强 TAP 论文的实际可能，但本报告不预先授予成功。

## 15. 来源、版本与读取边界

### 项目来源

- [A25] `A25_FINAL_RESEARCH_DECISION.md`；相关 `A25_RESEARCH_REPORT_ZH.md` 章节。历史原项目 `migodam/a25-adaptive-om-feedback`，原 commit `59d8cc57c9da99ccb7978febc308193c43d6f3e5`；本轮通过固定 A29 仓库保留的报告读取。
- [A26] `A26_FINAL_DECISION.md`、`A26_RESEARCH_REPORT_ZH.md` 相关章节、`src/a26/metrics.py`。原项目 `a26-om-feedback-prior-completion`，commit `2603f3bd16c48e48587fedc4363975779def17f5`。
- [A27] `A27_MECHANISM_DIAGNOSIS.md`。原 commit `325cc8a5f99d686ce1b1570296f94b0df1e90141`。
- [A28-E1] https://github.com/migodam/a28-maxwell-material-information/blob/c7819fa142bb70f9920835e8e91ba145f15ed8e3/E1_DECISION.md
- [A28-Theory] `theory/a28/A28_RESEARCH_REPORT_ZH.md`，通过 A29 固定仓库读取相关理论部分。其有限割线、条件风险、κ 与 GN 缺陷不是 A30 新贡献。
- [A29] https://github.com/migodam/a29-material-hypothesis-coverage/blob/5d5e31fcfc56ac8ef9d64c46b4b7bbdedef96bb4/A29_DECISION.md
- [A29-Audit] 同 commit 的 `research/delegated/a29_audit/COVERAGE_FAILURE_ATTRIBUTION.md`。
- [A29-release] https://github.com/migodam/a29-material-hypothesis-coverage/releases/tag/a29-v0.1.0 。只取得元数据；未取得原数组 ZIP。
- [A29.1-input] 本包保留的 `A29_1_PARTIAL_RESULT.md`、原 `a29_1_convex_diagnostic.py` 和原任务书。四例数值为已有交接结果，不是本轮全池重算。

### 原始文献

- [L1] Khorashadizadeh et al., **Deep Injective Prior for Inverse Scattering**, IEEE TAP, 2023. DOI: 10.1109/TAP.2023.3312818. https://arxiv.org/abs/2301.03092 。论文公开文本/摘要与作者机构记录核对。
- [L2] Sun et al., **Latent Manifold Projection for Plug-and-Play Generative Priors in Electromagnetic Inverse Scattering**, IEEE TAP, 2026. DOI: 10.1109/TAP.2026.3722905. 出版记录核对；全文不可得。
- [L3] Tong et al., **Learned Regularization for Microwave Tomography**, IEEE TAP, 2026; preprint 2025. DOI: 10.1109/TAP.2026.3664658. https://arxiv.org/abs/2508.08114 。原摘要及 journal reference 核对。
- [L4] Liu et al., **Exploring Scaling Laws in Large Learning Models for Inverse Scattering With Spatial–Temporal Diffusion**, IEEE TAP, 2025. DOI: 10.1109/TAP.2025.3569099. 出版记录/摘要核对，非全文。
- [L5] Chen, SOM, IEEE TGRS 48(1), 42–49, 2010, DOI: 10.1109/TGRS.2009.2025122; Zhong & Chen, TSOM, Inverse Problems 25, 085003, 2009, DOI: 10.1088/0266-5611/25/8/085003; FFT-TSOM, IEEE TAP 59(3), 914–927, 2011, DOI: 10.1109/TAP.2010.2103027. 作者原始出版列表与摘要记录核对。**SOM-Net**, IEEE TGRS 60, 2022, DOI: 10.1109/TGRS.2022.3217162, https://arxiv.org/abs/2209.03567 。不将原算法和 A26 小 CNN 视为同一个基线。
- [L6] Spantini et al., **Goal-Oriented Optimal Approximations of Bayesian Linear Inverse Problems**, SIAM J. Sci. Comput., 2017. DOI: 10.1137/16M1082123. 原始出版/作者存档摘要核对。
- [L7] Bora et al., **Compressed Sensing using Generative Models**, ICML 2017. https://proceedings.mlr.press/v70/bora17a.html 。原出版页面核对；其随机测量假设不可移植为固定 Maxwell 性质。
- [L8] Iglesias, Lu & Stuart, **A Bayesian Level Set Method for Geometric Inverse Problems**, 2016. DOI: 10.4171/IFB/362. https://arxiv.org/abs/1504.00313 。原出版/摘要核对。
- [L9] Miller, Kilmer & Rappaport, **A New Shape-Based Method for Object Localization and Characterization from Scattered Field Data**, IEEE TGRS, 2000. DOI: 10.1109/36.851967. 摘要/出版记录。Dorn, Miller & Rappaport, **A Shape Reconstruction Method for Electromagnetic Tomography Using Adjoint Fields and Level Sets**, Inverse Problems, 2000. DOI: 10.1088/0266-5611/16/5/303. 原出版记录。
- [L10] Guo et al., **Plug-and-Play Latent Diffusion for Electromagnetic Inverse Scattering with Application to Brain Imaging**, 2025 preprint. https://arxiv.org/abs/2509.04860 。原摘要核对。
- [L11] Chehelgami, LoVetri & Khoshdel, **Physics-Guided Conditional Diffusion Networks for Microwave Image Reconstruction**, 2025 preprint; 2026 IEEE OJAP record, DOI: 10.1109/OJAP.2026.3727556. https://arxiv.org/abs/2510.25729 。原摘要及出版元数据，非 TAP。
- [L12] Guo, Gao & Sun, **ScoreField: Neural Inverse Scattering with Score-Based Generative Priors**, 2026-08-03 preprint. https://arxiv.org/abs/2608.02937 。原公开 HTML/摘要读取；未核实 TAP 接收。
- [L13] Kim, Kim & Ye, **FlowDPS: Flow-Driven Posterior Sampling for Inverse Problems**, 2025 preprint. https://arxiv.org/abs/2503.08136 。原摘要；不视为已验证电磁方法。
- [L14] Pourya, El Rawas & Unser, **FLOWER: A Flow-Matching Solver for Inverse Problems**, ICLR 2026; preprint 2025. https://arxiv.org/abs/2509.26287 。原摘要；通用逆问题，不据此声称 TAP 工作。

文献表中的“未获得全文”是结论强度限制，而不是断言该文缺少某项技术。所有本轮代数推导均需与这些一般先例以及 A28 既有理论区分。**出版状态补核：** FLOWER 的作者 EPFL 页面与 ICLR 官方 proceedings 均确认 ICLR 2026 论文，不仅是 2025 preprint。原始会议页面：https://proceedings.iclr.cc/paper_files/paper/2026/hash/939af25e6dc31d3d020fda2f64016917-Abstract-Conference.html 。这是通用线性逆问题的 flow posterior 工作，不是 IEEE TAP 或电磁实验。