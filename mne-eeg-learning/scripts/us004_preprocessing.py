"""
US-004: EEG 预处理 — 可复用函数库

提供函数：
    apply_notch()           — 陷波滤波（去工频）
    apply_bandpass()        — 带通滤波
    apply_resample()        — 降采样
    apply_rereference()     — 重参考
    apply_interpolate_bads()— 坏导插值
    preprocess_pipeline()   — 一键预处理
"""

import mne


def apply_notch(raw, freqs=50.0):
    """陷波滤波，去除工频干扰。

    Parameters
    ----------
    raw : mne.io.Raw
    freqs : float | list
        陷波频率，中国/欧洲=50，北美=60。

    Returns
    -------
    raw : mne.io.Raw（原地修改）
    """
    raw.notch_filter(freqs=freqs)
    return raw


def apply_bandpass(raw, l_freq=1.0, h_freq=40.0, **kwargs):
    """带通滤波。

    Parameters
    ----------
    raw : mne.io.Raw
    l_freq : float | None
        高通截止频率 (Hz)。None 表示不高通。
    h_freq : float | None
        低通截止频率 (Hz)。None 表示不低通。
    **kwargs
        传递给 raw.filter() 的额外参数。
    """
    raw.filter(l_freq=l_freq, h_freq=h_freq, **kwargs)
    return raw


def apply_resample(raw, sfreq=150.0):
    """降采样。

    注意：调用前应先低通滤波，确保 sfreq 满足 Nyquist 定理。

    Parameters
    ----------
    raw : mne.io.Raw
    sfreq : float
        目标采样率 (Hz)。
    """
    raw.resample(sfreq=sfreq)
    return raw


def apply_rereference(raw, ref_channels="average"):
    """重参考。

    Parameters
    ----------
    raw : mne.io.Raw
    ref_channels : str | list
        'average' 为平均参考；或通道名列表如 ['M1', 'M2']。
    """
    raw.set_eeg_reference(ref_channels=ref_channels)
    return raw


def apply_interpolate_bads(raw, reset_bads=True):
    """插值坏导。

    Parameters
    ----------
    raw : mne.io.Raw
    reset_bads : bool
        插值后是否清除 bads 列表。
    """
    raw.interpolate_bads(reset_bads=reset_bads)
    return raw


def preprocess_pipeline(
    raw,
    notch_freqs=50.0,
    l_freq=1.0,
    h_freq=40.0,
    target_sfreq=150.0,
    ref_channels="average",
    interpolate=True,
):
    """标准 EEG 预处理流水线（返回副本，不修改原始 raw）。

    步骤：
        1. 陷波去工频
        2. 带通滤波
        3. 降采样
        4. 重参考
        5. 坏导插值（可选）

    Parameters
    ----------
    raw : mne.io.Raw
        原始数据（不会被修改）。
    notch_freqs : float | list
        工频频率。
    l_freq : float | None
        高通截止频率。
    h_freq : float | None
        低通截止频率。
    target_sfreq : float
        目标采样率。
    ref_channels : str | list
        参考方式。
    interpolate : bool
        是否插值坏导。

    Returns
    -------
    raw_clean : mne.io.Raw
    """
    raw_clean = raw.copy()

    # 1. 陷波
    if notch_freqs:
        apply_notch(raw_clean, freqs=notch_freqs)

    # 2. 带通
    if l_freq or h_freq:
        apply_bandpass(raw_clean, l_freq=l_freq, h_freq=h_freq)

    # 3. 降采样
    if target_sfreq and target_sfreq != raw_clean.info["sfreq"]:
        apply_resample(raw_clean, sfreq=target_sfreq)

    # 4. 重参考
    if ref_channels:
        apply_rereference(raw_clean, ref_channels=ref_channels)

    # 5. 坏导插值
    if interpolate and raw_clean.info["bads"]:
        apply_interpolate_bads(raw_clean)

    return raw_clean


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-004 演示：预处理 Pipeline")
    print("=" * 60)

    from us000_path import set_datasets_path
    set_datasets_path()

    # 加载数据
    sample_dir = mne.datasets.sample.data_path()
    raw_fname = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"
    raw = mne.io.read_raw_fif(raw_fname, preload=True).pick_types(eeg=True)

    print(f"\n原始数据: {raw}")
    print(f"  采样率: {raw.info['sfreq']} Hz")
    print(f"  滤波:   {raw.info['highpass']}-{raw.info['lowpass']} Hz")

    # 运行预处理
    raw_clean = preprocess_pipeline(
        raw,
        notch_freqs=None,      # sample 数据采样率 600Hz，没有 50Hz 干扰
        l_freq=1.0,
        h_freq=40.0,
        target_sfreq=150.0,
        ref_channels="average",
        interpolate=False,     # sample 数据没有坏导
    )

    print(f"\n预处理后: {raw_clean}")
    print(f"  采样率: {raw_clean.info['sfreq']} Hz")
    print(f"  滤波:   {raw_clean.info['highpass']}-{raw_clean.info['lowpass']} Hz")

    print("\n全部完成。")
