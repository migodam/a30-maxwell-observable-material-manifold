# A30 研究包

先读 `A30_THEORY_REPORT_ZH.md`，再读 `A30_MINIMAL_PROTOCOL.md`。报告包含独立推导、已有工作边界、主路线与唯一备选，以及 Strong-TAP 裁决。

## 已完成

原 A29.1 脚本 convex self-test 通过；`a30_algebra_checks.py` 的 17 项有限矩阵测试通过；新增 topology supplement 的 4 个合成数字图像自检通过。真实 Maxwell 后端调用、训练更新和 locked 数据读取均为 0。

`A30_ALGEBRA_CHECKS.json` 是实际运行输出。测试只验证代数，不是实际几何成像证据。

## 未完成

Release 原始候选/目标数组未能下载到本环境，完整 32 条件 A29.1 没有运行。`a29_1/A29_1_EXECUTION_STATUS.json` 明确保存缺失状态。`A29_1_PARTIAL_RESULT.md` 是已有四例三图 hull 的交接结果，不是本轮全候选结果。没有创建伪造的 A29_1_SUMMARY。

LaMP 2026 的出版元数据已核对，全文未取得。当前不作无条件首创/强论文成立声明。

## 脚本

- `a29_1_convex_diagnostic.py`：用户提供的原脚本，未修改。
- `run_a29_1_guarded.py`：完整性防护与 FW 误差区间，拒绝将 partial pool 当 campaign statistics。
- `a30_topology_supplement.py`：完整 A29.1 运行后添加数字 topology 与阈值敏感性，只使用保存的数组。
- `a30_algebra_checks.py`：独立有限矩阵验证，不导入真实物理后端。

```
OPENBLAS_NUM_THREADS=1 python a30_algebra_checks.py
python a29_1_convex_diagnostic.py --self-test
python a30_topology_supplement.py --self-test
OPENBLAS_NUM_THREADS=1 python run_a29_1_guarded.py --root /path/to/a29 --out /path/to/a29_1
python a30_topology_supplement.py --root /path/to/a29 --results /path/to/a29_1
```

依赖 NumPy、SciPy；原始 morphology 指标可从 A29 仓库的 src/a26 读取。完整原数组缺失时必须停止，不用 solver 自动补齐。完整数据路径下的 guard/topology 主流程本轮未执行，因此交付的是已编译和小例自检的分析代码，不是已完成的 32-case 复现。

最终状态与来源范围另见 `A30_MANIFEST.json`。所有新大实验只是规格，未启动。研究包不包含论文全文或大规模原始数据。