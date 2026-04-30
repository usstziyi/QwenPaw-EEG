# US-002 学习笔记：核心数据结构

## 三种核心对象

```
Raw      →  (n_channels, n_times)         连续原始信号
Epochs   →  (n_epochs, n_channels, n_times)  事件相关的时间片段
Evoked   →  (n_channels, n_times)         某个条件的平均 ERP
```

## Raw

- 创建方式：
  - `mne.io.read_raw_*()` — 从文件加载
  - `mne.io.RawArray(data, info)` — 从 NumPy 数组创建（本模块重点）
- `raw.get_data()` 返回 `(n_channels, n_times)` 的 NumPy 数组
- 建议数据处理前执行 `raw.load_data()` 把数据从磁盘加载到内存

## Events

- 形状 `(n_events, 3)`，列含义：`[样本索引, 持续时间, 事件ID]`
- 持续时间通常为 0（瞬时事件）
- 事件 ID 用字典映射到有意义的条件名：`{'target': 1, 'distractor': 2}`
- `mne.find_events()` 可从 Stim 通道自动提取事件

## Epochs

- 关键参数：
  - `tmin / tmax`：时间窗口，相对于事件 onset
  - `baseline`：基线校正，如 `(None, 0)` 表示用事件前的全部时间做基线
  - `reject`：幅值拒绝阈值，如 `dict(eeg=150e-6)` 拒绝峰峰值超过 150µV 的段
  - `preload=True`：直接加载到内存
- 索引方式：`epochs['condition_A']` 用事件 ID 字典的 key
- `epochs.get_data()` 返回 `(n_epochs, n_channels, n_times)`

## Evoked

- `epochs.average()` 对某个条件的全部 Epochs 做平均
- 也可以对多个条件分别 `.average()` 得到多个 Evoked
- Evoked 是 ERP 分析的最终输出对象

## 关键经验

1. **基线校正很重要**：不设 baseline 的话，ERP 波形可能整体偏移
2. **tmin 要足够长**：至少留 100-200ms 用于基线校正
3. **epochs 是三维数组**：第一维是 trial 数，容易和 Raw 搞混
4. **模拟数据是最好的学习方式**：α 振荡（10Hz）在 ERP 里应该被平均掉，这是理解 averaging 原理的好练习

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `events` 超出数据范围 | onset 索引 > n_times | 确认 tmin/tmax 范围内的 events |
| 索引不到某些条件 | event_id 字典 key 与 events 不匹配 | 检查大小写 |
| baseline 时段无数据 | tmin 太短 | tmin 至少设 -0.2s |
