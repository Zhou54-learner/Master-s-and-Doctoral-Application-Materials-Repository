# 00 · Source Record

2026-09-27｜INTERNAL｜**材料已准备 / 待本人学习**

## 核实的文献身份

**PAPER-SUPPORTED，P1 首页、末两页；出版元数据经 APS 页面复核。**

Gui-Geng Liu, Subhaskar Mandal, Peiheng Zhou, Xiang Xi, Rimi Banerjee, Yuan-Hang Hu, Minggui Wei, Maoren Wang, Qiang Wang, Zhen Gao, Hongsheng Chen, Yihao Yang, Yidong Chong, Baile Zhang. *Localization of Chiral Edge States by the Non-Hermitian Skin Effect*. **Physical Review Letters 132, 113802 (2024)**. [DOI: 10.1103/PhysRevLett.132.113802](https://doi.org/10.1103/PhysRevLett.132.113802).

正式发表 2024-03-12；卷期日期 2024-03-15，两者不要混用。前四位作者等贡献；通讯作者为 Yihao Yang、Yidong Chong、Baile Zhang。刘癸庚为共同第一作者之一，当时署名单位为 NTU，不称此文为其在西湖独立组建团队后完成的独立成果。

## 实际取得的来源

访问日期均为 2026-09-27；精确 UTC 时间、字节数及逐文件 SHA-256 见 [acquisition_log.json](sources/acquisition_log.json)，全部留存来源的现存哈希见 [source_manifest.json](sources/source_manifest.json)。下面的“取得”仅描述助理的来源工作。

| ID | 原始来源与版本 | 本地文件 / 实际状态 |
|---|---|---|
| P1 | [刘组官网提供的正式排版 PDF](https://www.liuguigeng.com/wp-content/uploads/2025/12/Localization-of-Chiral-Edge-States-by-the-Non-Hermitian-Skin-Effect.pdf)；页眉 PRL 132, 113802，6 页，2024 正式版 | [paper_published.pdf](sources/paper_published.pdf)；已取得并核读；正文科学论据主来源。路径含 2025/12 是网站文件路径，不是发表日期 |
| P0 | [APS 正式页面](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.132.113802) | 浏览工具可读摘要/作者/日期；直接下载 HTML 返回 403，未伪造网页副本；访问观察见 [记录](sources/access_notes.md) |
| S1 | [正式 Supplemental Material 入口](https://link.aps.org/supplemental/10.1103/PhysRevLett.132.113802)；由 P1 参考文献 50 指向 | **未取得、未阅读**；APS 页面显示订阅要求；直接请求 403，API 401。没有可核实文件名、版本、页数、哈希 |
| O1 | [刘癸庚组 Research](https://www.liuguigeng.com/research/)，第 2 项 Non-Hermitian Photonic Chern Insulator | [lab_research.html](sources/lab_research.html)；已取得。属于组官方研究说明 |
| O2 | [刘组 Publications](https://www.liuguigeng.com/publications/)，该论文条目（访问时编号 26） | [lab_publications.html](sources/lab_publications.html)；标题/DOI/全文链接相互对应 |
| PP1 | [arXiv:2305.13139v1](https://arxiv.org/abs/2305.13139)，2023-05-22 | [预印本 PDF](sources/arxiv_2305.13139v1.pdf)、[摘要页](sources/arxiv_abstract.html)；14 页，仅作版本对照，**不是补充材料** |

正式 PDF SHA-256：`039ad1fa9824156325ce9ea70decc3575617b59c9b009efb1dc241181bf4fa07`。

**官方说明（O1；不能当成独立论文证据）：** 组官网把该工作归于非厄米光子 Chern 绝缘体，说明利用损耗的空间配置使边缘态复谱产生 point-gap winding，并与 Chern 拓扑共同决定局域化。它与邮件点名工作的主题和 P1 一致，不需要另换论文。

## 版本风险：不要把预印本的实验段落接到正式图上

**PAPER-SUPPORTED，P1 pp.3–4 / Fig.3；版本对照 PP1 pp.6–7。** 正式版描述测量各个组成偶极源产生的场，再得到空间结构化线源的响应；其空间分布匹配目标态。2023 v1 则描述单源场及传播损耗补偿/重构的处理。两个版本不应拼接成同一套最终实验方法。本包的 Fig.2–4 全取 P1，实验解释也只依 P1；未从 PP1 补造最终版的源相位/权重。

## 补充材料待补核清单

P1 参考文献 50 说明 S1 包含下列内容，**这只能证明正文引用了它们，不能证明助理已核验其细节**：

| 待核项 | 现有正文能支持到哪里 | 取得 S1 后的最小动作 |
|---|---|---|
| 非厄米 Chern 数计算 | P1 p.3 给 C₂=-1、C₃=+1 | 核对内积/左右本征矢或等价方法、材料色散处理；不自行宣称算法已掌握 |
| 材料与装置、数值参数 | P1 给旋磁柱、0.7 T、平行板、损耗包覆与铜边界 | 核对材料模型、损耗参数、网格/求解方法；不把正文 “first-principles” 误读成 DFT |
| 阵列激励 | P1 pp.3–4 给逐偶极测量与组合响应 | 核对幅相权重、组合方法、测量归一化及对照 |
| 鲁棒性 | P1 结论提出局部缺陷鲁棒性，细证据转引 S1 | 核对具体缺陷、强度、频率、比较基准；不推广到任意无序 |
| 补图对照 | 正文提到 S1、S3–S7、S8 | 按正文引用逐一对应；不预填补图结论或虚构截图 |

公开替代来源也已检查：作者网站仅找到正式主文；arXiv v1 无附录式 SM；NTU [机构记录](https://hdl.handle.net/10356/174762) 的公开接口返回 metadata.only，文件包只有 LICENSE。未登录他人账号、未绕过访问控制。已向用户请求已有 SM 的本地路径；当前不自动联系作者索取。

## 证据使用规则

**INTERPRETATION。** 正文支持的定性主线可以开始学习；精确复现参数、补图对照与鲁棒性范围留空。后续取得 S1 时保留现有版本记录，新增文件、哈希及核验日期，再按证据修订相关答案。该来源缺口意味着“所有原始来源均已取得”目前不成立。
