# US-003 学习笔记：多格式导入导出

## 常见格式一览

| 格式 | 扩展名 | 来源设备/软件 | 特点 |
|------|--------|--------------|------|
| FIF | `.fif` | MNE / Neuromag | MNE 原生，信息最全，推荐中间格式 |
| EDF | `.edf` | 医院 EEG 系统 | 最通用的临床格式，通道名常不规范 |
| BDF | `.bdf` | BioSemi | EDF 的 24-bit 版本 |
| BrainVision | `.vhdr/.vmrk/.eeg` | BrainProducts | 三文件组合，指定 .vhdr 即可 |
| EEGLAB | `.set/.fdt` | EEGLAB (MATLAB) | 二元组，MNE 自动找 .fdt |
| Neuroscan | `.cnt` | Neuroscan | 老格式，有时需要额外安装包 |
| GDF | `.gdf` | 通用 | 较新，支持更多事件类型 |

## 读取模式

- `preload=False`（默认）：延迟加载，数据留在磁盘，内存占用小，支持的操作有限
- `preload=True`：全部加载到内存，支持所有操作，适合预处理
- 无论哪种模式，都可以随时 `raw.load_data()` 切换到全内存模式

## EDF 通道名的坑

EDF 文件的通道名可能类似 `"EEG Fpz-Cz"` 或直接 `"Fpz-Cz"`。MNE 可能**不会自动识别为 eeg 类型**。

**修复方法：**
```python
raw.set_channel_types({ch: 'eeg' for ch in raw.ch_names if 'EEG' in ch or 'eeg' in ch})
# 或逐个指定
raw.set_channel_types({'Fpz-Cz': 'eeg', 'Oz-Cz': 'eeg'})
```

## BrainVision 的特殊性

- `.vmrk` 文件中的标记会被自动转为 MNE Annotations
- marker 编码方式可能不同（基于采样点 vs 基于时间），MNE 通常能自动处理
- 如有问题，用 `mne.io.read_raw_brainvision(..., preload=True, event_id=...)` 显式指定

## 推荐工作流

```
原始文件 (.edf/.vhdr/.set)
    │
    │  read_raw_xxx(preload=True)
    ▼
Raw 对象
    │
    │  raw.save('cleaned_raw.fif', overwrite=True)
    ▼
中间存储 .fif  ← 从这往后都用 .fif，加载快，Info 完整
    │
    │  read_raw_fif('cleaned_raw.fif', preload=True)
    ▼
预处理 → Epochs → Evoked
```

## 关键经验

1. **读入后第一件事：存 .fif** — 以后重跑不用重新解析原始格式
2. **检查通道类型** — 用 `set_channel_types()` 修正，不然后续分析全乱
3. **EDF 最麻烦** — 通道名不规范是常态，做好心理准备
4. **大文件用 preload=False** — 4GB+ 的文件不要盲目 preload
