"""
US-007: 时频分析与 ERP 可视化 — 可复用函数库

提供函数：
    compute_evoked()        — 计算 Evoked
    plot_butterfly()        — 蝴蝶图
    plot_topomap()          — 地形图
    plot_joint()            — 联合图
    plot_compare()          — 多条件对比
    compute_tfr()           — 时频分析 (Morlet)
    plot_tfr()              — 单通道时频图
    plot_tfr_diff()         — 条件间时频差异
"""

import numpy as np
import mne
from mne.time_frequency import tfr_morlet


def compute_evoked(epochs, condition):
    """计算某个条件的 Evoked。

    Parameters
    ----------
    epochs : mne.Epochs
    condition : str

    Returns
    -------
    evoked : mne.Evoked
    """
    return epochs[condition].average()


def plot_butterfly(evoked, title=""):
    """蝴蝶图：所有通道 ERP 叠加。

    Parameters
    ----------
    evoked : mne.Evoked
    title : str
    """
    fig = evoked.plot(spatial_colors=True, titles=title or "Butterfly Plot")
    return fig


def plot_topomap(evoked, times=None, ncols=3):
    """地形图：指定时间点的头皮电位分布。

    Parameters
    ----------
    evoked : mne.Evoked
    times : list | None
        时间点列表。None 自动选 6 个。
    ncols : int
    """
    if times is None:
        times = np.linspace(
            evoked.times[0] + 0.05, evoked.times[-1] - 0.05, 6
        )
    fig = evoked.plot_topomap(
        times=times, ch_type="eeg", time_unit="s", colorbar=True,
        ncols=ncols, nrows="auto",
    )
    return fig


def plot_joint(evoked, title=""):
    """Joint Plot：单通道 ERP + 峰值地形图。

    Parameters
    ----------
    evoked : mne.Evoked
    title : str
    """
    fig = evoked.plot_joint(times="peaks", title=title or "Joint Plot")
    return fig


def plot_compare(evoked_dict, picks="eeg", combine="mean", ci=0.95):
    """多条件 ERP 对比图。

    Parameters
    ----------
    evoked_dict : dict of {name: mne.Evoked}
    picks : str | list
    combine : str
        'mean' 或 None。
    ci : float | bool
        置信区间。
    """
    fig = mne.viz.plot_compare_evokeds(
        evoked_dict,
        picks=picks,
        combine=combine,
        legend="upper right",
        show_sensors="upper left",
        ci=ci,
        truncate_yaxis="auto",
    )
    return fig


def compute_tfr(
    epochs,
    freqs=None,
    n_cycles=None,
    method="morlet",
    decim=3,
    n_jobs=1,
):
    """计算时频表示 (TFR)。

    Parameters
    ----------
    epochs : mne.Epochs
    freqs : ndarray | None
        频率列表。None 自动生成 4-30 Hz。
    n_cycles : float | ndarray | None
        小波周期数。None 自动 = freqs/2。
    method : str
        'morlet' 或 'multitaper'。
    decim : int
        时间降采样因子。
    n_jobs : int
        并行数。

    Returns
    -------
    power : mne.time_frequency.AverageTFR
    """
    if freqs is None:
        freqs = np.logspace(*np.log10([4, 30]), num=20)
    if n_cycles is None:
        n_cycles = freqs / 2.0

    if method == "morlet":
        power = tfr_morlet(
            epochs,
            freqs=freqs,
            n_cycles=n_cycles,
            use_fft=True,
            return_itc=False,
            decim=decim,
            n_jobs=n_jobs,
        )
    else:
        raise NotImplementedError("目前仅支持 'morlet'")

    print(f"TFR 计算完成: {power.data.shape}")
    return power


def plot_tfr(
    power,
    picks=None,
    baseline=(None, 0),
    mode="logratio",
    title="Time-Frequency",
):
    """单通道时频图。

    Parameters
    ----------
    power : AverageTFR
    picks : str | list | None
    baseline : tuple
    mode : str
        'logratio', 'percent', 'mean', 'zscore'。
    title : str
    """
    if picks is None:
        picks = power.ch_names[0]
    fig = power.plot(
        picks=picks,
        baseline=baseline,
        mode=mode,
        title=title,
        colorbar=True,
    )
    return fig


def plot_tfr_diff(power1, power2, picks=None, baseline=(None, 0)):
    """两条件时频差异图。

    Parameters
    ----------
    power1, power2 : AverageTFR
    picks : str | list | None
    baseline : tuple
    """
    power_diff = power1 - power2
    if picks is None:
        picks = power_diff.ch_names[0]
    fig = power_diff.plot(
        picks=picks,
        baseline=baseline,
        mode="logratio",
        title="TFR Difference",
        colorbar=True,
    )
    return fig


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-007 演示：ERP 可视化与时频分析")
    print("=" * 60)

    # 快速演示（不实际绘图，仅数据准备）
    sample_dir = mne.datasets.sample.data_path()
    raw_fname = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"
    raw = mne.io.read_raw_fif(raw_fname, preload=True).pick_types(eeg=True, stim=True)
    raw.filter(l_freq=1.0, h_freq=40.0)

    events = mne.find_events(raw, stim_channel="STI 014")
    event_id = {"auditory/left": 1, "auditory/right": 2}

    epochs = mne.Epochs(
        raw, events, event_id=event_id,
        tmin=-0.5, tmax=1.0, baseline=(None, 0),
        preload=True, reject=dict(eeg=150e-6),
    )

    print(f"\n{epochs}")
    print("数据就绪。取消代码中对应函数的注释即可绘图。")
