"""
US-002: 核心数据结构 — 可复用函数库

提供以下函数：
    create_dummy_raw()     — 用 NumPy 创建模拟 EEG Raw 对象
    create_dummy_events()  — 创建模拟事件数组
    raw_to_epochs()        — Raw + Events → Epochs
    epochs_to_evoked()     — Epochs → Evoked（分条件平均）
    plot_evoked_butterfly()— 蝴蝶图可视化
"""

import numpy as np
import mne


def create_dummy_raw(
    n_channels=8,
    sfreq=250,
    duration=60,
    seed=42,
):
    """用 NumPy 数组创建模拟 EEG Raw 对象。

    每个通道 = 10Hz alpha 振荡 + 高斯噪声。

    Parameters
    ----------
    n_channels : int
        EEG 通道数。
    sfreq : float
        采样率 (Hz)。
    duration : float
        数据时长 (秒)。
    seed : int
        随机种子，保证可复现。

    Returns
    -------
    raw : mne.io.Raw
    """
    rng = np.random.default_rng(seed)
    n_times = int(sfreq * duration)
    t = np.arange(n_times) / sfreq

    # 每个通道：alpha 振荡 + 噪声
    data = np.zeros((n_channels, n_times))
    for ch in range(n_channels):
        alpha = 50e-6 * np.sin(2 * np.pi * 10 * t)
        noise = 20e-6 * rng.standard_normal(n_times)
        data[ch] = alpha + noise

    # 构建 Info
    ch_names = [f"EEG {i:03d}" for i in range(1, n_channels + 1)]
    info = mne.create_info(ch_names, sfreq=sfreq, ch_types="eeg")
    montage = mne.channels.make_standard_montage("standard_1020")
    info.set_montage(montage)

    raw = mne.io.RawArray(data, info)
    return raw


def create_dummy_events(n_times, sfreq, event_ids=(1, 2)):
    """创建模拟事件数组。

    每秒产生一个事件，交替使用给定 event_id。

    Parameters
    ----------
    n_times : int
        总采样点数。
    sfreq : float
        采样率。
    event_ids : tuple
        事件 ID 列表。

    Returns
    -------
    events : ndarray, shape (n_events, 3)
    event_id : dict
    """
    onsets = np.arange(0, n_times, int(sfreq))
    ids = np.tile(event_ids, len(onsets) // len(event_ids) + 1)[:len(onsets)]
    durations = np.zeros(len(onsets), dtype=int)
    events = np.column_stack([onsets, durations, ids])

    event_id = {
        f"condition_{i}": i for i in event_ids
    }
    return events, event_id


def raw_to_epochs(
    raw,
    events,
    event_id,
    tmin=-0.2,
    tmax=0.8,
    baseline=(None, 0),
    reject=None,
):
    """从 Raw 和 Events 创建 Epochs。

    Parameters
    ----------
    raw : mne.io.Raw
    events : ndarray, shape (n_events, 3)
    event_id : dict
    tmin, tmax : float
        事件前后时间窗口 (秒)。
    baseline : tuple | None
        基线窗口。
    reject : dict | None
        拒绝阈值，如 dict(eeg=150e-6)。

    Returns
    -------
    epochs : mne.Epochs
    """
    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=baseline,
        preload=True,
        reject=reject,
        verbose=False,
    )
    return epochs


def epochs_to_evoked(epochs):
    """对每个条件分别平均，返回 Evoked 字典。

    Parameters
    ----------
    epochs : mne.Epochs

    Returns
    -------
    evoked_dict : dict of {condition_name: mne.Evoked}
    """
    evoked_dict = {}
    for cond in epochs.event_id:
        evoked_dict[cond] = epochs[cond].average()
    return evoked_dict


def plot_evoked_butterfly(evoked_dict):
    """绘制所有条件的蝴蝶图。

    Parameters
    ----------
    evoked_dict : dict of {name: mne.Evoked}
    """
    for name, evoked in evoked_dict.items():
        print(f"\n--- {name} ---")
        evoked.plot(spatial_colors=True)


# ============================================================
# 主入口：演示全流程
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-002 演示：Raw → Epochs → Evoked 全流程")
    print("=" * 60)

    # 1. 创建模拟数据
    raw = create_dummy_raw(n_channels=8, sfreq=250, duration=60)
    print(f"\n[1] Raw 创建成功: {raw}")

    # 2. 创建事件
    events, event_id = create_dummy_events(
        raw.n_times, raw.info["sfreq"], event_ids=(1, 2)
    )
    print(f"\n[2] Events 创建: {len(events)} 个事件, 映射={event_id}")

    # 3. 切分 Epochs
    epochs = raw_to_epochs(raw, events, event_id, tmin=-0.2, tmax=0.8)
    print(f"\n[3] Epochs 创建: {epochs}")

    # 4. 平均得到 Evoked
    evoked_dict = epochs_to_evoked(epochs)
    for name, ev in evoked_dict.items():
        print(f"\n[4] {name}: {ev}")

    print("\n全部完成。如需可视化，取消 plot_evoked_butterfly 的注释。")
    # plot_evoked_butterfly(evoked_dict)
