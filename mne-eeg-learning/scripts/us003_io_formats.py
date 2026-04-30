"""
US-003: 多格式 EEG 数据导入与导出 — 可复用脚本

提供以下函数：
    read_raw_by_ext()      — 根据文件扩展名自动选择读取函数
    save_as_fif()          — 将 Raw 保存为标准 FIF 格式
    list_supported_formats() — 列出 MNE 支持的 EEG 格式
"""

import mne
from pathlib import Path


# ============================================================
# 格式-函数映射
# ============================================================
FORMAT_READERS = {
    ".fif":  mne.io.read_raw_fif,
    ".edf":  mne.io.read_raw_edf,
    ".bdf":  mne.io.read_raw_bdf,
    ".vhdr": mne.io.read_raw_brainvision,
    ".set":  mne.io.read_raw_eeglab,
    ".cnt":  mne.io.read_raw_cnt,
    ".gdf":  mne.io.read_raw_gdf,
}


def list_supported_formats():
    """列出当前 MNE 版本支持的 EEG 读取格式。"""
    print("MNE 支持的 EEG 数据格式：")
    for ext, func in FORMAT_READERS.items():
        print(f"  {ext:8s} → {func.__name__}")


def read_raw_by_ext(filepath, preload=True, **kwargs):
    """根据文件扩展名自动选择合适的 read_raw 函数。

    Parameters
    ----------
    filepath : str or Path
        文件路径。
    preload : bool
        是否加载到内存。
    **kwargs
        传递给对应 read_raw_xxx 的额外参数。

    Returns
    -------
    raw : mne.io.Raw
    """
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    if ext not in FORMAT_READERS:
        raise ValueError(
            f"不支持的格式 '{ext}'。支持的格式: {list(FORMAT_READERS.keys())}"
        )

    reader = FORMAT_READERS[ext]
    raw = reader(filepath, preload=preload, **kwargs)
    print(f"[OK] 已加载 {ext} 文件: {filepath.name}")
    return raw


def save_as_fif(raw, filepath, overwrite=True):
    """将 Raw 对象保存为 FIF 格式。

    Parameters
    ----------
    raw : mne.io.Raw
    filepath : str or Path
        输出路径（建议 .fif 扩展名）。
    overwrite : bool
        是否覆盖已有文件。
    """
    raw.save(filepath, overwrite=overwrite)
    print(f"[OK] 已保存: {filepath}")


def quick_info(raw, label=""):
    """快速打印 Raw 对象的关键信息。

    Parameters
    ----------
    raw : mne.io.Raw
    label : str
        标签前缀。
    """
    print(f"\n--- {label} ---")
    print(f"  通道数: {len(raw.ch_names)}")
    print(f"  采样率: {raw.info['sfreq']} Hz")
    print(f"  时长:   {raw.times[-1]:.1f} 秒")
    print(f"  前 5 通道: {raw.ch_names[:5]}")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    # 列出支持的格式
    list_supported_formats()
    # 设置路径
    from us000_path import set_datasets_path
    set_datasets_path()

    # --- 演示：加载 FIF 并另存 ---
    sample_dir = mne.datasets.sample.data_path()
    fif_path = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"

    print("\n" + "=" * 60)
    print("演示：FIF 读取 → 保存 → 重载")
    print("=" * 60)

    # 通过扩展名自动选择读取函数
    raw: mne.io.Raw = read_raw_by_ext(fif_path, preload=True)
    quick_info(raw, "原始 FIF")

    # 截取前 30 秒，只保留 EEG 通道
    eeg_raw: mne.io.Raw = raw.copy().pick_types(eeg=True).crop(tmin=0, tmax=30)
    save_as_fif(eeg_raw, "./mne-eeg-learning/outputs/us003_demo_output.fif")
    
    # 重载验证
    reloaded: mne.io.Raw = read_raw_by_ext("./mne-eeg-learning/outputs/us003_demo_output.fif", preload=True)
    quick_info(reloaded, "重载的 FIF（截取版）")
    

    print("\n全部完成。")
