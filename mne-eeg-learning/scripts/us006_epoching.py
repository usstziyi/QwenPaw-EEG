"""
US-006: 事件提取与 Epoching — 可复用函数库

提供函数：
    extract_events()       — 从 Stim 通道提取事件
    create_epochs()        — 创建 Epochs 对象
    equalize_conditions()  — 平衡条件间 trial 数
    compare_conditions()   — 快速对比多条件 ERP
"""

import numpy as np
import mne


def extract_events(
    raw,
    stim_channel="STI 014",
    mask=None,
    mask_type="not_and",
    min_duration=0,
):
    """从 Stim 通道提取事件。

    Parameters
    ----------
    raw : mne.io.Raw
    stim_channel : str
        Stim 通道名，'auto' 自动选择。
    mask : int | None
        事件 ID 掩码，如 32 保留 response 相关事件。
    mask_type : str
        'and'（保留匹配的）或 'not_and'（排除匹配的）。
    min_duration : int
        最短事件持续采样点数。

    Returns
    -------
    events : ndarray, shape (n_events, 3)
    """
    events = mne.find_events(
        raw,
        stim_channel=stim_channel,
        mask=mask,
        mask_type=mask_type,
        min_duration=min_duration,
        output="onset",
        consecutive=True,
        shortest_event=2,
    )
    print(f"提取到 {len(events)} 个事件, ID: {np.unique(events[:, 2])}")
    return events


def create_epochs(
    raw,
    events,
    event_id,
    tmin=-0.2,
    tmax=0.8,
    baseline=(None, 0),
    reject=None,
    flat=None,
):
    """从 Raw 和 Events 创建 Epochs。

    Parameters
    ----------
    raw : mne.io.Raw
    events : ndarray
    event_id : dict
    tmin, tmax : float
    baseline : tuple | None
    reject : dict | None
        如 dict(eeg=150e-6)。
    flat : dict | None
        如 dict(eeg=1e-6)。

    Returns
    -------
    epochs : mne.Epochs
    """
    kwargs = dict(
        tmin=tmin,
        tmax=tmax,
        baseline=baseline,
        preload=True,
    )
    if reject:
        kwargs["reject"] = reject
    if flat:
        kwargs["flat"] = flat

    epochs = mne.Epochs(raw, events, event_id=event_id,  verbose=False, **kwargs)
    kept_pct = len(epochs) / max(1, len(events)) * 100
    print(f"Epochs 创建: {len(epochs)} 个通过 ({kept_pct:.1f}%)")
    return epochs


def equalize_conditions(epochs, event_ids=None, method="mintime"):
    """平衡条件间 trial 数。

    Parameters
    ----------
    epochs : mne.Epochs
    event_ids : list | None
        参与平衡的条件名列表。None 为全部。
    method : str
        'mintime' 随机下采样；'truncate' 截断。

    Returns
    -------
    epochs : mne.Epochs（原地修改）
    """
    epochs.equalize_event_counts(event_ids=event_ids, method=method)
    for cond in epochs.event_id:
        print(f"  {cond}: {len(epochs[cond])} trials")
    return epochs


def compare_conditions(epochs, conditions, picks=None):
    """快速对比多条件 ERP。

    Parameters
    ----------
    epochs : mne.Epochs
    conditions : list of str
    picks : list | None

    Returns
    -------
    evoked_dict : dict
    """
    evoked_dict = {}
    for cond in conditions:
        evoked_dict[cond] = epochs[cond].average()
        if picks:
            evoked_dict[cond] = evoked_dict[cond].pick(picks)

    fig = mne.viz.plot_compare_evokeds(
        evoked_dict,
        legend="upper right",
        show_sensors="upper left",
    )
    return evoked_dict


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-006 演示：事件提取与 Epoching")
    print("=" * 60)

    from us000_path import set_datasets_path
    set_datasets_path()

    # 加载数据
    sample_dir = mne.datasets.sample.data_path()
    raw_fname = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"
    raw = mne.io.read_raw_fif(raw_fname, preload=True).pick_types(
        eeg=True, stim=True
    )

    # 事件
    events = extract_events(raw, stim_channel="STI 014")

    # 事件映射
    event_id = {
        "auditory/left": 1,
        "visual/left": 3,
    }
    print(f"\n事件映射: {event_id}")

    # 创建 Epochs
    epochs = create_epochs(
        raw,
        events,
        event_id,
        tmin=-0.2,
        tmax=0.8,
        baseline=(None, 0),
        reject=dict(eeg=150e-6),
    )
    print(f"\n{epochs}")

    # 平衡条件间 trial 数
    equalize_conditions(epochs, event_ids=event_id.keys())

    print(event_id.keys())

    # 对比条件 ERP
    compare_conditions(epochs, event_id.keys())

    print("\n全部完成。")
