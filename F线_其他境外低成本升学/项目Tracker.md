# F线项目 Tracker

更新：2026-09-29
状态：第一轮广扫后候选跟踪表。`CANDIDATE/HOLD/DROP` 为调研状态，不等于申请状态；本轮无 READY/SENT/SUBMITTED。

> 2026-09-29新增：除 Funding Gate / Eligibility Gate 外，正式第二轮必须同时执行 `Geo/Security Gate`。详细规则见 [`政治与研究安全风险Gate.md`](政治与研究安全风险Gate.md)。加拿大 F003/F004/F005 由于 HIT 被列入加拿大 Named Research Organizations，当前均记 `PASS/HOLD`：HIT 历史学历本身不构成 STRAC admission ban，但需核 current affiliation、funding source 与 sensitive-technology research。澳洲 HDR 记 `PASS/HOLD`；德国/法国/意大利/奥地利/日本/新加坡目前无已核实的 HIT-specific blanket ban，不据此降桶，但具体敏感项目仍须查 export-control / research-security 条件。未来美国项目默认 `HOLD-HIGH`，先核 PP10043 / Entity List / visa / lab-access 风险。

| ID | 项目 | 类型 | Funding Gate | Eligibility Gate | 当前桶 | 下一步 | 状态 |
|---|---|---|---|---|---|---|---|
| F001 | ISTA PhD 2027 | bachelor-entry PhD | PASS A | PASS | S | 查 physics/scicomp/materials groups + selection profile + project-level security restrictions | CANDIDATE |
| F002 | OIST PhD 2027 | bachelor-entry PhD | PASS A | PASS | S | 查 6–10 个可迁移 research units + rotation fit + security restrictions | CANDIDATE |
| F003 | UBC MSc Physics | funded thesis MSc | PASS A-like | PASS pending grade equivalency | P1 | 查 2027 deadline、PI consent、80.2/100 equivalency + STRAC/funding/current-affiliation | CANDIDATE |
| F004 | McGill MSc Physics | funded thesis MSc | PASS A-like | HOLD grade equivalency | P1 | 查 China grade equivalency + potential supervisors + STRAC/funding/current-affiliation | CANDIDATE |
| F005 | McMaster MSc Physics | funded thesis MSc | PASS A-like | PASS/HOLD supervisor fit | P1/P0 | 先查 active supervisors + rolling funding timing + STRAC/funding/current-affiliation | CANDIDATE |
| F006 | Paderborn MSc Physics | low-tuition research MSc | PASS C | PASS | P0 | 查 specialization + thesis groups + living/HiWi + project security | CANDIDATE |
| F007 | Greifswald MSc Physics | low-tuition research MSc | PASS C | PASS | P0 | 查 IPP/INP thesis routes + plasma/soft matter groups + project security | CANDIDATE |
| F008 | Osnabrück MSc Physics | low-tuition research MSc | PASS C | PASS | P0 | 查 relevant groups + actual living budget + project security | CANDIDATE |
| F009 | HHU Düsseldorf MSc Physics | low-tuition research MSc | PASS C | PASS | P0 | 查 plasma/soft matter/computational supervisors + project security | CANDIDATE |
| F010 | Saarland MSc Physics | low-tuition research MSc | PASS C | PASS | P0 | 查 thesis research areas + cash budget + project security | CANDIDATE |
| F011 | Jena MSc Photonics | low-tuition research MSc | PASS C | PASS | P1 | 查 2027 deadline + Abbe groups + scholarship/HiWi + project security | CANDIDATE |
| F012 | Jena MSc Physics | low-tuition research MSc | PASS C | PASS/HOLD curriculum audit | P0/P1 | 对照 HIT transcript 核 physics/math credits + project security | CANDIDATE |
| F013 | TU Dortmund MSc Physics | low-tuition MSc | PASS C | PASS | P0 | 查 research profile + thesis groups + project security | CANDIDATE |
| F014 | Bremen MSc Physics | low-tuition MSc | PASS C | HOLD language/credit audit | P1 | 核 C1/B2 discrepancy + 80CP physics + project security | CANDIDATE |
| F015 | Hannover MSc Physics | low-tuition MSc | PASS C | PASS/HOLD | P1 | 查 photonics/metrology thesis groups + project security | CANDIDATE |
| F016 | FU Berlin MSc Physics | low-tuition research MSc | PASS C | PASS/HOLD | P1 | 核 admission conversion + living cost + project security | CANDIDATE |
| F017 | KIT MSc Physics | non-EU tuition | HOLD C | PASS | HOLD/P1 | 只有独特 PI/奖学金时重开；同时核 project security | HOLD |
| F018 | Ulm MSc Physics | non-EU tuition | HOLD C | HOLD grade/top20 | HOLD | 核 German grade equivalency；不过则 DROP | HOLD |
| F019 | Paris-Saclay M1 General Physics | research MSc | HOLD B/C | PASS | P1/HOLD | 核 2027 tuition/waiver/scholarship + project security | CANDIDATE |
| F020 | Paris-Saclay M1 Physics & Applications | research MSc | HOLD B/C | PASS | P1/HOLD | 核授课语言 + funding + project security | CANDIDATE |
| F021 | Europhotonics EMJM | scholarship MSc | PASS if scholarship | PASS | S/P1 | 等 2027 call，核 scholarship seats/selection + mobility security | CANDIDATE |
| F022 | iPSRS EMJM | scholarship / zero-tuition MSc | PASS B/C | HOLD full eligibility | P1 | 2026-10 call open后核完整条件 + mobility security | CANDIDATE |
| F023 | Padua Physics MSc | scholarship master | PASS if award | PASS/HOLD | P1 | 核 exact Physics programme + 2027 Excellence call + project security | CANDIDATE |
| F024 | Trieste Physics MSc | low-cost MSc | HOLD C | PASS/HOLD | P1/HOLD | 核 English track、net tuition、thesis structure + project security | HOLD |
| F025 | Tohoku IGPAS Physics MSc | MEXT-linked research MSc | PASS if MEXT | PASS | P1 | 查 supervisor list + 2027 application deadline + project security | CANDIDATE |
| F026 | KAUST MS Applied Physics | fully funded MSc | PASS A | PASS | S/P1 | 查 AP faculty + admission selectivity + project security | CANDIDATE |
| F027 | KAUST MS MSE thesis | fully funded MSc | PASS A | PASS | S/P1 | 查 modeling/device/materials groups + project security | CANDIDATE |
| F028 | KAUST AMCS MS/PhD | bachelor-entry fully funded | PASS A | PASS/HOLD quant fit | S | 查 numerical/scicomp faculty与先修 + project security | CANDIDATE |
| F029 | NUS Physics PhD | direct PhD | HOLD/PASS B | HOLD honours-equivalent | S | 查 eligibility wording + selective PIs + security/export-control restrictions | CANDIDATE |
| F030 | NTU Physics PhD | direct PhD | PASS if scholarship | PASS | S | 核 GRE/GATE + scholarship deadlines + security/export-control restrictions | CANDIDATE |
| F031 | NTU Ran Ni Group PhD | project/group PhD | PASS if scholarship | PASS | P1/S | 查近作、openings、SINGA/NTU scholarship route + project security | CANDIDATE |
| F032 | NTU Spintronics Lab PhD | funded group PhD | PASS B/high | PASS | P1 | 查 current openings + group fit + project security | CANDIDATE |
| F033 | SINGA project pool | fully funded PhD award | PASS if award | PASS/HOLD | S | 按 materials/waves/physics筛具体 project + security/export-control restrictions | CANDIDATE |
| F034 | ANU MPhil Physics | HDR research master | HOLD B | HOLD honours-equivalence | HOLD | formal equivalency check only if strong project；Geo/Security PASS/HOLD | HOLD |
| F035 | ANU PhD + RTP | funded HDR | PASS if scholarship | HOLD | HOLD | 当前不占主申请名额；Geo/Security PASS/HOLD | HOLD |
| F036 | UQ HDR + UQGSS/RTP | funded HDR | PASS if scholarship | HOLD | HOLD | supervisor明确接受当前学历再开；Geo/Security PASS/HOLD | HOLD |
| F037 | Otago Physics PhD 2027 | funded PhD | PASS if scholarship | HOLD | DROP | 2027 round deadline已过 | DROP |
| F038 | Auckland Physics PhD | funded PhD | HOLD | HOLD | HOLD/2028 | 2028再评估 + security rules | HOLD |
| F039 | KU Leuven MSc Physics | master | FAIL/HOLD | PASS | HOLD | 中国是否有其他 scholarship；否则不占名额 | HOLD |
| F040 | Copenhagen MSc Physics | master | FAIL without scholarship | PASS/HOLD ECTS | HOLD | 仅 full scholarship现实可行时重开 | HOLD |

## 第二轮优先队列

**F-1 funded MSc / probability layer**：F005 → F006 → F007 → F009 → F008 → F003 → F004。

**F-2 bachelor-entry funded PhD**：F001 → F002 → F031 → F032 → F030 → F033 → F029。

**F-3 scholarship masters**：F025 → F021 → F022 → F026/F027/F028 → F023 → F019。

## Geo/Security Gate 当前特别处理

- **Canada F003/F004/F005**：`PASS/HOLD`。HIT 在加拿大 NRO 名单中；历史学历不触发 STRAC 自动排除，但 current HIT affiliation/support + federally funded sensitive technology project 可能冲突。
- **Australia F034/F035/F036**：`PASS/HOLD`。存在 university foreign-interference / research-security due diligence；尚未核到 HIT-specific admissions ban。
- **Germany / France / Italy / Austria / Japan / Singapore**：暂记 `PASS/HOLD-project-level`，不得据“未发现统一禁令”推导为零风险。
- **United States（未来新增）**：默认 `HOLD-HIGH`；HIT 背景叠加 PP10043 与 BIS Entity List 风险，academic offer 不等于 visa / lab access 可行。

## 硬规则

- 未核 funding、bachelor eligibility 与 Geo/Security Gate，不升级。
- scholarship exists 不等于 budget PASS。
- academic admission possible 不等于 visa / controlled-lab access possible。
- 任何 `S/P1/P0` 都只是 internal research bucket。
- 不因 PI friendly wording、年轻组、学校品牌低而宣称“竞争小”。
- 只有完成第二轮项目/PI级证据后，才讨论有限申请名额的最终组合。