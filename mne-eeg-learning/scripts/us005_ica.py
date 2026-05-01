"""
US-005: ICA 伪迹去除 — 可复用函数库

提供函数：
    fit_ica()              — 拟合 ICA
    detect_eog_components()— 自动检测眼电成分
    detect_ecg_components()— 自动检测心电成分
    apply_ica_cleaning()   — 应用 ICA 清洗数据
    ica_pipeline()         — 一键 ICA 去眼电
"""

import mne
from mne.preprocessing import ICA


def fit_ica(
    raw,
    picks=None,
    n_components=20,
    method="fastica",
    random_state=42,
    fit_params=None,
):
    """拟合 ICA 模型。

    Parameters
    ----------
    raw : mne.io.Raw
        预处理后的数据（必须已高通滤波 ≥1 Hz）。
    picks : list | None
        用于 ICA 的通道索引。默认自动选择 EEG 通道。
    n_components : int | float
        成分数。int=固定数量，float(0-1)=解释方差比例。
    method : str
        'fastica', 'picard', 'infomax'。
    random_state : int
        随机种子。
    fit_params : dict | None
        额外参数如 dict(extended=True)。

    Returns
    -------
    ica : mne.preprocessing.ICA
    picks : list
    """
    if picks is None:
        picks = mne.pick_types(raw.info, eeg=True, eog=False, ecg=False)

    # 初始化 ICA 模型
    ica = ICA(
        n_components=n_components,
        method=method,
        random_state=random_state,
        max_iter="auto",
        fit_params=fit_params,
    )
    # 拟合 ICA 模型
    ica.fit(raw, picks=picks)
    print(f"ICA 拟合完成: {ica.n_components_} 个成分")
    return ica, picks


def detect_eog_components(ica, raw, eog_ch=None, threshold=3.0):
    """自动检测眼电成分。

    Parameters
    ----------
    ica : ICA
    raw : mne.io.Raw
    eog_ch : str | None
        EOG 通道名。None 时自动找 EOG 类型通道。
    threshold : float
        Z-score 阈值。

    Returns
    -------
    eog_indices : list
    eog_scores : ndarray
    """
    eog_indices, eog_scores = ica.find_bads_eog(
        raw, ch_name=eog_ch, threshold=threshold
    )
    print(f"检测到 {len(eog_indices)} 个眼电成分: {eog_indices}")
    return eog_indices, eog_scores


def detect_ecg_components(ica, raw, ecg_ch=None, threshold=3.0):
    """自动检测心电成分。

    Parameters
    ----------
    ica : ICA
    raw : mne.io.Raw
    ecg_ch : str | None
        ECG 通道名。
    threshold : float
        Z-score 阈值。

    Returns
    -------
    ecg_indices : list
    ecg_scores : ndarray
    """
    ecg_indices, ecg_scores = ica.find_bads_ecg(
        raw, ch_name=ecg_ch, threshold=threshold
    )
    print(f"检测到 {len(ecg_indices)} 个心电成分: {ecg_indices}")
    return ecg_indices, ecg_scores


def apply_ica_cleaning(ica, raw, exclude_indices):
    """应用 ICA 去除指定成分并重建信号。

    Parameters
    ----------
    ica : ICA
    raw : mne.io.Raw
        原始数据（副本）。会被原地修改。
    exclude_indices : list
        要排除的成分索引。

    Returns
    -------
    raw : mne.io.Raw（原地修改后返回）
    """
    ica.exclude = exclude_indices
    ica.apply(raw)
    print(f"已排除 {len(exclude_indices)} 个成分，信号已重建")
    return raw


def ica_pipeline(raw, eog_ch=None, n_components=20, method="fastica"):
    """一键 ICA 去眼电流水线。

    注意：raw 必须已高通滤波（≥1 Hz）。

    Parameters
    ----------
    raw : mne.io.Raw
    eog_ch : str | None
    n_components : int
    method : str

    Returns
    -------
    raw_clean : mne.io.Raw
    ica : ICA
    """
    # 1. 拟合 ICA
    ica, picks = fit_ica(raw, n_components=n_components, method=method)

    # 2. 检测眼电成分
    if eog_ch is None:
        eog_names = [
            ch for ch in raw.ch_names
            if "eog" in ch.lower() or "EOG" in ch
        ]
        eog_ch = eog_names[0] if eog_names else None

    if eog_ch:
        eog_indices, _ = detect_eog_components(ica, raw, eog_ch=eog_ch)
    else:
        print("⚠ 未找到 EOG 通道，请手动查看 ica.plot_components() 选择")
        eog_indices = []

    # 3. 去除眼电成分
    if eog_indices:
        raw_clean = raw.copy()
        apply_ica_cleaning(ica, raw_clean, eog_indices)
    else:
        raw_clean = raw.copy()

    return raw_clean, ica


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-005 演示：ICA 去眼电")
    print("=" * 60)

    from us000_path import set_datasets_path
    set_datasets_path()


    # 加载数据
    sample_dir = mne.datasets.sample.data_path()
    raw_fname = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"
    raw = mne.io.read_raw_fif(raw_fname, preload=True)
    raw.pick_types(eeg=True, eog=True)

    # 高通滤波（ICA 前提）
    raw.filter(l_freq=1.0, h_freq=None)
    print(f"\n数据就绪: {raw}")

    # 运行 ICA pipeline
    raw_clean, ica = ica_pipeline(raw, n_components=20)

    print(f"\n清洗后: {raw_clean}")
    print("全部完成。")
