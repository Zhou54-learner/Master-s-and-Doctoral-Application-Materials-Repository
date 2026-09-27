# 来源访问观察

2026-09-27，助理执行记录；与 acquisition_log.json 配合使用。本文件是观察笔记，不是 APS/NTU 网页原件。

- APS 摘要页经浏览工具可读：标题、14 位作者、2024-03-12 发表日期与 DOI 均与作者官网正式 PDF 一致。页面标出 Supplemental Material 的订阅要求。直接 HTTP 下载页面和 supplemental 入口返回 403；harvest API 返回 401。
- `https://link.aps.org/supplemental/10.1103/PhysRevLett.132.113802` 是主文参考文献 50 中给出的原始入口。没有取得有效的补充 PDF；不能把访问错误页面命名为补充材料。
- 官方网站 WordPress 公开媒体检索 Localization / skin 只定位到主文，supplement 未返回相关文件。未找到不等于作者没有补充文件。
- NTU 记录 `https://hdl.handle.net/10356/174762` 可由公开接口 `https://dr.ntu.edu.sg/server/api/pid/find?id=10356/174762` 核验，条目 UUID 为 `e31bdfcc-6e5b-4afd-9ce7-12c0fed5a9b1`。访问时权利字段为 metadata.only，bundles 仅有 LICENSE，不提供文章/补充 PDF。
- arXiv v1 下载是 14 页主文；尝试 source 入口返回的仍是同一主文 PDF（哈希一致），不当作源代码或 SM，重复候选已移除。
- 合作者公开出版目录只给 DOI，未找到额外补充文件。
- 本包将缺口交还为 S1 待补核，不用非原始二手解读填补。
