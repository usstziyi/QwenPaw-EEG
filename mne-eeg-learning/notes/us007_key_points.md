# US-007 学习笔记：时频分析与 ERP 可视化

## 可视化类型速查

| 图 | 何时用 | MNE 函数 |
|-----|--------|----------|
| 蝴蝶图 | 快速扫描所有通道 | `evoked.plot(spatial_colors=True)` |
| 单通道 ERP | 展示经典波形成分 | `evoked.pick('Cz').plot()` |
| 地形图 | 展示空间分布 | `evoked.plot_topomap(times=...)` |
| Joint Plot | 论文综合展示 | `evoked.plot_joint(times='peaks')` |
| 条件对比 | 多条件统计 | `plot_compare_evokeds(evokeds, ci=0.95)` |
| 时频图 | 频域动态 | `power.plot(picks=ch, baseline=...)` |
| 时频地形图 | 频率+空间 | `power.plot_topo(baseline=...)` |

## ERP 关键时间成分

| 成分 | 潜伏期 | 意义 |
|------|--------|------|
| P1 | 80-130 ms | 早期感觉加工 |
| N1 | 100-150 ms | 注意/辨别 |
| P2 | 150-250 ms | 特征检测 |
| N2 | 200-350 ms | 冲突监测/oddball |
| P3/P300 | 300-600 ms | 认知更新/context updating |
| N400 | 300-500 ms | 语义违反 |
| P600 | 500-800 ms | 句法加工 |

## 时频分析

### Morlet 小波
- 核心思想：用不同频率的高斯窗正弦波与信号做卷积
- `n_cycles`：小波周期的数量
  - 越大 → 频率分辨率越高，时间分辨率越低
  - 常用 `freqs / 2`（如 10 Hz → 5 个周期）
- `decim`：时间降采样因子，加速计算

### baseline 归一化

| mode | 公式 | 适用场景 |
|------|------|----------|
| `'logratio'` | 10 × log10(P / P_baseline) | 论文标准，类似 dB |
| `'percent'` | (P - P_baseline) / P_baseline × 100 | 直观但不对称 |
| `'zscore'` | (P - μ_baseline) / σ_baseline | 统计意义 |
| `'mean'` | P - μ_baseline | 原始差值 |

### ERD/ERS 解读
- **ERD (去同步化)**：功率下降，表示脑区激活、神经元活动去同步
- **ERS (同步化)**：功率上升，表示抑制或节律性活动增强
- 运动想象中，对侧感觉运动区 alpha (8-13 Hz) 出现 ERD，beta (13-30 Hz) 出现 ERD

## 配色与美化

```python
# MNE 默认使用 viridis，也可以自定义
power.plot(cmap='RdBu_r', vmin=-3, vmax=3)  # 蓝-白-红

# 调整时间轴显示
evoked.plot(xlim=(0, 0.5))  # 只显示 0-500 ms
```

## 关键经验

1. **tmin 留够**：时频分析需要足够的基线（至少 200-500ms），否则归一化失真
2. **频率范围要合理**：不要超过低通滤波的截止频率
3. **n_cycles 影响很大**：频率分辨率 vs 时间分辨率的权衡
4. **logratio 是论文默认**：百分比变化在小功率时可能不稳定
5. **地形图时间点选关键点**：不要随机选，选成分峰值潜伏期
6. **多条件对比加置信区间**：`ci=0.95` 让读者知道 variance
7. **plot_joint 最省事**：一张图涵盖 ERP + 地形图，适合快速报告

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 地形图是空白 | 没有 montage | 设置 `raw.set_montage(...)` |
| TFR 结果全一样 | baseline 选错 | 确保 baseline 窗口在事件前 |
| 时频图边缘撕裂 | decim 太激进 | 减小 decim 或不用 |
| plot_compare 报错 | Evoked 通道数不一致 | 确保所有 Evoked 来自同一组通道 |
