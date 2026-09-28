"""Read-only checks of transcribed grades and archived simulation output."""
import csv
import json
import math
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "材料" / "成绩单转录_20260926.csv").open(encoding="utf-8-sig", newline="") as stream:
    rows = list(csv.DictReader(stream))
numeric = [r for r in rows if r["score"]]
credits = sum(float(r["credits"]) for r in rows)
assert credits == 242.5, credits
assert len({(r["page"], r["column"], r["row"]) for r in rows}) == len(rows)
grade_result = {
    "total_rows": len(rows),
    "numeric_rows": len(numeric),
    "total_credits": credits,
    "numeric_credits": sum(float(r["credits"]) for r in numeric),
    "score_sum": sum(float(r["score"]) for r in numeric),
    "arithmetic_mean": mean(float(r["score"]) for r in numeric),
    "credit_weighted_mean": sum(float(r["score"]) * float(r["credits"]) for r in numeric)
    / sum(float(r["credits"]) for r in numeric),
    "excluded_pass_fail_rows": len(rows) - len(numeric),
}
print(json.dumps({"transcript": grade_result}, ensure_ascii=False, indent=2))

archive = Path(r"F:\biyesheji\最终结果ohmic_sheet_12x12_multitemplate_topology_ga")
with (archive / "best_s11_ohmic_sheet_12x12.txt").open(encoding="utf-8-sig", newline="") as stream:
    curve = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(stream, delimiter="\t")]
freq = [r["freq_GHz"] for r in curve]
rl = [r["rl_dB"] for r in curve]
assert all(b > a for a, b in zip(freq, freq[1:]))
assert max(abs(r["rl_dB"] - 20 * math.log10(r["s11_mag"])) for r in curve) < 1e-9
intervals, start = [], None
for i, value in enumerate(rl):
    if value <= -10 and start is None:
        start = i
    if start is not None and (value > -10 or i == len(rl) - 1):
        end = i - 1 if value > -10 else i
        intervals.append((start, end))
        start = None
lo, hi = max(intervals, key=lambda pair: freq[pair[1]] - freq[pair[0]])
step = mean(b - a for a, b in zip(freq, freq[1:]))
assert max(abs((b - a) - step) for a, b in zip(freq, freq[1:])) < 1e-9
bandwidth = freq[hi] - freq[lo]
result = {
    "source": str(archive / "best_s11_ohmic_sheet_12x12.txt"),
    "samples": len(curve), "step_GHz": step,
    "sampled_interval_GHz": [freq[lo], freq[hi]],
    "sampled_contiguous_bandwidth_GHz": bandwidth,
    "coverage_percent": bandwidth / 16 * 100,
    "minimum_reflection_dB": min(rl),
    "point_count_times_step_GHz_not_interval_width": sum(v <= -10 for v in rl) * step,
    "caution": "One saved reflection channel only; not an independent CST rerun or total absorptance validation.",
}
assert math.isclose(bandwidth, 13.2, abs_tol=1e-8)
assert math.isclose(min(rl), -23.485400435875423, abs_tol=1e-8)
print(json.dumps({"simulation_archive": result}, ensure_ascii=False, indent=2))
