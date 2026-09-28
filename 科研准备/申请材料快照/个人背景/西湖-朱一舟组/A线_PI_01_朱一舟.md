# A线导师档案 01｜朱一舟（Yizhou Zhu）

> 用途：西湖大学 A 线申请内部工作文档。用于后续查阅、套磁、材料定制、面试准备与最终决策。  
> 状态：**A+｜第一批联系对象｜暂未发送套磁**

---

## 0. 一句话结论

朱一舟是当前西湖 A 线中与申请者长期目标高度匹配的核心 PI 之一。

最自然的申请叙事不是“我已经会 AI/DFT”，而是：

> **从应用物理与电磁材料出发，通过 CST + Python + 遗传算法完成过真实的计算设计工作，并由此希望进一步进入原子尺度计算、第一性原理、机器学习势函数与 AI for Materials。**

当前主要优势是研究兴趣、方法论和申请故事高度连贯；主要短板是尚无 DFT、MLFF、深度学习、Linux/HPC 的实际项目经验。

---

# 1. 申请者背景摘要

## 1.1 学术背景

- 哈尔滨工业大学应用物理本科
- 2026 年 6 月毕业
- 已取得学历、学位证书
- 本科专业排名约 21–22 / 46
- 算术平均分约 80.2 / 100
- CET-6：471
- 无挂科、无延毕

## 1.2 真实科研资产

### A. 本科毕业设计——当前最重要的申请资产

课题：电阻膜型宽带微波吸收结构的仿真与优化设计

主要内容：

- CST 电磁仿真；
- Python 自动调用 CST；
- 自动读取与处理仿真结果；
- 使用遗传算法进行参数搜索；
- 根据实际设计问题逐步增加搜索自由度；
- 补充筛选逻辑；
- 调试和改进整个自动优化流程；
- 保存有原始 Python 代码、CST 文件和毕业论文。

独立性：

导师给出课题；学长提供基本结构思路、参考代码和 CST 软件环境；后续主体工作由本人在学习、调试和迭代中完成。

**申请意义：**
不是简单“会用遗传算法”，而是已经独立完成过：

> physics forward model → automation → optimization → scientific design

这一完整科研工作流。

---

### B. 二维尘埃等离子体晶格波项目

论文作者排序第六。

真实贡献：

- 使用 MATLAB 仿真处理晶格中的偏振；
- 输出和处理数据；
- 绘制结果图；
- 保留有原始代码。

**申请意义：**
可作为第二项“数值物理 / 科研编程”证据。

---

### C. 磁纳米合金/石墨烯吸波材料项目

论文作者排序第四。

真实贡献：

- 数据处理；
- 图像绘制；
- 文本写作；
- 围绕项目参加大学生创新项目，并获得国家级项目结题证书。

实验参与度有限，申请时不得夸大为核心实验工作。

---

### D. 其他论文 / 专利

部分论文、专利署名参与度较低。

原则：

- CV 中可诚实列出；
- 不作为核心科研能力证明；
- 被追问时如实说明具体贡献；
- 不使用“主导”“核心完成”等表述。

---

# 2. 技能画像

## 已有真实项目经验

- Python 科研脚本
- MATLAB 数值计算
- CST 电磁仿真
- CST-Python 自动化
- 遗传算法优化
- 数据处理与可视化
- Git 基础工作流
- AI 辅助科研编程与调试
- 科研问题的独立迭代和排错

## 尚未形成真实项目经验

- DFT
- VASP / Quantum ESPRESSO
- 分子动力学
- ML interatomic potentials
- PyTorch / JAX
- GNN
- diffusion model
- Linux / HPC
- 大型科研软件工程

正确定位：

> 已经通过计算物理和优化进入数据/计算驱动科研，希望在博士阶段系统学习第一性原理、原子模拟和 physics-informed machine learning。

不应自称已经是 AI4Science / ML Materials 研究者。

---

# 3. 朱一舟组的核心研究画像

## 3.1 总体方向

重点关注：

- Computational Materials
- AI for Materials Discovery
- High-throughput computation
- Machine-learning force fields
- Solid-state materials
- Solid-state electrolytes
- Crystal structure determination
- Data-driven / AI-assisted materials characterization

## 3.2 当前最值得关注的方法论

不是单纯“把神经网络套到材料数据上”，而是：

> **Materials knowledge + Physics + First-principles + Automation + Machine Learning**

其近期工作反复体现：

- 把热力学、晶体学和化学约束加入自动分析；
- 把已知短程物理作用加入机器学习势函数；
- 把几何对称性 / 等变性编码进生成模型；
- 使用 DFT 等物理方法继续验证 AI 结果。

核心特点：

> **已知物理结构不浪费数据重新学习；机器学习主要负责复杂、难显式建模或高维搜索的部分。**

---

# 4. 三篇代表工作及申请意义

## 4.1 AutoMapper / 高通量 XRD 自动相图分析

核心问题：

- 大量材料样品产生大量 XRD；
- 传统人工分析效率低；
- 单纯数学拟合可能得到物理不合理的相组成。

方法骨架：

> XRD forward model  
> + 候选晶相数据库  
> + 第一性原理 / 热力学信息  
> + 晶体学与组成约束  
> + 自动优化

与申请者毕业设计的方法论联系：

> CST forward simulation  
> + Python automation  
> + GA search  
> + design constraints

研究对象不同，但都属于：

> **physics-based forward model + automated search + domain constraints**

这是当前最容易与本人过去科研形成连接的一篇工作。

---

## 4.2 Physics-informed MLFF

核心问题：

使用机器学习势函数替代昂贵 DFT，从而进行大规模分子动力学模拟。

基本链条：

> DFT data  
> → ML potential  
> → molecular dynamics

关键思想：

纯数据模型在训练分布之外可能出现非物理行为，因此加入已知短程排斥物理：

> V_total = V_ML + V_short-range

申请意义：

本人在遗传算法优化中也实际遇到过：

> “objective function 数值更好” ≠ “设计具有真实物理意义”

因此可自然理解 physics prior + data-driven model 的价值。

---

## 4.3 XRDSol / 扩散模型反演晶体结构

核心问题：

> Crystal structure → PXRD

是 forward problem，而实验真正希望解决：

> PXRD → Crystal structure

属于典型 scientific inverse problem。

方法：

- diffusion model
- equivariant graph neural network
- 晶体几何与对称性
- DFT / crystallography 验证

与本人毕业设计的联系：

本人此前：

> structure parameters  
> → CST  
> → absorption spectrum

再通过：

> GA + forward simulation

寻找满足目标性能的结构。

两者都属于更广义的：

> **Inverse Scientific Design / Inverse Problem**

区别在于：

- 本人：Maxwell-scale + evolutionary search
- 朱一舟组：atomic-scale + generative AI

---

# 5. 为什么与申请者匹配

## 5.1 高匹配项

- 更偏计算而非纯实验；
- 希望 AI 服务于真实物理问题；
- 对计算材料 / AI4Science 有长期兴趣；
- 已经做过 physics simulation + automation + optimization；
- 不要求博士继续做微波吸收；
- 愿意补 DFT、固体、ML、Linux/HPC 等基础；
- 接受直接 5 年博士。

## 5.2 现有科研迁移链条

> Applied Physics  
> ↓  
> Electromagnetic Materials  
> ↓  
> CST Electromagnetic Simulation  
> ↓  
> Python Automation  
> ↓  
> Genetic Algorithm Optimization  
> ↓  
> Computational Design  
> ↓  
> Atomistic Modelling / DFT  
> ↓  
> ML Potentials / Scientific ML  
> ↓  
> AI for Materials / AI4Science

这是当前最重要的申请故事。

---

# 6. 主要短板和风险

## 6.1 方法栈差距

当前尚未实际做过：

- DFT
- MD
- MLFF
- PyTorch
- GNN
- diffusion
- Linux/HPC

因此申请策略必须是：

> 强调已有计算研究能力与学习能力，同时明确博士阶段希望系统训练这些方法。

绝对不能包装成已经熟练掌握。

## 6.2 本科成绩

整体成绩不是申请优势，核心理论课程部分成绩偏低。

策略：

- 不回避；
- 不把自己包装成纯理论高分型学生；
- 用科研独立性、代码、项目完成度和方法迁移潜力补偿；
- 考研阶段继续补量子、热统、固体物理，为面试做准备。

## 6.3 研究对象迁移

朱一舟组主要科学对象并非微波吸波材料，而是无机固体、固态电解质、晶体结构、材料发现等。

申请时必须明确：

> 对研究问题和方法的兴趣高于对“必须继续吸波材料”的执念。

---

# 7. 推荐信策略

## 第一推荐人

**李均教授**

理由：

- 毕设导师；
- 班主任；
- 长期合作多个项目和比赛；
- 能具体评价科研执行力、独立性、解决问题能力。

应争取成为强推荐信。

## 第二推荐人

候选：**田浩教授**

优势：

- 学院院长；
- 光学课程授课老师；
- 曾参与其团队项目。

待确认：

- 是否能写出足够具体的个人评价。

原则：

> 推荐信的具体性与可信度优先于推荐人头衔。

---

# 8. 给朱一舟的申请叙事骨架

## 第一段：起点

本科从电磁材料科研进入真实的结构—性能问题。

## 第二段：独立计算科研

毕业设计中把 CST、Python 与遗传算法连接起来，从人工试错转向自动化计算设计。

## 第三段：兴趣形成

复杂设计空间无法依赖人工穷举，由此认识到：

> computational methods can fundamentally change how scientific design problems are explored.

开始关注：

- computational materials
- inverse problems
- AI for Science

## 第四段：博士阶段迁移

希望从：

> electromagnetic-scale modeling

进一步进入：

> atomistic simulation  
> first-principles calculations  
> ML potentials  
> physics-informed machine learning  
> AI-assisted materials discovery

## 第五段：为什么朱一舟

重点不是泛泛“AI + materials”，而是：

> 她的工作持续把 materials knowledge / physical constraints 与 data-driven methods 结合，而非把 ML 当成黑箱。

---

# 9. 套磁语言策略

## 推荐方案

**中文正文 + 英文 Academic CV + 官方成绩单**

原因：

- 导师为中文母语者；
- 第一封套磁本质是建立沟通，不是正式英文写作考试；
- 中文可以更精准、自然地表达科研经历和转向逻辑；
- 更容易避免模板化英文群发感；
- 英文 CV 仍可体现后续国际科研沟通能力。

如果导师后续主动使用英文回复，则之后跟随导师语言切换即可。

---

# 10. 中文套磁信母稿 v1

**主题：2027年博士申请咨询｜哈工大应用物理本科｜计算材料与 AI for Materials**

朱老师您好：

我叫周子靖，2026 年 6 月毕业于哈尔滨工业大学应用物理专业，目前计划申请西湖大学 2027 年博士项目。近期了解了您课题组在计算材料、机器学习势函数以及 AI 辅助材料发现等方面的工作，我对其中将材料物理知识与数据驱动方法结合的研究思路非常感兴趣，因此想向您咨询 2027 年博士生招生情况以及我的背景与课题组方向是否具有一定匹配度。

我的本科科研经历主要集中在电磁材料和计算建模。毕业设计中，我研究了一类电阻膜型微波吸收结构。在导师和学长提供初始课题思路、参考代码与 CST 环境后，我主要独立完成了后续工作，包括使用 Python 自动调用 CST 进行参数化电磁仿真、处理仿真结果，并搭建和逐步改进基于遗传算法的结构优化流程。这个过程让我第一次比较系统地体会到，自动化计算和算法搜索可以把依赖人工试错的复杂设计问题转化为可系统探索的问题，也使我逐渐对计算材料、科学逆问题以及 AI for Science 产生了更强的兴趣。

目前我的实际项目经验仍主要集中在电磁仿真、科研脚本和优化计算，还没有正式参与过 DFT、分子动力学或机器学习势函数项目。因此我希望在博士阶段系统学习第一性原理、原子尺度模拟以及 physics-informed machine learning，并逐渐从宏观电磁结构优化进一步进入计算材料与 AI 辅助材料设计。

我尤其关注到您课题组近年来并不是单纯使用黑箱机器学习，而是持续将材料知识和物理约束引入数据驱动模型与自动化分析中。这种研究思路与我希望发展的方向非常契合。

想请问您 2027 年是否还有博士生招生名额，以及以我目前的物理和计算背景，是否适合申请您的课题组？随信附上个人简历和本科成绩单，供您参考。

感谢您抽出时间阅读邮件。

祝好！

周子靖  
哈尔滨工业大学 应用物理学学士  
2026 届

---

# 11. 套磁信中不得夸大的内容

禁止：

- “熟练机器学习”
- “熟练 DFT”
- “熟练 VASP / QE”
- “具有丰富 AI4Science 经验”
- “developed a genetic algorithm”
- 把挂名论文写成核心科研成果
- 把有限实验参与写成材料制备主导者

推荐表述：

> implemented and adapted a genetic-algorithm-based optimization workflow

或中文：

> 搭建并逐步改进了基于遗传算法的自动优化流程。

---

# 12. 第一封邮件附件

建议仅：

1. **Academic CV（英文，建议 2 页）**
2. **官方本科成绩单**

暂不主动发送：

- 毕业论文全文
- Python 代码
- CST 工程
- 所有论文全文
- 专利证明
- CET-6 成绩单
- 比赛证书

如果导师感兴趣，再发送第二层材料。

---

# 13. 后续如获回复的处理

## 弱正面信号

> “有名额，可以正常申请。”

含义：

- 允许申请；
- 尚不能说明导师特别感兴趣；
- 继续正常准备材料。

## 中强信号

导师开始询问：

- 毕设细节；
- 代码；
- 论文；
- 研究方向；
- 成绩；
- 是否愿意线上交流。

说明已经进入实质筛选。

## 强信号

> 邀请 Zoom / 腾讯会议 / 电话交流。

应立即进入：

- 研究汇报 PPT；
- 毕设复盘；
- 代表论文理解；
- DFT / MLFF 基础；
- “为什么直博 / 为什么转方向”面试准备。

---

# 14. 当前状态卡

- PI：朱一舟
- 学校：西湖大学
- 方向：Computational Materials / AI for Materials
- 内部评级：**A+**
- 研究兴趣匹配：**高**
- 现有背景连接：**高**
- 方法迁移难度：**中高但合理**
- 2027 招生信号：**明确存在博士岗位信号**
- 套磁母稿：**已完成**
- CV：**待制作**
- 成绩单：**已有**
- 论文阅读：**已完成第一轮申请者视角导读**
- 正式联系：**暂缓，待与其他核心 PI 横向比较后统一决定第一批发送顺序**

---

# 15. 后续待办

- [ ] 进一步确认 2027 实际招生名额与招生学科
- [ ] 制作英文 Academic CV
- [ ] 精读至少 1 篇代表论文
- [ ] 准备毕业设计 1 页项目摘要
- [ ] 梳理毕业设计代码与 CST 文件，确保可展示
- [ ] 确认李均教授推荐意愿
- [ ] 确认第二推荐人
- [ ] 与刘仕等核心 PI 横向比较
- [ ] 决定是否进入第一批正式套磁
