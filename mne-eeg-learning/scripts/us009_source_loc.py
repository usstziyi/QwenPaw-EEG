"""
US-009: Source Localization 入门 — 可复用函数库

注意：首次运行需下载 fsaverage 模板（~400 MB）。

提供函数：
    prepare_fsaverage()     — 准备 fsaverage 模板
    setup_source_space()    — 创建源空间
    compute_forward()       — 计算前向解
    compute_inverse()       — 计算逆算子
    apply_source_recon()    — 应用源重建
    plot_source_activity()  — 在标准脑上绘制源活动
"""

import os
import os.path as op
from pathlib import Path
import mne



def prepare_fsaverage():
    """下载并返回 fsaverage 模板路径。

    Returns
    -------
    subjects_dir : str
    subject : str ('fsaverage')
    """
    subjects_dir = Path("../mne-eeg-learning/datasets/subjects").resolve() # 绝对路径
    print(f"subjects_dir: {subjects_dir}")

    fs_dir = mne.datasets.fetch_fsaverage(
        subjects_dir=subjects_dir,
        verbose=True
    )
    subjects_dir = op.dirname(fs_dir)
    return subjects_dir, "fsaverage"


def setup_source_space(subject, subjects_dir, spacing="ico4"):
    """创建皮层源空间。

    Parameters
    ----------
    subject : str
    subjects_dir : str
    spacing : str
        'ico4' (~5mm, 2562 顶点/半球), 'ico5' (~7mm), 'oct6' (~4.5mm)。

    Returns
    -------
    src : mne.SourceSpaces
    """
    src = mne.setup_source_space(
        subject,
        spacing=spacing,
        subjects_dir=subjects_dir,
        add_dist=False,
    )
    n_lh = len(src[0]["vertno"])
    n_rh = len(src[1]["vertno"])
    print(f"源空间: 左半球 {n_lh}, 右半球 {n_rh} → 共 {n_lh + n_rh} 个源")
    return src


def compute_forward(
    info,
    trans="fsaverage",
    src=None,
    bem=None,
    subject="fsaverage",
    subjects_dir=None,
    spacing="ico4",
    conductivity=(0.3, 0.006, 0.3),
):
    """计算前向解。

    Parameters
    ----------
    info : mne.Info
        通道信息（含 montage）。
    trans : str
        'fsaverage' 使用默认 trans，或提供 trans 文件路径。
    src : mne.SourceSpaces | None
        源空间。None 自动创建。
    bem : mne.BEM | None
        BEM 模型。None 自动创建。
    subject : str
    subjects_dir : str | None
    spacing : str
    conductivity : tuple
        电导率。

    Returns
    -------
    fwd : mne.Forward
    """
    if src is None:
        src = setup_source_space(subject, subjects_dir, spacing)

    if bem is None:
        model = mne.make_bem_model(
            subject, ico=4,
            conductivity=conductivity,
            subjects_dir=subjects_dir,
        )
        bem = mne.make_bem_solution(model)

    fwd = mne.make_forward_solution(
        info,
        trans=trans,
        src=src,
        bem=bem,
        eeg=True,
        mindist=5.0,
        n_jobs=1,
    )
    print(f"前向解: Gain 矩阵 {fwd['sol']['data'].shape}")
    return fwd


def compute_inverse(evoked, fwd, noise_cov, loose=0.2, depth=0.8):
    """计算逆算子。

    Parameters
    ----------
    evoked : mne.Evoked
    fwd : mne.Forward
    noise_cov : mne.Covariance
    loose : float
        源朝向自由度 (0=固定径向, 1=自由)。
    depth : float
        深度加权 (0=无, 1=完全)。

    Returns
    -------
    inv : mne.minimum_norm.InverseOperator
    """
    inv = mne.minimum_norm.make_inverse_operator(
        info=evoked.info, 
        forward=fwd, 
        noise_cov=noise_cov,
        loose=loose, 
        depth=depth,
    )
    print("逆算子计算完成")
    return inv


def apply_source_recon(evoked, inv, snr=3.0, method="sLORETA"):
    """应用源重建。

    Parameters
    ----------
    evoked : mne.Evoked
    inv : InverseOperator
    snr : float
        信噪比估计。
    method : str
        'MNE', 'dSPM', 'sLORETA'。

    Returns
    -------
    stc : mne.SourceEstimate
    """
    lambda2 = 1.0 / snr ** 2
    stc = mne.minimum_norm.apply_inverse(
        evoked=evoked, 
        inverse_operator=inv, 
        lambda2=lambda2, 
        method=method,
    )
    
    # 打印源时间过程（STC）的详细信息
    # stc.data.shape: 源空间顶点数 × 时间点数，表示每个源在每个时间点的活动强度
    # stc.times[0] 和 stc.times[-1]: 时间窗口的起始和结束时间（秒）
    print(f"{method} STC: {stc.data.shape} ({stc.times[0]:.2f} ~ {stc.times[-1]:.2f} s)")
    return stc


def plot_source_activity(
    stc,
    subject="fsaverage",
    subjects_dir=None,
    initial_time=None,
    hemi="both",
    views="lateral",
    time_viewer=True,
):
    """在标准脑上绘制源活动。

    Parameters
    ----------
    stc : mne.SourceEstimate
    subject : str
    subjects_dir : str | None
    initial_time : float | None
    hemi : str
    views : str | list
    time_viewer : bool

    Returns
    -------
    brain : mne.viz.Brain
    """
    if initial_time is None:
        initial_time = stc.times[len(stc.times) // 2]

    brain = stc.plot(
        subject=subject,
        subjects_dir=subjects_dir,
        hemi=hemi,
        views=views,
        time_viewer=time_viewer,
        initial_time=initial_time,
        clim="auto",
        background="white",
    )
    return brain


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("US-009 演示：Source Localization（需要 fsaverage）")
    print("=" * 60)

    # 准备 fsaverage 模板
    subjects_dir, subject = prepare_fsaverage()

    # 加载数据
    data_dir = os.path.abspath("./mne-eeg-learning/datasets")
    mne.set_config("MNE_DATA", data_dir)
    sample_dir = mne.datasets.sample.data_path()
    raw_fname = op.join(sample_dir, "MEG", "sample", "sample_audvis_raw.fif")
    raw = mne.io.read_raw_fif(raw_fname, preload=True).pick_types(
        eeg=True, stim=True
    )
    raw.set_eeg_reference(projection=True) # 重参考，应用投影器
    raw.filter(l_freq=1.0, h_freq=40.0)
   
    # 从刺激通道中提取事件标记
    events = mne.find_events(raw, stim_channel="STI 014")
    # 定义感兴趣的事件类型：左耳听觉刺激
    event_id = {"auditory/left": 1}
    # 创建 Epochs：分段、基线校正、预加载、拒绝坏段
    epochs = mne.Epochs(
        raw, events, event_id, tmin=-0.2, tmax=0.5,
        baseline=(None, 0), preload=True, reject=dict(eeg=150e-6),
    )
     # 平均左耳听觉刺激的ERP
    evoked = epochs["auditory/left"].average()

    print(f"\n数据就绪: {evoked}")

    # 噪声协方差
    noise_cov = mne.compute_covariance(
        epochs, tmin=-0.2, tmax=0.0, method="empirical",
    )

    # 前向解
    fwd = compute_forward(
        info=evoked.info,
        subject=subject,
        subjects_dir=subjects_dir,
    )

    # 逆问题，计算逆算子
    inv = compute_inverse(evoked, fwd, noise_cov)

    # 源重建
    # stc: Source Time Course 源时间过程
    stc = apply_source_recon(evoked, inv, method="sLORETA")

    print(f"\n源重建完成！")
    # 可视化源活动
    plot_source_activity(stc, subject, subjects_dir)
    print("\n按 Enter 关闭窗口...")
    input()
