"""
US-008: 公开数据集端到端实战 — 完整 Pipeline 脚本

以 BCI Competition IV Dataset 2a 为例。
使用前请先下载数据（MOABB 或手动下载 .gdf 文件）。

用法：
    python scripts/us008_end_to_end.py --data_dir ./data/BCICIV_2a/ --subject 1

依赖：
    pip install mne moabb
"""

import argparse
from pathlib import Path
import numpy as np
import mne


# ============================================================
# 配置
# ============================================================

# BCIC IV 2a 的 22 个 EEG 通道
BCI_CHANNELS = [
    "Fz", "FC3", "FC1", "FCz", "FC2", "FC4",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "CP3", "CP1", "CPz", "CP2", "CP4",
    "P1", "Pz", "P2", "POz",
]

EOG_CHANNELS = ["EOG-left", "EOG-central", "EOG-right"]

# 事件映射
EVENT_ID = {
    "left_hand": 769,
    "right_hand": 770,
    "feet": 771,
    "tongue": 772,
}

# 频段
FREQ_BANDS = {
    "alpha": (8, 13),
    "beta": (13, 30),
}


# ============================================================
# Pipeline 函数
# ============================================================

def load_bci_data(data_dir, subject, session="T"):
    """加载 BCIC IV 2a 数据。

    Parameters
    ----------
    data_dir : str or Path
    subject : int (1-9)
    session : str ('T' 训练, 'E' 测试)

    Returns
    -------
    raw : mne.io.Raw
    """
    data_dir = Path(data_dir)
    gdf_path = data_dir / f"A{subject:02d}{session}.gdf"
    if not gdf_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {gdf_path}")

    raw = mne.io.read_raw_gdf(gdf_path, preload=True)

    # 设置通道类型和蒙太奇
    eeg_chs = [ch for ch in raw.ch_names if ch in BCI_CHANNELS]
    eog_chs_in_file = [ch for ch in raw.ch_names if ch in EOG_CHANNELS]

    type_map = {ch: "eeg" for ch in eeg_chs}
    type_map.update({ch: "eog" for ch in eog_chs_in_file})
    raw.set_channel_types(type_map)

    # 设置蒙太奇
    montage = mne.channels.make_standard_montage("standard_1020")
    raw.set_montage(montage)

    print(f"[OK] 已加载: {gdf_path.name}")
    print(f"  EEG: {len(eeg_chs)} 通道, EOG: {len(eog_chs_in_file)} 通道")
    return raw


def preprocess_eeg(raw, notch_freq=50, l_freq=1, h_freq=40, target_sfreq=150):
    """预处理 EEG。

    Parameters
    ----------
    raw : mne.io.Raw
    notch_freq : float
    l_freq : float
    h_freq : float
    target_sfreq : float

    Returns
    -------
    raw : mne.io.Raw
    """
    raw = raw.copy()
    if notch_freq:
        raw.notch_filter(freqs=notch_freq)
    raw.filter(l_freq=l_freq, h_freq=h_freq)
    if target_sfreq:
        raw.resample(sfreq=target_sfreq)
    raw.set_eeg_reference(ref_channels="average")
    print(f"[OK] 预处理完成: {raw.info['highpass']}-{raw.info['lowpass']} Hz @ {raw.info['sfreq']} Hz")
    return raw


def remove_eog_ica(raw, n_components=20):
    """用 ICA 去除眼电。

    Parameters
    ----------
    raw : mne.io.Raw
    n_components : int

    Returns
    -------
    raw_clean : mne.io.Raw
    ica : mne.preprocessing.ICA
    """
    from mne.preprocessing import ICA

    picks = mne.pick_types(raw.info, eeg=True, eog=False)
    ica = ICA(n_components=n_components, method="fastica", random_state=42)
    ica.fit(raw, picks=picks)

    # 自动检测眼电成分
    eog_chs = [ch for ch in raw.ch_names if "eog" in ch.lower()]
    if eog_chs:
        eog_indices, _ = ica.find_bads_eog(raw, ch_name=eog_chs[0])
    else:
        eog_indices = []

    if eog_indices:
        raw_clean = raw.copy()
        ica.exclude = eog_indices
        ica.apply(raw_clean)
        print(f"[OK] ICA 排除了 {len(eog_indices)} 个眼电成分")
    else:
        raw_clean = raw.copy()
        print("[OK] 未检测到眼电成分，跳过 ICA")

    return raw_clean, ica


def epoch_data(raw, events, event_id, tmin=-0.5, tmax=2.5):
    """切分 Epochs。

    Parameters
    ----------
    raw : mne.io.Raw
    events : ndarray
    event_id : dict
    tmin, tmax : float

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
        baseline=(tmin, 0),
        preload=True,
        reject=dict(eeg=150e-6),
    )
    print(f"[OK] Epochs: {len(epochs)} trials 通过")
    return epochs


def analyze_erd_ers(epochs, condition, ch_name, freq_band="alpha"):
    """计算指定条件的 ERD/ERS。

    Parameters
    ----------
    epochs : mne.Epochs
    condition : str
    ch_name : str
    freq_band : str

    Returns
    -------
    power_avg : AverageTFR
    """
    from mne.time_frequency import tfr_morlet

    fmin, fmax = FREQ_BANDS[freq_band]
    freqs = np.logspace(*np.log10([fmin, fmax]), num=10)

    power = tfr_morlet(
        epochs[condition],
        freqs=freqs,
        n_cycles=freqs / 2.0,
        use_fft=True,
        return_itc=False,
        decim=3,
        n_jobs=1,
    )
    power_avg = power.average()
    return power_avg


def run_full_pipeline(data_dir, subject, session="T"):
    """运行完整分析流水线。

    返回所有中间结果供后续使用。
    """
    # 1. 加载
    raw = load_bci_data(data_dir, subject, session)

    # 2. 预处理
    raw = preprocess_eeg(raw)

    # 3. ICA
    raw, ica = remove_eog_ica(raw)

    # 4. 提取事件
    events = mne.find_events(raw, stim_channel="auto")
    print(f"[OK] 事件: {len(events)} 个, ID: {np.unique(events[:, 2])}")

    # 5. Epoching（只选左右手）
    event_id_subset = {k: v for k, v in EVENT_ID.items() if k in ["left_hand", "right_hand"]}
    epochs = epoch_data(raw, events, event_id_subset)

    # 6. ERP
    evoked_L = epochs["left_hand"].average()
    evoked_R = epochs["right_hand"].average()
    print(f"[OK] Evoked 计算完成")

    # 7. ERD/ERS
    power_L = analyze_erd_ers(epochs, "left_hand", "C3")
    power_R = analyze_erd_ers(epochs, "right_hand", "C4")
    print(f"[OK] ERD/ERS 计算完成")

    return raw, epochs, {"left": evoked_L, "right": evoked_R}, power_L, power_R


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BCIC IV 2a 端到端分析")
    parser.add_argument("--data_dir", required=True, help="数据目录")
    parser.add_argument("--subject", type=int, default=1, help="被试编号")
    parser.add_argument("--session", default="T", help="T=训练, E=测试")
    args = parser.parse_args()

    print("=" * 60)
    print(f"BCIC IV 2a 分析 — 被试 {args.subject} ({args.session})")
    print("=" * 60)

    raw, epochs, evoked_dict, power_L, power_R = run_full_pipeline(
        args.data_dir, args.subject, args.session
    )

    print("\n全部完成！")
    print(f"产出: raw, epochs, evoked_dict, power_L, power_R")
    print("使用 plot_compare / plot_tfr 等函数可视化结果。")
