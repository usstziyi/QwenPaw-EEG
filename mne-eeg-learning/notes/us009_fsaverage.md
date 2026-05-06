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
