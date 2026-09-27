# A线导师档案 04｜吴泰霖（Tailin Wu）

> 用途：西湖大学 A 线申请内部工作文档。用于后续查阅、套磁、材料定制、面试准备与最终决策。  
> 更新日期：2026-09-26  
> 状态：**A-/高风险冲刺｜研究方向高度匹配，但申请门槛与当前方法背景存在明显缺口｜需确认2027招生学科与英语门槛**

---

# 0. 一句话结论

吴泰霖组是目前西湖候选 PI 中最接近“AI4Science 方法本身就是研究核心”的实验室。

其研究不是：

> 在某个材料/物理课题上顺便使用机器学习，

而是直接研究：

> **如何设计新的生成模型、图神经网络、神经算子、AI Agent 等方法，用于科学仿真、控制、反向设计与科学发现。**

因此，如果申请者未来希望成为：

> **以 AI / Scientific ML 方法创新为核心、面向真实物理系统做 AI4Science 的研究者**

吴泰霖是非常有吸引力的导师。

但与朱一舟、刘仕相比，这条线的现实申请风险明显更高，原因主要有三点：

1. 课题组 2027 博士招聘明确要求“课业成绩或科研成果拔尖”；
2. 明确要求“有机器学习或相关领域科研经验”；
3. 吴泰霖主要通过工学院**智能信息技术**学科招生，而该学科 2026 年英语门槛为 CET-6 480；申请者目前 CET-6 为 471。

因此当前定位应是：

> **科学兴趣 A+，申请可行性暂评 A-/高风险冲刺。**

---

# 1. PI 基本信息

- 姓名：吴泰霖 / Tailin Wu
- 单位：西湖大学工学院人工智能系
- 兼任：理学院相关交叉研究
- 实验室：AI for Scientific Simulation and Discovery Lab
- 当前职称：助理教授 / 博士生导师
- 本科：北京大学物理学院
- 博士：MIT Physics
- 博士研究主题：AI for Physics / Physics for AI
- 博后：Stanford Computer Science，合作导师 Jure Leskovec
- 曾在 Google AI、NVIDIA Research 实习

官方主页：
https://en.westlake.edu.cn/faculty/tailin-wu.html

实验室：
https://ai4s.lab.westlake.edu.cn/

个人主页：
https://tailin.org/

---

# 2. 当前研究方向

吴泰霖本人目前将实验室研究分为三条大主线。

## 2.1 Core AI

重点包括：

- diffusion / flow matching
- next-generation generative models
- self-evolving AI architectures
- generalist AI scientists
- AI engineers
- test-time reasoning / generative reasoning

这意味着该组并非只做 AI 的科学应用，而会直接做：

> **AI 方法创新本身。**

---

## 2.2 AI for Physical Sciences

主要研究：

- scientific simulation
- physical control
- inverse design
- scientific reconstruction
- scientific discovery

对象包括：

- fluids
- plasmas
- coupled physics
- deformable objects
- real PDE systems
- engineering construction / physical mechanisms

方法包括：

- neural operators
- graph neural networks
- diffusion models
- flow matching
- equivariant models
- surrogate simulation
- generative inverse design

---

## 2.3 AI for Life Science

包括：

- virtual cell
- protein design
- single-cell perturbation prediction
- biological system simulation

这一条与申请者当前兴趣不是主方向，但说明实验室的方法具有很强跨学科迁移性。

---

# 3. 2025–2026 年研究趋势

当前实验室发展速度非常快。

吴泰霖个人主页显示：

- 2026 ICLR：实验室有 7 篇论文录用；
- RealPDEBench 为 ICLR 2026 Oral（top 1.2%）；
- BuildArena 进入 ICML 2026；
- EqCollide 为 SIGKDD 2026 Oral；
- 另有多个生成模型、PDE 仿真、物理控制、生命科学项目。

这说明实验室当前已经不是单一“PDE surrogate model”课题组，而开始向：

> **生成模型 + Scientific ML + AI Agent + physical design/discovery**

快速扩张。

---

# 4. 最值得申请者理解的代表工作

## 4.1 Compositional Generative Inverse Design（ICLR 2024 Spotlight）

核心问题：

传统 inverse design 往往对训练分布内的目标有效，但复杂设计任务可能需要：

> 比训练样本更复杂的结构组合。

该工作使用 compositional generative models，在复杂物理系统中进行边界条件和初始状态的反向设计。

### 与申请者毕业设计的直接方法论连接

申请者的毕业设计：

> target absorption  
> → GA  
> → CST forward simulation  
> → structure optimization

吴泰霖的路线则是：

> target physical behavior  
> → generative inverse design  
> → learned physical model / physical constraints  
> → design

两者属于非常明确的同一大类问题：

> **Scientific Inverse Design**

只是：

- 本科项目：evolutionary optimization + Maxwell solver
- 吴泰霖组：generative AI + learned physical representations

这是目前申请者与吴泰霖最自然的科研连接点。

---

## 4.2 RealPDEBench（ICLR 2026 Oral）

核心问题：

大量 Scientific ML 模型只在：

> synthetic / simulated benchmark

上测试。

但真实物理系统的数据存在：

- measurement noise
- imperfect boundary conditions
- simulator-reality gap
- missing variables
- distribution shift

RealPDEBench 建立：

> real-world data + paired simulation data

来测试模型是否真正能够从“仿真世界”迁移到真实系统。

### 对申请者的意义

这与申请者对 AI4Science 的价值判断高度一致：

> benchmark 高并不等于真实科研能力强。

它也与申请者此前经历过的：

> CST simulation 与实验/真实材料之间存在差异

具有方法论上的共鸣。

---

## 4.3 BuildArena（ICML 2026）

核心问题：

让 LLM Agent 不只是“回答工程问题”，而是在物理模拟器中：

> 设计 → 建造 → 测试

真实可工作的：

- rockets
- bridges
- vehicles
- 3D mechanisms

这是一个：

> language → design → executable construction → physics validation

的闭环。

### 与申请者 Agent 项目的潜在连接

申请者此前真正做过：

- 学习型 Agent
- RAG
- workflow 设计
- Git 版本管理
- AI 辅助工作流

这些经历本身不等同于 ML research，但在吴泰霖组这里比在传统材料组更加有潜在叙事价值：

> 申请者已经对“Agent 如何调用工具并形成闭环 workflow”有工程经验。

如果后续把科研 Agent 与物理模拟自动化结合起来，这条经历可能成为辅助资产。

但必须避免夸大：

> software agent project ≠ machine learning research。

---

## 4.4 GenCP / M2PDE / DiffPhyCon 等

这些工作体现实验室另一条稳定主线：

> generative models for physical simulation and control

研究对象是：

- multiphysics PDE
- coupled systems
- control problems
- large-scale physical simulation

其核心身份更接近：

> **Scientific Machine Learning**

而不是传统 computational physics。

---

# 5. 与朱一舟 / 刘仕的根本区别

## 朱一舟

典型路径：

> materials problem  
> → physical/material knowledge  
> → DFT / high-throughput  
> → ML  
> → materials discovery

博士训练身份更像：

> computational materials scientist using AI

---

## 刘仕

典型路径：

> condensed matter problem  
> → DFT  
> → ML potential  
> → large-scale MD  
> → multiscale physical mechanism

博士训练身份更像：

> computational physicist using AI

---

## 吴泰霖

典型路径：

> scientific problem class  
> → identify universal computational/learning bottleneck  
> → invent ML / generative / agent method  
> → apply across physics / engineering / biology

博士训练身份更像：

> **AI4Science / Scientific ML researcher**

这里“AI 方法创新”本身往往就是论文贡献的重要部分。

---

# 6. 对申请者的吸引力

## 6.1 长期研究兴趣高度匹配

申请者已经明确对：

- AI4Science
- scientific computing
- inverse design
- automated research workflows

有长期兴趣。

吴泰霖组几乎正面覆盖这些主题。

---

## 6.2 本科物理身份并非劣势

吴泰霖本人：

> 北大物理本科 → MIT Physics PhD → Stanford CS postdoc

其研究路径本身就是：

> Physics → AI / Scientific ML

而官方招聘也明确欢迎：

> machine learning **or natural sciences** 背景学生。

因此“物理本科转 AI4Science”在理念上完全合理。

---

## 6.3 CST + GA 是真实的 Scientific Inverse Design 起点

申请者可以非常自然地讲：

> 我第一次接触 inverse design，不是通过标准 ML benchmark，而是在真实 Maxwell simulation 中通过 GA + CST 做结构优化。

这比泛泛地说：

> “我对 AI for Science 很感兴趣”

更可信。

---

## 6.4 Agent 项目在这里有额外价值

相较于朱一舟 / 刘仕，吴泰霖组已经明确开展：

> AI Agent / generalist AI scientists / AI engineers

因此申请者此前的 Agent 工程经历可作为：

> secondary project evidence

证明：

- software workflow thinking
- tool integration
- RAG / agent architecture experience
- Git / project engineering

但不能用它代替 ML research。

---

# 7. 当前最严重的申请问题：机器学习研究经历不足

2027 博士招聘公告明确写：

- 本科就读于国内外知名高校；
- 课业成绩或科研成果拔尖；
- **有机器学习或相关领域科研经验**；
- 有志于 AI + Science 开创性研究。

申请者当前实际情况：

### 符合

- 哈工大本科：高校背景没有问题；
- 有科研经历；
- 有真实 scientific simulation / optimization 项目；
- 有 Agent 工程项目；
- AI4Science 动机是真实且可追溯的。

### 不占优势

- 专业排名约 21–22 / 46；
- 平均分约 80；
- 论文作者贡献并非强一作成果；
- 没有 PyTorch/JAX 深度学习研究项目；
- 没有 NeurIPS/ICLR 类 ML research；
- GA 优化不能简单等同于现代 machine-learning research。

因此：

> **吴泰霖是当前几位候选中“兴趣匹配非常高、现有申请材料竞争力却最弱”的一位。**

必须诚实面对。

---

# 8. 第二个潜在硬门槛：英语

吴泰霖主要属于工学院：

> Information Technology in Artificial Intelligence / 智能信息技术。

西湖工学院 2026 博士招生规则明确规定：

> 智能信息技术 CET-6 不低于 480；
> 其他工学院学科不低于 460。

申请者当前：

> CET-6 = 471。

因此：

> **如果 2027 仍沿用 480 分标准，并且吴泰霖只能通过智能信息技术学科招生，则 CET-6 471 不满足形式门槛。**

这是一个真正可能导致无法提交有效申请的硬问题。

当前不能假设 2027 一定仍为 480，因此必须做两件事：

1. 确认吴泰霖 2027 实际招生学科；
2. 等待 / 查询工学院 2027 正式普博规则。

如果仍要求 480，则解决办法是：

- IELTS ≥ 6.0；
- TOEFL ≥ 90；

或 2027 新规则允许的其他英语证明。

这意味着：

> **对吴泰霖这条线，英语目前不能像物理学 A 线那样视为完全解决。**

---

# 9. 课题组资源

2027 博士招聘页直接公开：

- 可调用西湖大学 AI Station；
- H800 / A100 / A800 / V100 等百余张 GPU；
- 实验室拥有多台 8 卡 A6000/L40 服务器；
- 长期租用多台 8 卡 H800 服务器。

课题组自评：

> 计算资源处于国内高校第一梯队。

从硬件信息本身看：

> GPU 资源确实非常充足。

对于 generative models / foundation models / scientific simulation，资源不是明显瓶颈。

---

# 10. 组规模与成熟度

当前官网公开：

- 3 名博士后；
- 8 名博士生；
- 3 名科研/行政助理；
- 9 名访问学生；
- 2 名本科生；
- 7 名 alumni / former members。

组成立于 2023 年，因此：

> **仍属于年轻实验室。**

已有积极去向：

- 博后 Long Wei 将赴复旦大学任助理教授；
- 联合指导博士生 Haodong Feng 将赴中关村学院任研究员 / 博导。

但由于实验室成立时间较短：

> 尚无法像刘仕组一样观察一整代由 PI 独立培养完成的五年制博士毕业周期。

因此培养风险应标记：

> **高水平、高增长，但长期博士培养记录尚未完全成熟。**

---

# 11. 指导和组文化

招聘页公开表述：

- 强调 work-life balance；
- PI 表示会密切陪伴和引导学生；
- 同时鼓励 self-motivated；
- 强调独立思考、自主探索、交流和领导能力；
- 鼓励频繁参加国际顶会。

这些是积极信号。

但需要注意：

> 这些内容来自实验室自己的招聘页面，属于“自我描述”，不能等同于在读生真实体验。

后续必须通过实际学生核实：

- meeting 频率；
- PI 是否真正亲自指导；
- publication pressure；
- 工作时间；
- 项目选择自由度；
- 学生是否容易被大项目拆分成“工程劳动力”。

---

# 12. 国际网络

招聘页明确列出合作/联系网络：

- Stanford
- DeepMind
- MIT
- Caltech
- NVIDIA
- TAMU

并表示会推荐优秀高年级博士生前往这些组：

- internship
- postdoc

对长期希望保留海外科研流动能力的申请者，这是明显优势。

---

# 13. 对申请者最关键的路线判断

吴泰霖不是：

> “比刘仕更先进的 AI4Science”。

而是另一种博士训练产品。

## 如果选择刘仕

你首先会学会：

> physics → DFT → atomistic model → ML potential → MD

成为：

> **计算物理学家**

然后 AI 是强力工具。

---

## 如果选择吴泰霖

你首先必须成为：

> Python / PyTorch / modern deep learning / generative modeling / GNN / neural PDE

能力很强的人，

然后用这些方法解决：

> fluid / plasma / mechanics / engineering / biology

问题。

最终身份更接近：

> **Scientific ML / AI4Science 方法研究者。**

---

# 14. 当前申请叙事

吴泰霖版叙事不能和朱一舟 / 刘仕相同。

## 第一段：物理起点

哈工大应用物理本科，参与材料与数值物理项目。

## 第二段：Scientific Inverse Design 起点

毕业设计：

> microwave absorber  
> + CST Maxwell simulation  
> + Python automation  
> + genetic algorithm

这一经历让申请者首次真正处理：

> high-dimensional scientific design space + expensive physical forward simulator。

## 第三段：认识传统优化的局限

GA 能够搜索结构，但：

- 仍需大量 forward simulation；
- 缺乏可迁移的 learned physical representation；
- 难以扩展到更加复杂的 design/control problem。

因此开始关注：

> learned surrogate models  
> + generative inverse design  
> + scientific ML

## 第四段：第二条经验——Agent

通过学习 Agent / RAG / workflow 项目，进一步接触：

> AI agents + tool use + automated workflow

并意识到：

> AI 不仅可以预测物理系统，也可能参与科学研究流程本身。

## 第五段：为什么吴泰霖

吴泰霖组同时覆盖：

- scientific simulation
- inverse design
- control
- discovery
- AI agents

尤其是：

> 从通用 AI 方法层面解决科学问题，而不是局限于单一材料体系。

这与长期目标高度匹配。

---

# 15. 申请叙事中必须保持诚实

不能写：

- “我有机器学习科研经验”——除非后续补出真实项目；
- “熟练 PyTorch”；
- “熟悉 diffusion model / GNN”；
- “有 AI4Science research publication”。

可以写：

> 我已经做过基于物理仿真器的自动优化与 inverse-design 型本科研究，并正在从 optimization-based scientific computing 向 modern scientific machine learning 转变。

这是成立的。

---

# 16. 套磁策略

## 当前不建议立即按普通 PI 模板发

原因：

吴泰霖招聘要求非常明确，申请者现阶段在：

> ML research experience

上存在明显缺口。

因此第一封邮件应该：

1. 不回避这一 gap；
2. 强调真实 scientific simulation / inverse design 基础；
3. 询问其是否考虑“natural-science background + limited formal ML research”的申请者；
4. 同时确认 2027 招生学科与英语门槛。

如果对方明确表示：

> 需要已有强 ML paper / deep-learning project，

则不继续过度投入。

如果认为：

> physics + computational background 可以培养，

才进入下一阶段。

---

# 17. 中文套磁信母稿 v1

**主题：2027年博士申请咨询｜哈工大应用物理本科｜Scientific ML / AI for Physics**

吴老师您好：

我叫周子靖，2026 年 6 月毕业于哈尔滨工业大学应用物理专业，目前计划申请西湖大学 2027 年博士项目。近期系统了解了您课题组在 AI for scientific simulation、generative inverse design、physical control 以及 AI Agent for scientific discovery 等方面的研究，我对这种从通用 AI 方法层面解决科学仿真和设计瓶颈的研究路线非常感兴趣，因此想向您咨询 2027 年博士生招生情况，以及以我的背景是否适合申请您的课题组。

我的本科科研经历主要集中在物理仿真和计算优化。毕业设计中，我研究了一类电阻膜型微波吸收结构，在已有初始结构思路和参考代码的基础上，主要独立完成了 Python-CST 自动化仿真、结果处理以及基于遗传算法的结构优化工作。这是我第一次比较完整地处理“高维设计空间 + 物理 forward simulator”的问题，也使我对 scientific inverse design 产生了持续兴趣。

此外，我此前也独立参与过学习型 Agent / RAG 系统的开发和工作流设计。这个项目并非机器学习科研，但让我进一步接触了 AI Agent、工具调用和自动化工作流。结合毕业设计经历，我逐渐希望从目前以数值仿真和启发式优化为主的能力，进一步学习现代深度学习、生成模型和 Scientific ML，并研究如何用于真实物理系统的仿真、控制、反向设计和科学发现。

我也想如实说明，目前我的正式科研经历仍以电磁仿真、MATLAB/Python 科研计算和遗传算法优化为主，尚没有以 PyTorch、GNN 或 diffusion model 为核心的机器学习科研项目。因此想请教，您 2027 年招收博士生时，是否会考虑具有较强自然科学和计算研究基础、但需要进一步系统补充现代机器学习方法的申请者？

另外，我注意到您主要在工学院智能信息技术学科招生。我的 CET-6 成绩为 471 分，因此也想确认 2027 年申请您的课题组是否仍需按智能信息技术学科的英语标准报考。

随信附上个人简历和本科成绩单，供您参考。感谢您抽出时间阅读邮件。

祝好！

周子靖  
哈尔滨工业大学 应用物理学学士  
2026 届

---

# 18. 是否应该先补一个 ML 项目再联系？

当前建议：

> **不要为了“看起来会 ML”临时做一个玩具 MNIST 项目。**

没有意义。

如果希望增强吴泰霖线的竞争力，更有价值的是做一个：

> 与本人毕业设计 / physics simulation 真正连接的 Scientific ML mini-project。

例如：

### 方案 A：CST surrogate model

利用已有 CST 数据：

> structure parameters → absorption spectrum

训练一个小型 surrogate network。

再比较：

> CST + GA

与：

> learned surrogate + optimization

在计算成本和预测误差上的差异。

### 方案 B：inverse design

尝试：

> target spectrum → candidate structure

的简单神经网络 / conditional model。

不追求顶会创新，而是证明：

> 申请者已经真正跨过 PyTorch + scientific ML 的第一道门槛。

### 方案 C：physics-aware model

在 surrogate 模型中加入：

> parameter constraints / physically invalid design filtering

展示本人对“physics prior”而非纯拟合的理解。

如果能在不过度侵占考研时间的前提下完成一个小而完整的项目，其申请价值明显高于泛泛学一遍深度学习课程。

---

# 19. 英语问题的处理

当前 CET-6 471。

如果 2027 智能信息技术继续要求：

> CET-6 ≥ 480，

则必须在系统申请前取得其他符合标准的证明，例如：

- TOEFL ≥ 90；
- IELTS ≥ 6.0。

因此这条线应设一个明确 gate：

> **2027 招生简章发布后第一时间确认。**

在确认之前，不应假设 471 足够。

---

# 20. 当前内部评级

| 维度 | 评价 |
|---|---|
| 长期 AI4Science 兴趣匹配 | **极高** |
| Scientific ML 方法匹配 | **极高** |
| 与物理本科身份匹配 | 高 |
| 与 CST+GA 毕设叙事连接 | 高 |
| Agent 经历辅助价值 | 中高 |
| 当前 ML 技能直接匹配 | **偏低** |
| 当前成绩竞争力 | 中等偏低 |
| 招聘要求匹配 | 有明显缺口 |
| GPU/算力资源 | **极高** |
| 国际合作网络 | **极高** |
| PI/组成熟度 | 高增长，但组龄短 |
| 博士完整培养周期证据 | 暂不足 |
| 2027 招生信号 | **明确招生** |
| 英语形式条件 | **潜在硬门槛，待2027规则确认** |
| 当前推荐等级 | **A-/高风险冲刺** |

---

# 21. 与前三位 PI 的阶段性比较

| 维度 | 朱一舟 | 刘仕 | 李文彬 | 吴泰霖 |
|---|---|---|---|---|
| 博士核心身份 | AI Materials | Computational Physics | Electronic Materials Physics | **Scientific ML / AI4Science** |
| 物理问题中心性 | 高 | **极高** | **极高** | 中高 |
| AI 方法中心性 | 高 | 高 | 中高 | **极高** |
| 计算材料 | **极高** | 高 | **极高** | 低-中 |
| PDE/连续系统 | 低 | 低 | 低 | **极高** |
| inverse design | 高 | 中 | 中 | **极高** |
| AI Agent | 低 | 低 | 低 | **高** |
| 与现有 CST+GA 连接 | 高 | 高 | 中高 | **高** |
| 当前技能直接匹配 | 中 | 中 | 中 | **偏低** |
| 需要补 ML | 高 | 中高 | 中高 | **极高** |
| 申请门槛风险 | 中 | 中 | 中高 | **很高** |
| 当前优先级 | A+ | A+ | A-/B+ | **A-/冲刺** |

---

# 22. 当前决策

**保留并认真申请，但不应把吴泰霖视为“最稳的第一志愿 PI”。**

正确定位：

> **高价值、高风险冲刺对象。**

其价值：

- 是目前最纯粹的 AI4Science 方法组；
- 研究方向与长期兴趣高度一致；
- 物理 + AI 背景真实；
- 算力和国际合作极强；
- Scientific ML / inverse design / AI Agent 都与申请者兴趣产生连接。

其风险：

- 申请者目前 ML research 太弱；
- 学业成绩不是优势；
- 招聘文字明确要求高；
- CET-6 471 可能不满足智能信息技术 2027 形式门槛；
- 组成立时间较短，完整五年博士培养记录尚有限。

因此后续策略是：

1. 先确认 2027 英语与招生学科；
2. 套磁直接询问是否接受“physics/computation background but limited formal ML research”；
3. 如得到正面信号，再投入时间补 Scientific ML mini-project；
4. 不因关键词高度匹配而在未收到导师正面反馈前大量侵占考研时间。

---

# 23. 后续待办

- [ ] 确认 2027 智能信息技术英语门槛
- [ ] 确认吴泰霖是否只能通过智能信息技术招生
- [ ] 确认 2027 实际博士名额数量
- [ ] 阅读 Compositional Generative Inverse Design
- [ ] 阅读 RealPDEBench
- [ ] 浏览 BuildArena 项目与代码结构
- [ ] 调查在读博士本科/硕士背景
- [ ] 询问组内真实工作强度和 PI 指导频率
- [ ] 判断是否值得在考研期间做一个 CST-surrogate Scientific ML mini-project
- [ ] 制作英文 Academic CV
- [ ] 在与鲍芳琳完成横向比较后决定第一批/第二批套磁顺序
