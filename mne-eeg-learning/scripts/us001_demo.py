"""
US-001: 环境搭建与初识 MNE — 可复用脚本

功能：
    1. 验证 MNE 安装
    2. 加载 sample 数据集
    3. 探索 Raw / Info / Annotations 对象
    4. 可视化 EEG 波形

使用方法：
    python scripts/us001_demo.py
"""

import os
import mne
from collections import Counter


def check_installation():
    """验证 MNE 是否安装成功，打印系统信息。"""
    print("=" * 60)
    print("MNE 系统信息")
    print("=" * 60)
    print(mne.sys_info())
    print()


def load_sample_data():
    """下载并加载 MNE sample 数据集。

    Returns
    -------
    raw : mne.io.Raw
        原始连续数据。
    sample_dir : Path
        数据所在目录。
    """
    # 目录配置
    data_dir = os.path.abspath("./../datasets")
    os.makedirs(data_dir, exist_ok=True)
    # 每次运行强制更新 config
    mne.set_config("MNE_DATA", data_dir)
    mne.set_config("MNE_DATASETS_SAMPLE_PATH", data_dir)
    print("=" * 80)
    print("config file =", mne.get_config_path())
    print("=" * 80)
    # 打印config 内容,友好格式
    config = mne.get_config()
    for key, value in config.items():
        print(f"* {key:25s}: {value}")

    sample_dir = mne.datasets.sample.data_path()
    raw_fname = sample_dir / "MEG" / "sample" / "sample_audvis_raw.fif"
    raw = mne.io.read_raw_fif(raw_fname, preload=False)
    return raw, sample_dir


def inspect_raw(raw):
    """打印 Raw 对象的关键信息。

    Parameters
    ----------
    raw : mne.io.Raw
    """
    print("=" * 60)
    print("Raw 对象概览")
    print("=" * 60)
    print(f"  通道数: {len(raw.ch_names)}")
    print(f"  采样率: {raw.info['sfreq']} Hz")
    print(f"  时长:   {raw.times[-1]:.1f} 秒")
    print(f"  前 10 个通道: {raw.ch_names[:10]}")
    print()


def inspect_info(raw: mne.io.Raw):
    """打印 Info 对象的通道类型分布和滤波设置。

    Parameters
    ----------
    raw : mne.io.Raw
    """
    print("=" * 60)
    print("Info 对象概览")
    print("=" * 60)
    info = raw.info
    print(f"  MNE 版本: {info.get('mne_version', 'unknown')}")
    print(f"  高通: {info['highpass']} Hz")
    print(f"  低通: {info['lowpass']} Hz")

    # 通道类型分布
    ch_types = raw.get_channel_types()
    print(f"  通道类型: {dict(Counter(ch_types))}")
    print()


def inspect_annotations(raw):
    """打印 Annotations 的概览信息。

    Parameters
    ----------
    raw : mne.io.Raw
    """
    print("=" * 60)
    print("Annotations 概览")
    print("=" * 60)
    print(f"  总数: {len(raw.annotations)}")
    if len(raw.annotations) > 0:
        print(f"  前 5 个:\n{raw.annotations[:5]}")
    print()


def quick_plot(raw, n_channels=10, duration=10):
    """快速绘制 EEG 通道波形。

    Parameters
    ----------
    raw : mne.io.Raw
    n_channels : int
        显示的通道数。
    duration : float
        显示的时间长度（秒）。
    """
    eeg_chs = [ch for ch in raw.ch_names if "EEG" in ch][:n_channels]
    raw_copy = raw.copy().pick(eeg_chs)
    raw_copy.plot(duration=duration, n_channels=n_channels, scalings="auto")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    check_installation()
    raw, sample_dir = load_sample_data()
    inspect_raw(raw)
    inspect_info(raw)
    inspect_annotations(raw)

    print("正在打开交互式波形浏览器...")
    # 取消下行注释即可在本地弹窗：
    quick_plot(raw)
    print("完成。如需交互式可视化，请取消 quick_plot(raw) 的注释。")
