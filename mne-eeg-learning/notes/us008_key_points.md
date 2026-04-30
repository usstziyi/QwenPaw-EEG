# US-008 学习笔记：公开数据集端到端实战

## 推荐公开数据集

### 入门级

| 数据集 | 范式 | 通道 | 试次 | 推荐理由 |
|--------|------|------|------|----------|
| MNE Sample | 听觉+视觉 | 60 EEG + MEG | ~100 | 零配置，MNE 自带 |
| ERP CORE | 六种经典 ERP | 30 EEG | ~200/范式 | 结构清晰，文档好 |
| OpenNeuro ds003505 | 听觉 oddball | 64 EEG | ~400 | 标准 oddball |

### BCI 运动想象

| 数据集 | 类别 | 通道 | 被试 | 来源 |
|--------|------|------|------|------|
| BCIC IV 2a | 4 类 | 22 EEG | 9 | MOABB |
| BCIC IV 2b | 2 类 | 3 EEG | 9 | MOABB |
| PhysioNet MI | 4 类(运动/想象) | 64 EEG | 109 | PhysioNet |

### 高级

| 数据集 | 特点 |
|--------|------|
| OpenNeuro ds004504 | 同时 EEG-fMRI |
| TUH EEG Corpus | 临床脑电，巨大 |
| HBN (Healthy Brain Network) | 大规模静息态 |

## BCIC IV 2a 详解

### 数据结构
- 每个被试两个文件：`A{sub}T.gdf`（训练）和 `A{sub}E.gdf`（测试）
- 训练数据有标签，测试数据标签隐藏
- 每个 session ~288 trials，四类各 ~72 trials

### 事件时序
- 0s：出现提示（十字）
- 2s：出现 cue 箭头（←左手 →右手 ↑双脚 ↓舌）
- 3-6s：运动想象期间
- 6-7.5s：休息

**epoching 窗口建议**：`tmin=0, tmax=4`（cue 出现后），或`tmin=-1, tmax=3`（含基线）

### 通道配置注意事项
- GDF 格式读入后，通道名可能带括号后缀如 `'Fz (1)'`
- MNE 可能无法自动匹配标准 10-20 蒙太奇，需要手动 strip 后缀
- EOG 通道是双极导联，ICA 时记得排除在外

## 完整 Pipeline 检查清单

```
1. [ ] 数据加载：确定格式、通道配置、蒙太奇
2. [ ] 事件提取：find_events + 条件映射
3. [ ] 预处理：
       [ ] 陷波 50/60 Hz
       [ ] 带通滤波 1-40 Hz
       [ ] 降采样（如从 250 → 150 Hz）
       [ ] 重参考（平均参考）
       [ ] 坏导检测+插值
4. [ ] ICA：fit → 识别眼电 → 排除 → apply
5. [ ] Epoching：tmin/tmax + baseline + reject
6. [ ] 保存中间结果（.fif 或 .npy）
7. [ ] ERP 分析：
       [ ] 蝴蝶图（全通道扫描）
       [ ] 选择 ROI 通道
       [ ] 多条件对比图
       [ ] 地形图
8. [ ] 时频分析：
       [ ] Morlet 小波 TFR
       [ ] baseline 归一化
       [ ] ERD/ERS 图
       [ ] 条件间差异图
9. [ ] 统计检验（如果需要）：
       [ ] 配对 t-test
       [ ] 聚类置换检验
```

## 常见坑

| 坑 | 表现 | 解决 |
|----|------|------|
| 通道名不匹配蒙太奇 | set_montage 报错 | 手动 rename 或用 set_channel_types |
| GDF 事件检测不到 | 事件 ID 全一样 | 调 shortest_event 或用 stim_channel |
| 想象期太长 | TFR 基线不稳定 | 缩短 tmax，只用 cue 后 2-3 秒 |
| 被试间差异大 | 统合分析困难 | 先跑单个被试，确认 pipeline 正确 |
| 数据太大 | 内存溢出 | 先降采样，再 preload |

## 关键经验

1. **先在小数据（MNE sample）上跑通，再上公开数据集**
2. **一个被试跑通后，造个 for loop 批量跑**
3. **每步保存中间结果**，断点续跑不用从头来
4. **可视化每步输出**，预处理出错会一直传播
5. **写函数时加 docstring**，一周后你自己也认不出来
6. **BCI 数据通常有延迟反馈（smiley）**，epoching 时要区分 cue 和反馈
