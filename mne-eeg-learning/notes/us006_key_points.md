# US-006 学习笔记：事件提取与 Epoching

## Events 数组

### 格式
`events` 是 `(n_events, 3)` 的整数数组：
```
[onset_sample, duration, event_id]
```

- **onset_sample**：事件起始的采样点索引（不是秒）
- **duration**：事件持续采样点数（0 表示瞬时事件）
- **event_id**：事件类型编号（1, 2, 3...）

### find_events 常见问题

- **找不到 Stim 通道**：检查通道类型，有时 Stim 被误识别
- **事件数不对**：调整 `mask` / `mask_type` / `min_duration`
- **多个 Stim 通道**：用 `stim_channel='STI 014'` 指定

### mask 参数
`mask` 用于过滤事件。例如 sample 数据中：
- `mask=32` 保留 response 事件
- `mask=32, mask_type='not_and'` 排除 response，只留刺激事件

## Epochs 参数

### tmin / tmax
- 时间窗口相对于事件 onset
- 必须保证窗口在数据范围内（不要出界）
- 至少留 100-200ms 用于基线校正

### baseline
常用方式：
- `(None, 0)`：用事件前的全部时间做基线
- `(-0.2, 0)`：只用事件前 200ms
- `(-0.2, -0.05)`：事件前 200~50ms（避免刺激前活动污染基线）
- `None`：不做基线校正

### reject
峰值拒绝阈值。单位为 V：
- `dict(eeg=150e-6)` = 峰峰值超过 150 µV 的 trial 丢弃
- 可以分别对不同通道类型设阈值

### flat
死道检测：
- `dict(eeg=1e-6)` = 峰峰值小于 1 µV 的 trial 丢弃

## 条件间平衡

### 为什么需要
条件间的 trial 数不均衡会导致：
- 统计检验不公平
- 信噪比不均
- 视觉对比可能有偏差

### equalize_event_counts
- `method='mintime'`：以最少 trial 数为准，随机丢弃多的
- `method='truncate'`：直接截断（一般不用）

## 关键经验

1. **基线校正必做**：否则不同 trial 的基线偏移会混进 ERP
2. **reject 阈值要合理**：太严 → trial 太少，太松 → 伪迹多
3. **先标记坏导再做 epoching**：坏导的幅值异常会导致大量 trial 被拒绝
4. **epochs 索引用字符串**：`epochs['auditory']`，不是 `epochs[1]`
5. **preload=True**：大多数分析都需要，epochs 数据量通常不大

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 所有 trial 都被 reject | reject 阈值太低 | 调大阈值，检查数据单位 |
| 事件数 ≠ 预期 | find_events 配置不对 | 用 `events[:, 2]` 看事件 ID 分布 |
| 索引返回空 | event_id key 不匹配 | 检查 key 与 events 中实际 ID 一致 |
| 基线校正后波形乱跳 | baseline 覆盖了事件后 | baseline 元组的第二个元素 ≤ 0 |
