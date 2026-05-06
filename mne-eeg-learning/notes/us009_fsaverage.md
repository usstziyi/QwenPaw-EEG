这三者的关系可以这样抓主线：

> **EEG 是“信号来源”，MRI 是“个体解剖地图”，fsaverage 是“没有个体 MRI 或做群体对齐时使用的标准解剖地图”。**

在 Source Localization 里，它们共同服务于一个目标：

$$
\mathbf{x}(t)
=============

\mathbf{L}\mathbf{s}(t)
+
\mathbf{n}(t)
$$

其中：

* $$\mathbf{x}(t)$$：EEG 通道记录到的头皮信号；
* $$\mathbf{s}(t)$$：大脑皮层源活动；
* $$\mathbf{L}$$：lead field / forward matrix；
* $$\mathbf{n}(t)$$：噪声。

MRI 或 fsaverage 的核心作用，就是帮助构建：

$$
\mathbf{L}
$$

---

# 1. EEG 是什么角色？

EEG 提供的是 **时间信号**。

比如你有 64 个 EEG 通道：

$$
\mathbf{x}(t)
=============

\begin{bmatrix}
x_1(t) \
x_2(t) \
\vdots \
x_{64}(t)
\end{bmatrix}
$$

这些信号来自头皮电极，例如：

```text
Fp1, Fp2, F3, F4, C3, C4, Cz, Pz, O1, O2 ...
```

EEG 本身知道：

```text
每个通道随时间变化的电压
```

但 EEG 本身不知道：

```text
大脑皮层在哪里
颅骨在哪里
脑源应该放在哪里
C3 下面具体对应哪块皮层
```

所以 EEG 需要一个空间结构来解释它。

---

# 2. MRI 是什么角色？

这里的 MRI 通常指 **被试自己的结构 MRI**，比如 T1 MRI。

它提供的是 **个体解剖结构**：

```text
头皮
颅骨
脑脊液
灰质
白质
皮层表面
脑沟脑回
```

MRI 的作用包括：

## 2.1 构建头模型

也就是：

```text
scalp
skull
brain
```

或者更精细的：

```text
scalp
skull
CSF
gray matter
white matter
```

这些组织决定脑内电流如何传播到头皮 EEG 电极。

---

## 2.2 构建源空间

MRI 可以重建皮层表面，然后在皮层上放很多候选源点：

$$
\mathbf{r}_1, \mathbf{r}_2, \cdots, \mathbf{r}_M
$$

这些源点构成：

$$
\text{source space}
$$

---

## 2.3 提供皮层法向方向

很多源定位方法会假设源方向垂直于皮层表面。

MRI 重建皮层表面后，可以得到每个源点的法向方向：

$$
\mathbf{n}_j
$$

于是第 $$j$$ 个源可以写成：

$$
\mathbf{q}_j(t)
===============

s_j(t)\mathbf{n}_j
$$

---

## 2.4 与 EEG 电极配准

EEG 电极位置需要和 MRI 对齐：

$$
\mathbf{e}_i^{MRI}
==================

\mathbf{T}_{head \rightarrow MRI}
\mathbf{e}_i^{head}
$$

这样软件才知道每个 EEG 电极相对于个体大脑的位置。

---

# 3. fsaverage 是什么角色？

**fsaverage** 是 FreeSurfer 提供的一个标准平均大脑模板。

可以把它理解为：

> 一个“标准人的 MRI + 皮层表面 + 脑区标注 + 源空间模板”。

它不是你的个体 MRI，而是许多人的平均脑模板。

在 MNE / FreeSurfer 体系里，fsaverage 常用于：

```text
没有个体 MRI 时，作为替代头模型
```

或者：

```text
把多个被试的源定位结果对齐到同一个标准脑上做群体分析
```

---

# 4. EEG、MRI、fsaverage 三者的关系

可以分两种场景理解。

---

# 场景 A：有个体 MRI

这是更理想的情况。

```text
EEG 数据
    +
个体 MRI
    ↓
个体化头模型
    ↓
个体化 source space
    ↓
EEG 电极与个体 MRI 配准
    ↓
计算 forward solution
    ↓
源定位
    ↓
如果要群体分析，再把结果 morph 到 fsaverage
```

也就是：

```text
EEG → 个体 MRI → 个体源定位 → fsaverage 群体对齐
```

在这个场景里：

| 对象        | 作用               |
| --------- | ---------------- |
| EEG       | 提供传感器时间信号        |
| 个体 MRI    | 提供该被试真实解剖结构      |
| fsaverage | 用于跨被试标准化 / 群体可视化 |

所以此时 fsaverage 不是源定位的主头模型，而是后期对齐用的标准空间。

---

# 场景 B：没有个体 MRI

这是 BCI 中很常见的情况。

```text
EEG 数据
    +
fsaverage 标准模板
    ↓
模板头模型
    ↓
模板 source space
    ↓
EEG 电极与模板头配准
    ↓
计算 forward solution
    ↓
模板源定位
```

也就是：

```text
EEG → fsaverage → 模板源定位
```

在这个场景里：

| 对象        | 作用                   |
| --------- | -------------------- |
| EEG       | 提供传感器时间信号            |
| 个体 MRI    | 没有                   |
| fsaverage | 代替个体 MRI 提供标准头模型和源空间 |

所以：

> 没有个体 MRI 时，fsaverage 可以充当“标准 MRI 替代品”。

---

# 5. 它们在 MNE 里的对应关系

在 MNE-Python 里通常有几个关键对象。

---

## 5.1 EEG 数据：raw / epochs / evoked

EEG 信号在：

```python
raw
epochs
evoked
```

里面。

例如：

```python
raw.info
```

里面包含：

```text
通道名
采样率
通道类型
电极坐标
参考信息
```

---

## 5.2 MRI 或 fsaverage：subject

在 MNE 里，不管是个体 MRI 还是 fsaverage，通常都作为一个 `subject`。

例如有个体 MRI：

```python
subject = "sub-01"
```

没有个体 MRI，用模板：

```python
subject = "fsaverage"
```

也就是说：

```text
subject 可以是个体 MRI，也可以是 fsaverage
```

---

## 5.3 MRI 文件所在目录：subjects_dir

FreeSurfer 处理后的 MRI 结构通常放在：

```python
subjects_dir
```

里面。

例如：

```text
subjects_dir/
    sub-01/
        bem/
        surf/
        mri/
        label/

    fsaverage/
        bem/
        surf/
        mri/
        label/
```

其中：

```text
surf/  存皮层表面
bem/   存头模型表面
mri/   存 MRI 图像
label/ 存脑区 parcellation
```

---

# 6. 三者如何共同生成 forward solution？

Forward solution 需要四类东西：

```text
1. EEG/MEG 通道信息
2. 电极位置
3. 头模型 BEM
4. 源空间 source space
```

对应到三者：

| forward 所需内容 | 来自哪里                             |
| ------------ | -------------------------------- |
| EEG 信号 / 通道名 | EEG raw.info                     |
| EEG 电极位置     | montage / digitizer              |
| 头模型          | 个体 MRI 或 fsaverage               |
| 源空间          | 个体 MRI 皮层或 fsaverage 皮层          |
| 坐标变换 trans   | EEG head 坐标与 MRI/fsaverage 坐标的配准 |

最终：

```python
fwd = mne.make_forward_solution(
    info=raw.info,
    trans=trans,
    src=src,
    bem=bem,
    eeg=True,
    meg=False
)
```

这里：

```text
raw.info  ← EEG
trans     ← EEG 与 MRI/fsaverage 的配准
src       ← MRI/fsaverage 生成的源空间
bem       ← MRI/fsaverage 生成的头模型
```

所以：

$$
\mathbf{L}
==========

f(
\text{EEG electrode positions},
\text{MRI/fsaverage head model},
\text{MRI/fsaverage source space}
)
$$

---

# 7. 一张关系图

```text
                 ┌────────────────────┐
                 │        EEG          │
                 │  头皮电极时间信号   │
                 └─────────┬──────────┘
                           │
                           │ raw.info + montage
                           │
                           ▼
                 ┌────────────────────┐
                 │ EEG 电极三维位置    │
                 └─────────┬──────────┘
                           │
                           │ trans / coregistration
                           ▼
┌─────────────────────────────────────────────────┐
│          MRI 空间 / fsaverage 空间              │
│                                                 │
│  ┌──────────────┐      ┌────────────────────┐   │
│  │ head model   │      │ source space       │   │
│  │ 头模型        │      │ 皮层源空间          │   │
│  └──────────────┘      └────────────────────┘   │
└─────────────────────────────────────────────────┘
                           │
                           │ make_forward_solution
                           ▼
                 ┌────────────────────┐
                 │ Lead Field Matrix  │
                 │        L           │
                 └─────────┬──────────┘
                           │
                           │ inverse operator
                           ▼
                 ┌────────────────────┐
                 │ source estimate    │
                 │ 源空间脑活动        │
                 └────────────────────┘
```

---

# 8. 重点区别：MRI 和 fsaverage 不是并列使用的同一种数据吗？

它们有点像，但层级不同。

## 个体 MRI

代表：

```text
这个被试自己的真实头和脑结构
```

优点：

```text
更准确
```

缺点：

```text
需要额外 MRI 扫描，成本高
```

---

## fsaverage

代表：

```text
标准平均脑模板
```

优点：

```text
方便，不需要个体 MRI
便于跨被试对齐
```

缺点：

```text
不是这个被试自己的真实大脑
定位精度下降
```

---

# 9. 一个容易混淆的点

不要把 fsaverage 理解成“另一个 EEG 数据”。

fsaverage 没有 EEG 信号。

fsaverage 只是：

```text
标准解剖结构
标准皮层表面
标准源空间
标准脑区标签
标准 BEM 头模型
```

它提供的是空间，不提供时间信号。

真正的时间信号仍然来自 EEG：

$$
\mathbf{x}(t)
$$

---

# 10. 如果有个体 MRI，还需要 fsaverage 吗？

需要，但用途不同。

## 做单被试源定位

只用个体 MRI 就可以：

```text
EEG + sub-01 MRI → sub-01 source estimate
```

---

## 做群体分析

不同人的脑形状不同，源空间顶点也不完全对应。

所以要把每个人的源结果 morph 到 fsaverage：

```text
sub-01 source estimate → fsaverage
sub-02 source estimate → fsaverage
sub-03 source estimate → fsaverage
```

然后才能比较：

```text
同一个标准脑区上的平均活动
```

所以：

```text
个体 MRI 用于精确定位
fsaverage 用于标准化和群体对齐
```

---

# 11. 没有个体 MRI 时，fsaverage 具体替代了什么？

它替代了：

```text
个体头模型
个体皮层表面
个体 source space
个体脑区 parcellation
```

但它不能替代：

```text
EEG 数据
EEG 电极真实位置
实验任务标签
时间序列
```

所以没有个体 MRI 时的流程是：

```text
raw EEG
    ↓
set montage
    ↓
对齐到 fsaverage 头模型
    ↓
使用 fsaverage BEM
    ↓
使用 fsaverage source space
    ↓
计算 forward solution
    ↓
计算 inverse solution
```

---

# 12. 最关键的三句话

## EEG

$$
\text{EEG} = \text{时间信号}
$$

它回答：

> 什么时候、哪个通道测到了什么电压变化？

---

## MRI

$$
\text{MRI} = \text{个体空间结构}
$$

它回答：

> 这个被试的大脑、头皮、颅骨、皮层在哪里？

---

## fsaverage

$$
\text{fsaverage} = \text{标准空间结构}
$$

它回答：

> 如果没有个体 MRI，或者需要跨被试比较，可以映射到哪个共同标准脑空间？

---

# 13. 一句话总结

Source Localization 中三者的关系是：

```text
EEG 提供传感器时间信号；
MRI 提供个体解剖空间；
fsaverage 提供标准模板空间。
```

更具体地说：

```text
有个体 MRI：
EEG + 个体 MRI → 个体源定位 → morph 到 fsaverage 做群体分析

没有个体 MRI：
EEG + fsaverage → 模板源定位
```

最终它们共同服务于：

$$
\mathbf{x}(t)
=============

\mathbf{L}\mathbf{s}(t)
+
\mathbf{n}(t)
$$

其中：

$$
\mathbf{L}
$$

由 MRI 或 fsaverage 提供的头模型、源空间，以及 EEG 电极位置共同决定。


---

因为 **MNE sample data 里的 `fsaverage` 不一定完整**，而 `mne.datasets.fetch_fsaverage()` 的目的不是“重复下载一个名字相同的目录”，而是：

> **检查当前 `subjects_dir/fsaverage` 是否包含 MNE 需要的完整 fsaverage 文件；如果缺文件，就补齐。**

MNE 官方文档说明：`fetch_fsaverage()` 会比较 `subjects_dir/fsaverage` 和远程 zip 中应有的文件；如果有缺失，就下载并更新，且不会覆盖已有文件。([mne.tools][1])

---

## 1. sample data 里的 `fsaverage` 是“样例数据附带的”

MNE sample data 主要服务于官方教程，例如：

```python
sample_data_path = mne.datasets.sample.data_path()
subjects_dir = sample_data_path / "subjects"
```

里面通常会有：

```text
subjects/
    sample/
    fsaverage/
```

其中：

```text
sample/
```

是真实的 sample 被试 MRI / BEM / surface 等。

```text
fsaverage/
```

是一个 FreeSurfer 标准平均脑模板，很多教程会用它做：

```python
subject="fsaverage"
```

但这个目录在 sample data 中可能不是最新、最完整的 fsaverage 发行版。

---

## 2. `fetch_fsaverage()` 下载的是 MNE 专门维护的完整 fsaverage

`fetch_fsaverage()` 会提供几类东西：

1. FreeSurfer 6 风格的现代 `fsaverage` subject 文件；
2. MNE 需要的 fsaverage parcellations；
3. fsaverage 的 head surface、fiducials、head↔MRI trans、1 层和 3 层 BEM 及其 surfaces。([mne.tools][2])

也就是说，它不仅仅是：

```text
surf/
mri/
label/
```

还包括 MNE 做前向建模、配准、模板源空间、BEM 时常用的额外文件。

---

## 3. 为什么你明明有 `fsaverage`，代码还要写这句？

常见原因有三个。

### 原因一：保证文件完整

比如你做：

```python
src = mne.setup_source_space(
    subject="fsaverage",
    spacing="oct6",
    subjects_dir=subjects_dir
)
```

或者：

```python
bem = mne.make_bem_solution(...)
```

或者用 fsaverage 做模板源定位、source morph、标准脑可视化。

这些操作可能需要：

```text
fsaverage/bem/
fsaverage/surf/
fsaverage/label/
fsaverage/mri/
fsaverage/bem/fsaverage-trans.fif
fsaverage/bem/inner_skull.surf
fsaverage/bem/outer_skull.surf
fsaverage/bem/outer_skin.surf
```

sample data 里的 `fsaverage` 如果少了某些文件，就会报错。

`fetch_fsaverage()` 就是为了自动补齐。

---

### 原因二：路径可能不是同一个

你看到的 sample data 里有：

```python
sample_data_path / "subjects" / "fsaverage"
```

但如果你直接写：

```python
fs_dir = mne.datasets.fetch_fsaverage(verbose=True)
```

而没有指定 `subjects_dir`，MNE 可能会下载到默认位置，比如：

```text
~/mne_data/MNE-fsaverage-data/fsaverage
```

也就是说，它不一定用 sample data 里的那个 `fsaverage`。

更明确的写法是：

```python
sample_data_path = mne.datasets.sample.data_path()
subjects_dir = sample_data_path / "subjects"

fs_dir = mne.datasets.fetch_fsaverage(
    subjects_dir=subjects_dir,
    verbose=True
)
```

这样它会检查：

```text
sample_data_path/subjects/fsaverage
```

如果缺文件，就在这个目录里补齐。

---

### 原因三：官方教程希望代码可复现

很多教程不假设你已经下载了完整 sample data，也不假设你本地的 `subjects_dir` 已经有完整 `fsaverage`。

所以会写：

```python
fs_dir = mne.datasets.fetch_fsaverage(verbose=True)
```

这样无论你本机有没有 `fsaverage`，代码都能继续跑。

---

## 4. 那如果我已经有 sample data 的 fsaverage，还需要运行吗？

**不一定需要。**

如果你只是使用 sample data 教程中的已有 forward、inverse、source estimate 文件，比如：

```text
sample_audvis-meg-oct-6-fwd.fif
sample_audvis-meg-oct-6-meg-inv.fif
```

通常不需要重新 fetch fsaverage。

但如果你要自己做：

```python
mne.setup_source_space(subject="fsaverage")
mne.make_bem_model(subject="fsaverage")
mne.make_forward_solution(...)
mne.compute_source_morph(...)
```

建议运行：

```python
fs_dir = mne.datasets.fetch_fsaverage(subjects_dir=subjects_dir)
```

它不会覆盖已有文件，只会补缺失文件。([mne.tools][1])

---

## 5. `fs_dir` 返回的是什么？

```python
fs_dir = mne.datasets.fetch_fsaverage(verbose=True)
```

返回的是：

```text
subjects_dir / "fsaverage"
```

也就是 `fsaverage` 这个 subject 的目录路径。MNE 文档中也说明，返回值本质上是 `subjects_dir / 'fsaverage'`。([GitHub][3])

例如：

```python
print(fs_dir)
```

可能输出：

```text
/Users/你的用户名/mne_data/MNE-fsaverage-data/fsaverage
```

或者如果你指定了：

```python
subjects_dir = sample_data_path / "subjects"
```

则可能是：

```text
.../MNE-sample-data/subjects/fsaverage
```

---

## 核心总结

可以这样理解：

```python
mne.datasets.sample.data_path()
```

下载的是 **MNE sample 示例数据集**。

```python
mne.datasets.fetch_fsaverage()
```

下载/检查/补齐的是 **标准模板脑 fsaverage**。

sample data 里面可能已经带了一个 `fsaverage`，但 `fetch_fsaverage()` 的作用是确保它满足当前 MNE 版本对模板脑、BEM、surface、label、trans 等文件的完整要求。它不是简单重复下载，而是做完整性检查和补齐。

[1]: https://mne.tools/stable/generated/mne.datasets.fetch_fsaverage.html?utm_source=chatgpt.com "mne.datasets.fetch_fsaverage — MNE 1.12.1 documentation"
[2]: https://mne.tools/1.1/generated/mne.datasets.fetch_fsaverage.html?utm_source=chatgpt.com "mne.datasets.fetch_fsaverage — MNE 1.1.1 documentation"
[3]: https://github.com/mne-tools/mne-python/blob/main/mne/datasets/_fsaverage/base.py?utm_source=chatgpt.com "mne-python/mne/datasets/_fsaverage/base.py at main"


---

在 MEG/EEG 源定位领域，**逆问题**根据求解方法不同，有多个具体名称：

---

## 核心名称体系

```
逆问题 (Inverse Problem / Inverse Solution)
│
├── 分布式源模型 (Distributed Source Model)
│   ├── 最小范数估计 (MNE / Minimum Norm Estimate)
│   ├── dSPM (Dynamic Statistical Parametric Mapping)
│   ├── sLORETA (Standardized Low-Resolution Electromagnetic Tomography)
│   ├── eLORETA (Exact Low-Resolution Electromagnetic Tomography)
│   ├── 混合范数估计 (Mixed Norm Estimate / MxNE)
│   ├── TV-L1 (Total Variation + L1)
│   └── 时空源分析 (Spatio-Temporal Source Analysis)
│
├── 偶极子拟合 (Dipole Fitting / ECD)
│   ├── 等效电流偶极子 (ECD / Equivalent Current Dipole)
│   ├── 移动偶极子 (Moving Dipole)
│   ├── 旋转偶极子 (Rotating Dipole)
│   └── 固定偶极子 (Fixed Dipole)
│
├── 扫描方法 (Scanning Methods / Spatial Filters)
│   ├── 波束形成器 (Beamformer)
│   │   ├── LCMV (Linearly Constrained Minimum Variance)
│   │   └── DICS (Dynamic Imaging of Coherent Sources)
│   └── MUSIC (Multiple Signal Classification)
│
└── 贝叶斯方法 (Bayesian Approaches)
    ├── 经验贝叶斯 (Empirical Bayes)
    ├── 变分贝叶斯 (Variational Bayes / VBMEG)
    └── 稀疏贝叶斯学习 (Sparse Bayesian Learning / SBL)
```

---

## MNE-Python 中的对应函数

```python
# 分布式逆解
inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, noise_cov, 
                                              method='MNE')   # 或 'dSPM', 'sLORETA', 'eLORETA'
stc = mne.minimum_norm.apply_inverse(raw, inv, method='MNE')

# 偶极子拟合
dip = mne.fit_dipole(evoked, cov, bem)

# 波束形成器
filters = mne.beamformer.make_lcmv(raw.info, fwd, data_cov)
stc = mne.beamformer.apply_lcmv(raw, filters)

# 混合范数
stc = mne.inverse_sparse.mixed_norm(evoked, fwd, noise_cov, alpha=0.1)
```

---

## 命名逻辑

所有方法都叫**逆问题**，因为它们都在求解：

```
y = Gx + ε
已知 y, G → 求 x
```

但根据**对 x 的先验假设**不同，分为：

| 方法类别 | 对 x 的假设 | 核心思想 |
|---------|------------|---------|
| **MNE** | x 能量最小 | `min ‖x‖²` + 数据拟合 |
| **dSPM** | x 归一化到噪声水平 | MNE / 噪声标准差 |
| **sLORETA** | x 归一化到定位误差 | 标准化分辨率矩阵 |
| **偶极子拟合** | x 只有极少非零 | 搜索1-3个偶极子位置 |
| **Beamformer** | x 源间时间独立 | 空间滤波，抑制其他源 |
| **MxNE** | x 稀疏且局部平滑 | `min ‖x‖₁` + 结构先验 |

---

## 学术论文中的叫法

论文标题通常这样写：

```
"Source localization using MNE"
"Solving the MEG inverse problem with dSPM"
"Cortical source imaging via sLORETA"
"Dipole modeling of auditory evoked fields"
"Beamformer analysis of oscillatory activity"
```

**日常交流中**，最常用的是：
- "做逆解" (solve the inverse)
- "计算 MNE/dSPM" 
- "跑源定位" (source localization)
- "源重建" (source reconstruction)
- "溯源" (source imaging)

---

## 核心区别图示

```
逆问题的两种思路：

分布式：                    偶极子：
"到处都有源，         vs    "只有几个源，
 我猜强度分布"              我找位置和方向"

    ⚫⚪⚪⚪                  ⚪⚪⚪⚪
    ⚫⚫⚪⚪                  ⚪⚪⚫⚪
    ⚪⚫⚪⚪                  ⚪⚪⚪⚪
    ⚪⚪⚪⚪                  ⚪⚫⚪⚪
    
源的数量 = 数千个            源的数量 = 1-3 个
```

---

所以，**逆问题的具体名字取决于你用的方法**，但所有这些统称为 **"源定位" (source localization)** 或 **"源重建" (source reconstruction)**。在 MNE 社区，最常见的四种是：**MNE, dSPM, sLORETA, eLORETA**。