# A线导师档案 03｜李文彬（Wenbin Li）

> 用途：西湖大学 A 线申请内部工作文档。用于后续查阅、套磁、材料定制、面试准备与最终决策。  
> 更新日期：2026-09-26  
> 状态：**A-/B+｜核心候选保留｜建议第二批联系｜2027具体名额待确认**

---

# 0. 一句话结论

李文彬是当前西湖 A 线中“第一性原理 + 电子结构 + 半导体/功能材料 + 机器学习”这一方向非常扎实的 PI。

与朱一舟、刘仕相比，他的研究更明显地以：

> **电子结构、电子-声子相互作用、半导体输运与功能材料物理**

为主轴，机器学习是重要工具，但并不是课题组全部研究的中心。

因此，对申请者而言：

> 如果未来希望成为一个**电子结构 / 半导体计算物理研究者，并把 ML 作为加速工具**，李文彬很值得申请；  
> 如果更希望博士阶段直接把 AI4Science 放在研究核心，朱一舟或刘仕目前更优先。

当前最重要的现实信息是：

> 李文彬是工学院材料科学与工程系核心 PI，同时兼任理学院物理系导师；实际博士申请大概率应走**工学院材料科学与工程学科**，而不是物理学学科。

这会直接影响申请材料和面试形式。

---

# 1. PI 基本信息

- 姓名：李文彬 / Wenbin Li
- 单位：西湖大学工学院
- 兼任：理学院物理系
- 学科：Materials Science and Engineering / Physics
- 实验室：Materials Modeling and Design Lab
- 职称：副教授（2025 起）
- 2019 年加入西湖大学
- 本科：浙江大学，材料科学与工程
- 硕士：University of Pennsylvania，材料科学与工程
- 博士：MIT，材料科学与工程
- 博后：MIT Research Laboratory of Electronics
- Marie Curie Fellow：University of Oxford
- 曾获工学院教学优秀奖

官方主页：
https://en.westlake.edu.cn/faculty/wenbin-li.html

---

# 2. 研究方向画像

官方页面目前列出的三条主线是：

1. **Electron-phonon interactions in complex electronic materials**
2. **Modeling and design of advanced semiconductors**
3. **Machine learning for accelerated materials design**

总体方法是：

> quantum-mechanical calculations  
> + atomistic simulations  
> + machine learning

目标是：

> 理解复杂功能材料中的 structure-property relationships，并加速新材料设计。

从近年论文看，课题组真实重心可以更具体地拆成四块：

### A. 电子结构与输运

- carrier mobility
- electron-phonon interaction
- quantum geometry
- semiconductor transport
- dielectric response

### B. 二维 / 一维半导体与低维材料

- Bi2O2Se
- layered semiconductors
- MoS2 nanotubes
- helical 1D crystals
- strain engineering

### C. 铁电与极化物理

- strain-induced ferroelectricity
- highly polarizable semiconductors
- layered ferroelectric materials

### D. ML-assisted materials modeling

- ML interatomic potential
- deep-learning electronic structure
- accelerated mapping of large structural / chirality spaces

---

# 3. 这个组的真实研究风格

最准确的定义不是：

> “AI 材料组”

而是：

> **first-principles electronic materials physics + data-driven acceleration**

也就是说，核心仍然是：

> 电子结构、声子、输运、极化、材料物理机制

ML 的角色通常是：

> 让原本需要大量 DFT 计算才能覆盖的结构空间、尺寸空间或手性空间变得可扫描和可预测。

这与朱一舟的：

> AI for Materials Discovery

以及刘仕的：

> DFT → ML potential → large-scale MD → multiscale physics

都有明显差异。

---

# 4. 三篇最具代表性的近期工作

## 4.1 Quantum Geometry in Phonon-Mediated Optical Responses  
Physical Review Letters 135, 256404 (2025)

核心问题：

传统量子几何通常只考虑固定晶格下的电子 Hilbert space，但真实材料中电子与声子发生耦合。

该工作建立了：

> electron-phonon coupling quantum geometry

研究：

- EPC quantum metric
- EPC Berry curvature
- EPC shift vector

并将这些量与：

> phonon-mediated optical responses

连接起来。

### 对申请者意味着什么

这篇论文说明：

> 李文彬组并不是只做“材料数据库 + ML”。

其理论深度可以直接进入：

- quantum mechanics
- solid-state physics
- electron-phonon coupling
- Berry phase / quantum geometry

因此这个组对理论基础的要求会比“AI 工具型材料组”明显更高。

这也是申请者当前最大的适配风险之一。

---

## 4.2 An Atlas of Chirality-Dependent Electronic Structures of MoS2 Nanotubes from Deep Learning  
ACS Nano 20, 565–574 (2026)

这是目前最能体现李文彬组“ML + electronic structure”路线的一篇。

核心问题：

MoS2 nanotube 的电子性质同时依赖：

- tube diameter
- chirality
- curvature

整个 chirality space 非常大，如果每个结构都直接做完整 DFT，计算成本高。

方法：

> ML interatomic potential  
> + deep-learning DFT / electronic-structure model

建立完整的：

> chirality-dependent electronic structure atlas

预测：

- bandgap
- carrier effective mass
- direct / indirect bandgap

并发现小直径区域 hole effective mass 的明显跃迁。

Supporting Information 显示实际使用和比较了：

- VASP
- OpenMX
- CHGNet
- DeepH-E3

### 对申请者意味着什么

这一条与申请者长期目标非常相关：

> 不只是让 AI “猜一个材料性质”，而是用 ML 扩大电子结构计算能够覆盖的设计空间。

与本科毕业设计的方法论连接可以写成：

> CST forward simulation + GA search  
> ↓  
> 大量结构空间的自动探索

进一步升级为：

> atomistic structure  
> + ML-relaxed structure  
> + deep-learning electronic structure  
> + large-scale design-space mapping

这是申请者与李文彬最自然的连接点。

---

## 4.3 Giant Polarizability and Origin of Ferroelectricity in Layered Materials with a Litharge-Type Structural Unit  
Nano Letters 25, 4093–4100 (2025)

核心方法：

> first-principles calculations

研究一类层状半导体为什么具有异常大的极化率，并在应变下接近或进入铁电相。

结论重点不是模型预测，而是：

> 通过电子结构分析解释材料高极化率与铁电性的统一微观起源。

### 对申请者意味着什么

这篇论文说明：

> 即使没有 ML，李文彬组仍然会做大量纯粹的第一性原理材料物理问题。

如果进入这个组，博士训练很可能首先要求真正掌握：

- electronic structure
- DFT
- polarization
- dielectric response
- band structure
- orbital hybridization

而不是一入组就主要做深度学习。

---

# 5. 最新研究趋势判断

从 2025–2026 工作看，李文彬组正在同时加强两条路线。

## 路线一：更深入的电子材料物理

代表：

- electron-phonon quantum geometry
- carrier mobility
- ferroelectricity
- layered semiconductors
- quantum optical response

说明：

> 理论和第一性原理物理深度仍然是实验室核心竞争力。

## 路线二：ML 加速电子结构

代表：

> MoS2 nanotube electronic-structure atlas

这里不是简单材料属性回归，而是把：

- ML potential
- deep-learning Hamiltonian / electronic-structure model
- DFT validation

结合起来。

因此，可以期待未来组内继续出现：

> first-principles + ML surrogate / foundation atomistic models / learned electronic structure

这一类研究。

---

# 6. 与申请者的匹配点

## 6.1 计算导向高度匹配

申请者明确希望：

> 主要从事计算研究，而非纯实验。

李文彬组的核心方法几乎全部为：

- DFT
- atomistic simulation
- electronic structure
- numerical modeling
- machine learning

这一点高度匹配。

---

## 6.2 本科毕业设计有合理迁移逻辑

申请者已有：

> physical forward simulator  
> + Python automation  
> + optimization / search

李文彬组是：

> quantum-mechanical forward model  
> + materials modeling  
> + ML acceleration / design

因此可以形成：

> electromagnetic-scale computational design  
> → atomistic-scale materials modeling  
> → ML-accelerated electronic-structure design

的连续叙事。

---

## 6.3 物理本科身份并不违和

李文彬虽然主要在工学院材料系，但同时是理学院物理系 affiliated faculty。

其研究内容本身大量涉及：

- condensed-matter physics
- quantum mechanics
- electron-phonon coupling
- transport
- polarization

因此应用物理本科申请并不存在方向身份上的明显冲突。

---

# 7. 主要风险与短板

## 7.1 理论基础门槛是三人中最高的一档

与朱一舟相比，李文彬的很多核心问题更加依赖：

- quantum mechanics
- solid-state physics
- statistical mechanics
- band theory
- electron-phonon coupling
- quantum transport

而申请者本科核心理论课成绩并不是优势。

如果导师面试深入问：

- Bloch theorem
- band structure
- phonon
- carrier scattering
- effective mass
- DFT
- polarization / Berry phase

申请者需要较大幅度补课。

当前考研复习量子、热统、固体物理可同时服务于这一目标。

---

## 7.2 AI4Science 不是唯一核心

申请者长期兴趣偏：

> scientific ML / AI4Science

而李文彬组虽然明确做：

> machine learning for accelerated materials design

但近年论文显示：

> 许多核心项目完全可以不以 ML 为中心。

因此入组后不能期待：

> “博士五年主要就是 AI for Materials”。

更可能是：

> 电子材料物理 + 第一性原理是底座，ML 在适合的问题上加入。

如果申请者希望先建立扎实 computational materials physics 基础，这是优势。

如果希望博士一开始就以 AI 方法为主线，则优先级应低于朱一舟和刘仕。

---

## 7.3 科学对象需要真正感兴趣

主要对象包括：

- semiconductors
- electron transport
- phonons
- low-dimensional materials
- ferroelectricity
- electronic structure

申请者需要判断：

> 对这些“材料中的电子行为”本身是否有持续兴趣？

而不能只因为：

> “这个组也做机器学习”

就申请。

当前判断：

> 可以接受，且其中电子-声子耦合、半导体输运和低维材料值得进一步了解，但吸引力暂时低于刘仕组的多尺度物理与朱一舟组的 AI materials discovery。

---

# 8. 一个非常重要的招生制度差异

## 8.1 李文彬主要属于工学院材料科学与工程

官方 faculty 页面显示：

- School of Engineering
- School of Science（Affiliated）
- Subject: Materials Science and Engineering, Physics

实际实验室是：

> Materials Modeling and Design Lab

而工学院材料科学与工程系的 faculty list 将李文彬列为核心教师。

因此正式申请时，目前应优先假定：

> **报考西湖大学工学院材料科学与工程博士**

而不是理学院物理博士。

最终需要邮件向 PI 确认 2027 年具体招生学科与导师名额。

---

## 8.2 这会改变申请材料要求

按照西湖工学院 2026 年普通招考规则：

- 已获学士学位者可申请；
- 本科起点学制 5 年；
- 材料科学与工程欢迎跨专业；
- CET-6 要求为 460 分以上；
- 申请者需提交**英文个人陈述**；
- 2026 招生手册显示综合考核为**全英文面试**：
  - 学术汇报约 15 分钟；
  - 专家提问约 15 分钟。

申请者 CET-6 471 在 2026 标准下满足材料科学与工程英语门槛。

**但 2027 正式招生简章尚未发布，因此以上只能作为上一年度规则参考，不能直接视为 2027 最终要求。**

---

# 9. 这对当前语言策略的影响

之前对中国籍 PI 的第一封套磁，我们推荐：

> 中文邮件 + 英文 CV + 成绩单

对李文彬仍然可以这样做。

但是：

> **正式申请材料必须提前按英文体系准备。**

因为如果 2027 延续工学院 2026 规则，则：

- Personal Statement 要英文；
- 面试是全英文；
- 研究汇报也必须能用英文讲清楚。

因此李文彬这条线，比朱一舟 / 刘仕的“中文套磁”更早需要进入：

> English research narrative

准备状态。

---

# 10. 招生信号

目前官方 faculty 页面没有单独写出：

> “2027 PhD opening”

因此 2027 具体名额必须直接询问。

但历史招生信息和工学院材料学科机制显示：

- 李文彬是材料科学与工程独立实验室 PI；
- 工学院材料科学与工程接受本科起点普通招考博士；
- 西湖官方历史资料显示其组长期招收博士生；
- 当前仍持续有多名博士生 / 合作学生发表论文。

所以：

> **值得询问，但不能假定已经有名额。**

当前内部标记：

**2027 招生状态：待确认**

---

# 11. 学生与合作生态

公开论文可确认课题组长期培养或合作过：

- Ziye Zhu
- Shu Zhao
- Xiaoping Yao
- Jiaming Hu
- Yubo Yuan
- 等多名博士生 / 联合培养学生。

例如：

- 2022 年 Bi2O2Se 工作中，Ziye Zhu 为工学院二年级博士生；
- Jiaming Hu 本科为复旦大学物理，后进入西湖工学院博士阶段；
- 多篇工作与浙江大学量子物质团队、西湖理学院实验组合作。

这说明组的一个明显特点是：

> **计算材料与实验 / 量子材料团队连接较强。**

对于纯计算学生，这是好事：

> 模型并不完全脱离真实实验问题。

同时也意味着博士项目可能有较强的跨组合作属性。

---

# 12. 科研资源判断

公开论文多次明确使用：

> Westlake University HPC Center

而研究方法包括：

- VASP
- OpenMX
- ML interatomic potential
- deep-learning electronic-structure models

说明：

> 计算资源不存在明显短板。

但与刘仕组不同，目前没有找到李文彬组类似的公开 Wiki / cluster manual / reproducibility infrastructure。

因此在：

> **科研工程化与知识资产管理**

这一维度上，目前只能评价：

**资源足够，但公开证据少于刘仕组。**

不能因为没公开 Wiki 就推断组内管理差。

---

# 13. 申请者应如何讲自己的故事

李文彬版必须与朱一舟、刘仕再做一次变化。

## 第一段：应用物理与功能材料背景

本科阶段从：

> 电磁材料 / 吸波材料

接触真实 materials structure-property relationship。

## 第二段：毕业设计形成计算材料兴趣

通过：

> CST + Python + GA

发现：

> 复杂材料 / 结构设计问题可以通过物理模拟与自动化计算系统地探索。

## 第三段：从宏观结构性能进一步追问微观起源

这是李文彬版独有的关键转折：

> 本科研究主要停留在宏观电磁响应层面，而希望博士阶段进一步理解材料性质如何从电子结构、晶格振动和原子尺度相互作用中产生。

因此想系统学习：

- first-principles
- electronic structure
- electron-phonon interaction
- semiconductor transport

## 第四段：为什么 ML

不是因为：

> “想做 AI”。

而是：

> 希望利用 ML 加速高成本的 atomistic / electronic-structure calculations，从而覆盖传统 DFT 难以穷举的大结构空间。

## 第五段：为什么李文彬

重点：

> 他组在“电子材料物理深度”和“ML 加速电子结构计算”之间保持了很好的平衡。

---

# 14. 中文套磁信母稿 v1

**主题：2027年博士申请咨询｜哈工大应用物理本科｜计算材料与电子结构模拟**

李老师您好：

我叫周子靖，2026 年 6 月毕业于哈尔滨工业大学应用物理专业，目前计划申请西湖大学 2027 年博士项目。近期了解了您课题组在先进半导体材料、电子-声子相互作用、第一性原理计算以及机器学习辅助材料设计等方面的研究，我对这种从微观电子结构出发理解材料性质，并进一步利用数据驱动方法扩大计算设计空间的研究路线非常感兴趣，因此想向您咨询 2027 年博士生招生情况，以及我的背景与课题组是否具有一定匹配度。

我的本科科研经历主要集中在电磁材料和计算建模。毕业设计中，我研究了一类电阻膜型微波吸收结构。在导师和学长提供初始课题思路、参考代码与 CST 环境后，我主要独立完成后续工作，包括使用 Python 自动调用 CST 进行参数化电磁仿真、处理仿真结果，并搭建和逐步改进基于遗传算法的结构优化流程。这段经历让我对“物理模型 + 数值计算 + 自动化搜索”的研究方式产生了较强兴趣。

本科阶段我的工作主要关注材料或结构在宏观尺度上的电磁响应，但在继续学习和做计算研究的过程中，我逐渐希望进一步理解材料性能在原子和电子尺度上的微观来源。因此，我希望在博士阶段系统学习第一性原理计算、电子结构、声子与载流子输运等计算材料方法，并进一步探索机器学习如何用于加速高成本电子结构计算和更大材料设计空间的探索。

我尤其关注到您课题组近期关于电子-声子耦合、低维半导体以及机器学习辅助电子结构计算的工作，这种“以材料物理问题为基础，再引入机器学习提高可计算范围”的路线与我希望发展的方向很契合。

想请问您 2027 年是否计划招收本科起点普通招考博士生，以及如果申请您的课题组，应报考工学院材料科学与工程学科还是理学院物理学科？以我目前的应用物理和计算背景，是否适合申请您的课题组？随信附上个人简历和本科成绩单，供您参考。

感谢您抽出时间阅读邮件。

祝好！

周子靖  
哈尔滨工业大学 应用物理学学士  
2026 届

---

# 15. 套磁中必须避免的问题

不要写：

- 已熟练 DFT
- 熟练电子结构计算
- 熟练机器学习
- 熟悉电子-声子耦合
- 已有 semiconductor transport research experience

这些目前都不成立。

正确表达：

> 希望从已有 electromagnetic simulation / optimization 经验进一步学习 atomistic and electronic-structure modeling。

---

# 16. 面试准备优先级

如果李文彬回复积极，补课重点应明显不同于朱一舟和刘仕。

## 第一优先：固体物理基础

- crystal lattice
- reciprocal lattice
- Bloch theorem
- band structure
- effective mass
- semiconductor bandgap
- Fermi level

## 第二优先：声子与电子输运

- phonon
- electron-phonon interaction
- scattering
- mobility
- Boltzmann transport 基本图像

## 第三优先：DFT

- Born-Oppenheimer approximation
- Hohenberg-Kohn theorem 基本思想
- Kohn-Sham equation
- exchange-correlation functional
- pseudopotential
- k-point / cutoff convergence

## 第四优先：ML 加速材料计算

- ML interatomic potential
- learned Hamiltonian / DeepH
- CHGNet
- surrogate model
- training / validation
- extrapolation

## 第五优先：量子几何

只有进入具体论文讨论后再补：

- Berry phase
- Berry curvature
- quantum metric

不建议套磁前过度投入。

---

# 17. 当前内部评级

| 维度 | 评价 |
|---|---|
| 计算导向 | 很高 |
| 与物理本科匹配 | 高 |
| 与现有 CST/Python 经历连接 | 中高 |
| 与长期 AI4Science 兴趣 | 中高 |
| 第一性原理训练价值 | 很高 |
| 电子结构/半导体训练价值 | 很高 |
| AI 是否研究核心 | 中等偏高，但非唯一核心 |
| 理论门槛 | 高 |
| 对当前成绩单友好度 | 中等偏低 |
| 计算资源 | 高 |
| 工程化公开资产 | 未发现刘仕式 Wiki，暂不评价 |
| 2027 名额 | 待确认 |
| 推荐优先级 | **A-/B+，第二批优先** |

---

# 18. 与朱一舟、刘仕的第一轮横向比较

| 维度 | 朱一舟 | 刘仕 | 李文彬 |
|---|---|---|---|
| 主要身份 | AI for Materials / Computational Materials | Computational Physics / Multiscale Modeling | Electronic Materials / First-principles Modeling |
| 科学对象 | 无机固体、固态电解质、结构解析 | 铁电、复杂氧化物、极化动力学 | 半导体、低维材料、电子-声子、输运 |
| DFT | 强 | 强 | **很强 / 核心** |
| MD | 强 | **很强** | 有，但不是最主要特色 |
| ML | **研究主线之一** | **研究主线之一** | 重要工具线 |
| Scientific ML 味道 | 很强 | 很强 | 中高 |
| 物理机制导向 | 高 | **很高** | **很高** |
| AI-assisted discovery | **很高** | 中高 | 中高 |
| 与 CST+GA 迁移 | 高 | 高 | 中高 |
| 需要理论补课 | 中高 | 高 | **很高** |
| 申请故事自然度 | **很高** | **很高** | 高 |
| 公开科研工程文化 | 未充分核实 | **非常突出** | 未充分核实 |
| 当前招生信号 | 较明确 | 需确认 | 需确认 |
| 当前优先级 | **A+** | **A+** | **A-/B+** |

---

# 19. 当前决策

李文彬**不淘汰**，而且应保留在核心候选池。

但基于当前申请者画像：

> **第一批联系优先考虑朱一舟、刘仕。**

李文彬建议作为：

> **第二批高质量候选**

主要原因并不是研究水平，而是：

1. 当前长期兴趣更偏 AI4Science / scientific computing；
2. 李文彬组电子结构和凝聚态理论基础要求更高；
3. 本科成绩中相关理论课并非优势；
4. 与朱一舟 / 刘仕相比，现有经历的申请叙事略少一层“天然契合”。

但如果后续申请者在考研学习中发现自己非常喜欢：

> 固体物理、半导体、电子结构、电子-声子耦合

则李文彬优先级应立即上调。

---

# 20. 后续待办

- [ ] 向 PI 确认 2027 是否有博士名额
- [ ] 确认应报考材料科学与工程还是物理学
- [ ] 确认 2027 工学院英语与面试规则
- [ ] 阅读 MoS2 nanotube ML-electronic-structure 工作
- [ ] 阅读一篇 semiconductor transport / electron-phonon 代表论文
- [ ] 若进入第一批申请，则提前准备英文 PS 与英文科研汇报
- [ ] 通过西湖在读生了解组规模、毕业要求和导师指导方式
- [ ] 后续进入 A 线总表横向比较
