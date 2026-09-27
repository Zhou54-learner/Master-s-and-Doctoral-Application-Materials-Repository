# A线导师档案 02｜刘仕（Shi Liu）

> 用途：西湖大学 A 线申请内部工作文档。用于后续查阅、套磁、材料定制、面试准备与最终决策。  
> 更新日期：2026-09-26  
> 状态：**A+｜第一批联系对象｜需优先确认 2027 博士名额｜暂未发送套磁**

---

# 0. 一句话结论

刘仕是当前西湖 A 线中与申请者“物理 → 科学计算 → AI4Science”长期路线高度匹配的核心 PI。

与朱一舟相比，刘仕组更强调：

> **先提出凝聚态/铁电物理问题，再用 DFT、机器学习势、分子动力学与多尺度模型把原本无法覆盖的时间/空间尺度变得可计算。**

因此，如果申请者更希望最终成为：

> **以物理问题为中心、以 AI/计算方法为工具的 computational physicist**

而不是更偏“AI for materials discovery / materials informatics”的研究者，那么刘仕甚至可能比朱一舟更匹配。

最大的待确认项不是研究方向，而是：

> **2027 年是否还有本科起点普通招考博士名额。**

目前未找到刘仕本人单独发布的 2027 招生公告，因此必须通过邮件直接确认。

---

# 1. PI 基本信息

- 姓名：刘仕 / Shi Liu
- 单位：西湖大学理学院物理系
- 实验室：Multiscale Materials Modeling Laboratory / 多尺度材料建模实验室
- 职称：长聘副教授
- 学科：Physics / Chemistry
- 2019 年加入西湖大学
- 2025 年晋升长聘副教授
- 本科：中国科学技术大学化学物理
- 博士：University of Pennsylvania
- 博士研究：computational condensed matter physics
- 博后：Carnegie Institution for Science、U.S. Army Research Laboratory
- 研究主题：
  - 新型铁电材料；
  - 凝聚态拓扑态；
  - 基于深度学习的大尺度复杂氧化物建模；
  - 多尺度计算材料物理。

实验室主页：
https://liutheory.westlake.edu.cn/

西湖官方主页：
https://en.westlake.edu.cn/faculty/shi-liu.html

---

# 2. 研究方法论画像

刘仕组的核心不是“用 AI 做材料预测”本身，而是：

> **把不同尺度上原本彼此割裂的方法连接起来，使材料在技术相关时间尺度与空间尺度上的动力学和性质变得可计算。**

典型方法链：

> DFT / first-principles  
> ↓  
> atomistic physical understanding  
> ↓  
> machine-learning interatomic potential / deep potential  
> ↓  
> large-scale molecular dynamics  
> ↓  
> finite-temperature / domain / switching dynamics  
> ↓  
> continuum / analytical multiscale model  
> ↓  
> 与真实实验比较并反推材料机制

这意味着 AI 主要解决的是：

> **第一性原理太贵，传统经验势又不够准确时，如何把接近量子力学精度的模型扩展到大尺度动力学。**

这是一条非常典型的 Physics-first AI4Science 路线。

---

# 3. 当前三个最值得理解的研究主题

## 3.1 铁电极化与畴动力学

研究对象主要包括：

- PbTiO3 等传统铁电材料；
- HfO2 / HZO 铁电薄膜；
- 2D ferroelectrics；
- organic-inorganic hybrid ferroelectrics；
- 拓扑极化结构、畴壁、极化翻转。

核心问题并非只计算静态能量，而是：

> 原子尺度的极化如何随温度、电场、应变、缺陷和几何尺寸变化？

这类问题天然要求从 DFT 走向大尺度、有限温度的动态模拟。

---

## 3.2 Deep-learning-assisted molecular dynamics

实验室较早就开发并使用基于深度学习的力场。

基本逻辑：

> DFT 产生高精度训练数据  
> ↓  
> deep neural network 学习势能面  
> ↓  
> 用 ML force field 做大规模 MD  
> ↓  
> 研究 DFT 无法直接覆盖的时间/空间尺度

例如实验室曾为二维铁电 In2Se3 建立深度神经网络力场，并用并发学习更新第一性原理训练数据库，以接近 DFT 的精度预测相变、极化翻转和畴壁运动。

这一方向与申请者希望补齐的：

- DFT
- MLFF
- MD
- HPC

高度重合。

---

## 3.3 多尺度物理机制，而非单纯预测

刘仕组的强项是把：

> 原子尺度机制

继续向：

> 宏观/介观可测性能

连接。

例如 HfO2 铁电矫顽场研究中，团队结合：

- DFT；
- deep-learning potential；
- 大规模 MD；
- Landau-Ginzburg-Devonshire 分析模型；

最终解释不同极化翻转机制如何决定真实薄膜的 coercive field。

这体现出该组非常明显的科研取向：

> **不是让 AI 给一个数，而是利用计算把实验现象背后的物理机制拆出来。**

---

# 4. 三篇代表工作及申请意义

## 4.1 Giant Piezoelectric Effects of Topological Structures in Stretched Ferroelectric Membranes  
Physical Review Letters 133, 046802 (2024)

核心方法：

> DFT + deep-learning-assisted molecular dynamics

核心结果：

- 在拉伸 PbTiO3 薄膜中发现 dipole spiral；
- 研究极化拓扑结构；
- 解释其巨大压电响应；
- 把有限温度、大尺度原子动力学与第一性原理连接。

为什么对申请者重要：

申请者过去的 CST 项目本质上也是：

> 一个基础物理方程控制的 forward simulator  
> + 更高层的计算搜索工具

刘仕组进一步升级成：

> DFT-level atomic physics  
> + ML surrogate potential  
> + large-scale dynamics

迁移路线非常清楚：

> Maxwell-scale computational physics  
> → atomistic computational physics

---

## 4.2 Theoretical Lower Limit of Coercive Field in Ferroelectric Hafnia  
Physical Review X 15, 021042 (2025)

核心问题：

为什么 HfO2 铁电薄膜需要很大的电场才能翻转极化？

方法链：

> first-principles input  
> + deep neural network potential  
> + molecular dynamics  
> + multiscale analytical modeling  
> + experimental validation

关键申请意义：

这篇最能体现刘仕组的“多尺度”不是标签，而是真正把不同计算层次连在一起。

对于申请者而言，它说明未来博士训练可能不是：

> 只学一个 VASP 软件

而是：

> 理解物理问题 → 建模 → DFT → ML potential → MD → 分析模型 → 与实验连接。

这与申请者希望形成“长期不可替代的科学计算能力”高度一致。

---

## 4.3 Are Foundational Atomistic Models Reliable for Finite-Temperature Molecular Dynamics?  
J. Phys. Chem. C 129, 21538–21544 (2025)

核心问题：

近年来出现大量 foundation / universal atomistic models，但：

> 静态 benchmark 准确，是否意味着它们真的适合有限温度 MD？

该工作直接检验 foundation atomistic models 在真实 finite-temperature molecular dynamics 中的可靠性。

重要意义：

这非常符合申请者对 AI4Science 的价值判断：

> 不能把 benchmark 数字当成真实科学能力。

模型是否能：

- 保持物理稳定性；
- 重现有限温度行为；
- 预测真实动态性质；

比静态 RMSE 更重要。

论文作者背景也提供了非常有价值的招生参考：

- Denan Li：宁波大学材料本科 → 西湖物理博士；
- Jiyuan Yang：南京师大物理本科 → 博士研究 deep-potential ferroelectric dynamics；
- Xiangkai Chen：北科大材料博士 → 刘仕组博后；
- Lintao Yu：东北石油大学化学本科 → 西湖物理博士，研究大型计算基础设施。

说明实验室并非只接收已经完全训练好的计算物理学生，学生本科背景存在真实多样性。

---

# 5. 实验室规模与科研资源

实验室官网当前公开信息显示，组内约：

- 17 名成员；
- 11 名 PhD Candidate；
- 3 名 Postdoc；
- 另有 Research Scientist 等研究人员。

属于：

> **中等偏大规模计算组。**

与朱一舟组相比明显更大、更成熟。

## 5.1 算力基础设施

实验室 Resource 页面直接提供：

- 组内 GPU cluster 使用手册；
- Westlake SE cluster 使用手册；
- 实验室内部 Wiki；
- 多篇论文开放数据与代码。

这说明：

> 算力和计算基础设施并不是临时向公共服务器“借一点”，而是实验室工作流的正式组成部分。

这对申请者非常重要，因为长期目标就是进入：

> simulation + HPC + AI

路线。

## 5.2 开源/可复现倾向

实验室公开了多项工作的：

- scripts；
- model weights；
- DFT input；
- GitHub repository；
- open data。

这对一个希望逐渐提高科研软件能力的人是明显加分项。

---


## 5.3 实验室工程文化与科研资产管理（2026-09-26补充）

这一项目前应视为刘仕组相对于多数计算课题组的显著差异化优势。

### 公开 Wiki 的定位

刘仕组公开 Wiki 将自己定义为实验室的“working notebook”，用于沉淀：

- tutorials；
- 软件安装记录；
- HPC 使用技巧；
- 数据分析流程；
- 日常科研中容易散落在聊天记录、shell history 或个人 Downloads 文件夹里的知识。

Wiki 首页明确强调，它不是用于对外展示科研成果，而是用于：

> how we run calculations, reproduce results, and get new people moving without too much friction.

这说明实验室有意识地把“隐性经验”转化为可复用的组织知识，而不是依赖口耳相传。

### 论文级复现工作流

Wiki 首页专门设置 Research Snapshots，并把近期论文直接映射到可执行教程，例如：

- PRL 2025 sliding ferroelectrics → dynamic BEC + LAMMPS；
- PRX 2025 ferroelectric hafnia → persistent embryo method + LGD；
- PRL 2026 finite-temperature piezoelectricity → MD full piezoelectric tensor workflow。

这不是普通“软件教程”，而是：

> paper → method → input/scripts → reproducible workflow

的研究资产化。

### Machine-Learning Potential 教程

组内 MLP 教程由在读博士生撰写，明确包含：

1. application scope 定义；
2. DFT convergence test；
3. initial database；
4. active learning；
5. model validation；
6. speed optimization。

尤其值得注意：

- 教程明确说相关 input files 和 scripts 都提供；
- 不要求读者事先熟练 DFT/MD；
- 强调 MLP 的训练域与 extrapolation 风险；
- 强调参考 DFT 数据质量；
- 强调常规 RMSE 测试并不等于真实物理可靠；
- 把“能否复现实验”称为最终 golden standard。

这与实验室近年来论文中对“benchmark 与真实物理可靠性不能等同”的研究取向一致。

### 新成员 onboarding

Wiki 中专门设置 `New Members` 区域。

HPC manual 页面明确建议新成员在进入课题组后首先阅读集群手册以熟悉计算环境；手册来源于课题组成员参与设计的计算系统。

这说明：

> HPC 使用并不是靠新人自行询问和反复踩坑，而是被纳入正式 onboarding 流程。

### 教程粒度

公开教程的粒度非常细，已经覆盖：

- VASP；
- QE；
- CASTEP；
- CP2K；
- LAMMPS；
- MLP / DP-GEN；
- phonon / FourPhonon；
- polarization；
- ferroelectric domain analysis；
- MD piezoelectric tensor；
- dislocation motion；
- polaron DFT-MD；
- EndNote 等基础科研工具。

部分教程从：

> 环境安装 → 输入文件 → 提交脚本 → 常见错误 → 输出检查 → 后处理

逐步骤展开，并附真实 input/scripts。

这对缺少正规 scientific-computing 工程训练的新生尤其有价值。

### Wiki 本身也采用协作式维护

首页提供：

- Contributing Guide；
- How to write；
- Template；
- GitHub repository。

其理念是：

> 如果一项方法只存在于个人 shell history、聊天记录或本地 Downloads 中，就应该考虑把它转成 Wiki 页面。

这意味着知识资产管理不是由 PI 一个人维护，而是试图形成组内共同贡献机制。

### 对申请者的特殊意义

申请者当前的优势是：

- 能独立学习陌生工具；
- 有 Python/CST 自动化经验；
- 有 Git 基础；
- 对可复用 workflow 和知识资产管理高度认同。

当前短板则恰恰是：

- Linux/HPC；
- DFT/MD 正规流程；
- 科研软件工程；
- 可复现 scientific-computing workflow。

因此刘仕组公开的 Wiki / cluster / reproducibility 体系可能显著降低这一能力迁移的早期摩擦。

对申请者而言，这种环境的价值不只是“资料多”，而是：

> **一个已经把科学计算方法、代码、复现和新生训练系统化的科研生态。**

### 当前内部评价

新增评价维度：

- 科研工程化：**很高**
- 可复现文化：**很高**
- 新人 onboarding：**很高（基于公开文档）**
- 知识资产沉淀：**很高**
- 对自驱型学生友好度：**预期很高，但需向在读生核实**

### 仍需核实

公开文档能够证明“制度和资产存在”，但不能自动证明真实日常体验。

后续应向在读生询问：

1. Wiki 是否持续更新、实际使用频率如何；
2. 新人是否真的按照这些流程 onboarding；
3. 遇到 Wiki 无法解决的问题时，是否能及时获得学长/博后/PI 支持；
4. 组内代码 review、数据管理、复现要求是否真正执行；
5. 论文发表后是否普遍要求整理 source data / scripts / workflow。

如果公开文档与组内实际运作一致，则该项应成为刘仕在最终导师比较中的显著加分项。

---

# 6. 学生培养与毕业情况

目前官网可以确认近年连续多人完成博士答辩：

- Jiyuan Yang：2025-05 博士答辩；
- Liyang Ma：2025-05 博士答辩；
- Yihao Hu：2025-11 博士答辩；
- Wenjie Zhou：2026-05 博士答辩；
- Qisheng Yu：2026-05 博士答辩；
- Yudi Yang：2026-05 博士答辩。

说明实验室已经进入：

> **稳定产生博士毕业生的成熟阶段。**

目前没有公开证据显示该组存在普遍延毕问题。

但必须强调：

> **公开网页只能证明多人如期/完成毕业，无法计算全组平均毕业年限或延毕比例。**

后续真正进入联系阶段后，最好通过西湖在读同学进一步核实：

- 实际平均毕业时间；
- 导师是否会卡毕业；
- 论文要求；
- 导师沟通频率；
- 是否需要长期超负荷工作。

## 6.1 Yihao Hu 案例

西湖物理系 2026 年介绍：

> Yihao Hu 在完成约五年的 materials modeling 博士研究后毕业，并转向 hedge fund。

这至少说明该组培养出的 computational skill：

> 不只能够继续学术，也具有向量化金融、计算行业等方向迁移的可能。

这一点与申请者重视“能力可迁移”较为契合。

---

# 7. 当前学生背景对申请者意味着什么

公开成员信息显示：

### Denan Li

- 本科：宁波大学 Materials Science and Engineering
- 2024 → 西湖大学 Physics PhD
- 方向：machine-learning-assisted multiscale methods for ferroelectrics

### Lintao Yu

- 本科：东北石油大学 Chemistry
- 2025 → 西湖大学 Physics PhD
- 方向：high-performance computing infrastructure for large-scale simulations

### Yuanjinsheng Liu

- 武汉工程大学本科
- 中国地质大学（北京）应用统计硕士
- 现为博士生

以上背景说明：

> **刘仕组的录取不是单纯按本科院校、专业名称或“已经会 DFT”一刀切。**

但不能据此推断申请容易。

真正可能被看重的是：

- 科研潜力；
- 计算能力；
- 学习能力；
- 与具体研究项目的适配程度。

对于哈工大物理本科、已有 CST/Python 科研工作流经验的申请者而言，至少从背景结构上不存在明显“不属于这个池子”的问题。

---

# 8. 与申请者的匹配分析

## 8.1 特别匹配的地方

### A. Physics-first

申请者不希望未来变成：

> “只会调用 AI 工具的人。”

刘仕组的 AI 本质上是为了：

> 扩展可计算的物理尺度。

这与价值取向高度一致。

### B. Computational focus

申请者明确：

> 希望博士主要做计算，不希望主要依靠纯实验反复试错。

刘仕组主体明显是：

- DFT
- MD
- ML potentials
- numerical modeling
- HPC

高度符合。

### C. 本科项目可以自然迁移

本科：

> electromagnetic forward model  
> + Python automation  
> + GA optimization

博士：

> first-principles forward model  
> + ML potential  
> + large-scale MD / multiscale modeling

研究对象和算法不同，但科研方法论连续。

### D. 对科研自动化/基础设施的兴趣可发挥

申请者做过：

- 学习 Agent；
- Git；
- 自动化科研脚本；
- AI 辅助编程。

刘仕组存在：

- group GPU cluster；
- HPC infrastructure；
- large-scale simulation；
- open-source workflow。

这一点比一般传统 DFT 组更适合申请者的“物理 + 工具系统”兴趣。

---

# 9. 主要风险

## 9.1 理论基础要求更高

相对于朱一舟，刘仕组更明显偏：

> computational condensed matter physics

需要逐渐建立：

- quantum mechanics；
- statistical physics；
- solid-state physics；
- electronic structure；
- DFT；
- molecular dynamics；
- ferroelectric physics。

申请者本科成绩中核心理论课并非优势。

因此面试准备必须把：

> 当前考研中的量子、热统、固体物理复习

视为申请准备的一部分。

---

## 9.2 研究对象较集中于铁电/复杂氧化物

刘仕组虽然方法很广，但近年核心科学问题集中在：

- ferroelectrics；
- domain dynamics；
- complex oxides；
- hafnia；
- piezoelectricity；
- topological polar structures。

申请者必须判断：

> 是否愿意连续多年真正研究这些物理问题？

不能只因为“ML + DFT”方法漂亮就忽略科学对象。

当前判断：

> **可以接受，而且物理问题本身具有明显吸引力，但仍需通过代表论文进一步确认。**

---

## 9.3 组规模较大

优点：

- 方法体系成熟；
- 学长学姐多；
- 项目和合作网络丰富；
- 算力基础设施完整。

潜在风险：

- PI 对单个博士生日常指导频率可能低于小组；
- 很可能形成 senior student / postdoc 带新生的培养结构。

这不一定是负面。

申请者本人对指导方式并不强求，只要：

> PI 不开倒车 + 有可靠方向 + 有资源 + 学长体系有效

即可。

但后续应通过在读生核实。

---

## 9.4 2027 名额尚未确认

截至 2026-09-26：

- 西湖物理学允许学士学位申请五年制普通招考博士；
- 刘仕是物理系博士导师；
- 实验室活跃且仍有新博士生；
- 但未找到刘仕本人公开发布的“2027 PhD opening”公告。

因此套磁第一任务就是：

> **直接确认 2027 是否还有本科起点博士名额。**

---

# 10. 与朱一舟的横向区别

## 朱一舟

更接近：

> Materials problem  
> → high-throughput / data / ML  
> → materials discovery / characterization

关键词：

- AI for Materials
- MLFF
- generative materials
- high-throughput
- solid-state electrolyte
- XRD inverse problem

## 刘仕

更接近：

> Condensed matter physics problem  
> → DFT  
> → ML potential  
> → large-scale MD  
> → multiscale explanation of physical mechanisms

关键词：

- computational physics
- ferroelectrics
- DFT
- deep potential
- molecular dynamics
- multiscale modeling
- HPC

## 对申请者的区别

如果长期身份更希望是：

> **AI-assisted materials scientist**

朱一舟更直接。

如果更希望是：

> **computational physicist who uses AI to solve materials physics**

刘仕更直接。

当前个人画像下：

> **朱一舟 A+ ≈ 刘仕 A+**

但刘仕需要先确认 2027 名额。

---

# 11. 给刘仕的申请叙事骨架

与朱一舟版本必须明显不同。

## 第一段：物理与科研起点

哈工大应用物理本科，通过电磁材料项目进入真实材料物理研究。

## 第二段：毕业设计形成 computational physics 兴趣

毕业设计：

> resistive-film microwave absorber  
> → CST  
> → Python automation  
> → genetic-algorithm optimization

真正重要的是：

> 利用计算把复杂物理设计问题从人工试错变成可系统探索的模型。

## 第三段：兴趣不是“转 AI”，而是“扩大计算物理尺度”

进一步认识到：

> 很多真实材料动力学问题受限于传统计算方法能够覆盖的时间和空间尺度。

因此希望从：

> Maxwell-scale modeling

进一步进入：

> atomistic / first-principles / multiscale simulation

并学习如何使用 ML potentials 扩展传统物理计算。

## 第四段：为什么刘仕

重点表达：

> 对“DFT → ML potential → large-scale MD → physical mechanism”的多尺度路线尤其感兴趣。

这比说：

> “我喜欢 AI4Science”

更具体、更可信。

## 第五段：长期目标

希望形成：

> physics + scientific computing + AI-assisted modeling

的复合研究能力。

---

# 12. 套磁语言策略

与朱一舟一致：

> **中文正文 + 英文 Academic CV + 官方成绩单**

刘仕为中文母语 PI，首封邮件无需刻意使用英文。

若对方后续使用英文回复，再切换语言即可。

---

# 13. 中文套磁信母稿 v1

**主题：2027年博士申请咨询｜哈工大应用物理本科｜多尺度计算与AI辅助材料模拟**

刘老师您好：

我叫周子靖，2026 年 6 月毕业于哈尔滨工业大学应用物理专业，目前计划申请西湖大学 2027 年物理学博士项目。近期系统了解了您课题组在铁电材料、多尺度计算以及基于机器学习势函数的大规模分子动力学模拟方面的工作，我对这种以物理问题为核心、利用机器学习扩展传统计算方法时间和空间尺度的研究思路非常感兴趣，因此想向您咨询 2027 年博士生招生情况，以及我的背景与课题组方向是否具有一定匹配度。

我的本科科研经历主要集中在电磁材料和计算建模。毕业设计中，我研究了一类电阻膜型微波吸收结构。在导师和学长提供初始课题思路、参考代码与 CST 环境后，我主要独立完成后续工作，包括使用 Python 自动调用 CST 进行参数化电磁仿真、处理仿真结果，并搭建和逐步改进基于遗传算法的结构优化流程。这段经历让我第一次比较完整地经历了从物理模型、数值仿真到自动化搜索的计算研究过程，也使我逐渐希望从宏观尺度的电磁仿真进一步进入更基础的原子尺度和多尺度计算。

目前我的实际项目经验仍主要是电磁仿真、科研脚本和优化计算，尚没有正式参与 DFT、分子动力学或机器学习势函数项目。我希望在博士阶段系统学习第一性原理、原子模拟和高性能科学计算，并进一步理解如何利用机器学习势函数把接近第一性原理精度的模型扩展到真实有限温度和更大时空尺度的物理问题。

我尤其关注到您课题组近期将 DFT、deep-learning potentials 与大尺度分子动力学结合，用于理解铁电极化、畴动力学和压电响应等真实物理机制。这种“以计算方法扩展可研究物理尺度”的路线与我希望发展的方向非常契合。

想请问您 2027 年是否还有本科起点普通招考博士生名额，以及以我目前的物理和计算背景，是否适合申请您的课题组？随信附上个人简历和本科成绩单，供您参考。

感谢您抽出时间阅读邮件。

祝好！

周子靖  
哈尔滨工业大学 应用物理学学士  
2026 届

---

# 14. 套磁时应重点展示的材料

第一封：

1. 英文 Academic CV
2. 官方本科成绩单

如果导师进一步感兴趣：

3. 毕业设计 1 页摘要
4. Python-CST 自动优化 workflow 示意图
5. Git / 代码样例
6. 毕业论文
7. MATLAB 尘埃等离子体代码

刘仕组本身有较明显的软件、HPC 和开源工作流文化，因此：

> **代码和 workflow 的可展示性，在刘仕这条线上可能比普通材料组更有价值。**

---

# 15. 面试前最应该补的知识

若刘仕回复积极，优先级如下：

## 第一优先

- DFT 的物理图像；
- Born-Oppenheimer approximation；
- Kohn-Sham DFT 基本思想；
- classical MD；
- potential energy surface；
- force = -∇E；
- 为什么需要 ML potential。

## 第二优先

- ferroelectric polarization；
- domain / domain wall；
- polarization switching；
- piezoelectricity；
- perovskite / HfO2 ferroelectrics。

## 第三优先

- Deep Potential / MLFF 基本概念；
- training set；
- force/energy labels；
- transferability；
- finite-temperature MD；
- foundation atomistic model。

## 第四优先

- Linux；
- HPC / cluster；
- Git；
- Python scientific stack。

不需要在套磁前全部学会。

---

# 16. 当前状态卡

- PI：刘仕
- 学校：西湖大学
- 学科：Physics
- 实验室：Multiscale Materials Modeling Laboratory
- 内部评级：**A+**
- 研究兴趣匹配：**很高**
- 物理身份匹配：**很高**
- 现有科研经历连接：**高**
- 当前技能直接匹配：**中等**
- 长期成长价值：**很高**
- 计算资源：**公开信息显示较强**
- 学生培养成熟度：**较高**
- 组规模：**中等偏大**
- 延毕风险：**目前无公开负面信号，但需向在读生核实**
- 2027 名额：**待确认**
- 套磁母稿：**完成**
- 正式联系：**暂缓，待总表形成后决定第一批发送次序**

---

# 17. 后续待办

- [ ] 直接确认刘仕 2027 本科起点普通招考博士名额
- [ ] 精读 1 篇 DFT + ML-MD 代表论文
- [ ] 精读 foundation atomistic model reliability 论文摘要/逻辑
- [ ] 制作英文 Academic CV
- [ ] 制作毕业设计 1 页 computational workflow
- [ ] 梳理可展示代码
- [ ] 通过西湖在读同学了解组内真实指导方式
- [ ] 询问博士平均毕业时间与毕业要求
- [ ] 与朱一舟进行第一轮横向比较
- [ ] 决定正式套磁顺序

---

# 18. 当前推荐结论

**推荐进入第一批正式套磁名单。**

优先理由：

1. Physics-first AI4Science 路线与长期目标高度一致；
2. 已有 CST/Python/GA 经验可以自然迁移到更高层次 scientific computing；
3. 组内 DFT、ML potential、MD、HPC 方法体系完整；
4. 计算资源与软件工作流较成熟；
5. 学生背景多样，不要求入学前已经完整掌握 DFT/ML；
6. 已连续产生博士毕业生，培养体系明显进入成熟阶段。

主要不确定性：

> 2027 名额，以及申请者是否真正喜欢以铁电/复杂氧化物为主要科学对象。

这两个问题解决后，才能最终判断其是否应排在朱一舟之前。
