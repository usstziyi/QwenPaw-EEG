# US-001 学习笔记：环境搭建与初识 MNE

## 核心概念

### Raw — 原始数据容器
- MNE 最基础的数据结构，存储**连续时间序列**数据
- 类似 NumPy 的 `(n_channels, n_times)` 数组，但带有丰富的元信息
- 支持多种文件格式：`.fif`, `.edf`, `.bdf`, `.set`, `.vhdr` 等
- `preload=False` 时磁盘映射（省内存），`preload=True` 时全加载到 RAM

### Info — 元信息字典
- 存储通道名、类型、采样率、滤波器参数、电极位置等
- 关键字段：
  - `sfreq` — 采样率
  - `ch_names` — 通道名列表
  - `bads` — 标记为坏的通道
  - `highpass` / `lowpass` — 已应用的滤波范围
  - `meas_date` — 记录日期
- MNE 中绝大多数函数依赖 Info 来判断通道类型，**别手动乱改**

### Annotations — 事件标注
- 存储时间点/段上的事件标记
- 常见标注类型：`BAD_` 前缀（坏段）、`EDGE_` 前缀（边界）、刺激标签
- 与 `events` 数组互补：Annotation 是描述性的，events 是数值化的（用于 epoching）

## 关键经验

1. **`raw.info` 是只读？** —— 不是，但有些字段修改有限制。修改采样率等关键参数要用专用方法（如 `raw.resample()`）
2. **通道类型很重要** —— MNE 根据通道类型自动区分 EEG/MEG/EOG/STIM，选错类型会导致后续分析出错
3. **`preload` 的选择** —— 数据处理前建议 `preload=True`（或 `raw.load_data()`），磁盘映射模式很多操作不支持
4. **可视化用 `%matplotlib qt`** —— Jupyter 内嵌图交互性差，弹出独立 Qt 窗口体验更好

## 常见问题

| 问题 | 解决 |
|------|------|
| `mne.sys_info()` 报错 | 检查 numpy/scipy 版本兼容性，建议 Python 3.10 + MNE 最新版 |
| sample 数据集下载慢 | 可从 mne.tools 手动下载 zip 解压，设置 `MNE_DATA` 环境变量指向目录 |
| `raw.plot()` 无响应 | Jupyter 中用 `%matplotlib qt` 弹出独立窗口；脚本中直接调用即可 |
| 通道类型识别错误 | 用 `raw.set_channel_types()` 手动修正 |

## 下一步

US-002 将学习 MNE 的核心数据流转：`Raw → Epochs → Evoked`，以及如何手写代码创建这些对象。
