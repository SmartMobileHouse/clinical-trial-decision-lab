"""Export the evidence bundle (schema smh-research-data/1) for the Clinical Trial Decision Lab report.

Reads only saved result files and prediction files; computes nothing new except simple counts and unit conversions
(fractions -> percentage points). Contains aggregates only: no abstracts, no review text, no per-record rows.

Usage: .venv-classic/bin/python experiment/export_report_data.py <output.json>
"""
import json, sys, time, hashlib, statistics as st, platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "experiment"; TP = E / "screening/tp"; FIN = ROOT / "screening-check/trialpanorama/final"
J = lambda p: json.load(open(p))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
pts = lambda x: None if x is None else x * 100

res, sens = J(TP / "final-results.json"), J(TP / "final-sensitivity.json")
freeze, manifest = J(FIN / "freeze.json"), J(FIN / "sample-manifest.json")
selection = J(ROOT / "screening-check/trialpanorama/classic-final/selection.json")
for f, h in freeze["files"].items(): assert sha(ROOT / f) == h, f"changed since freeze: {f}"
N = res["sample"]["records"]

# ---------- locked run ----------
def preds(path, provider=None):
    out = []
    for l in open(TP / path):
        p = json.loads(l)
        if provider and p.get("provider") != provider: continue
        out.append(p)
    return out
SRC = {"decider": ("final-pass1-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": ("final-pass1-direct/predictions.jsonl", "nimble"),
       "gemini": ("final-pass1-or_gemini_decision_1/predictions.jsonl", None), "gpt": ("final-pass1-prob/llm_openai_prob.jsonl", None),
       "haiku": ("final-pass1-prob/llm_anthropic_prob.jsonl", None), "logistic": ("final-classic-logistic.jsonl", None), "xgboost": ("final-classic-xgboost.jsonl", None)}
PASS2 = {"decider": ("final-pass2-direct/predictions.jsonl", "pplx_decider_v13"), "nimble": ("final-pass2-direct/predictions.jsonl", "nimble"),
         "gemini": ("final-pass2-or_gemini_decision_1/predictions.jsonl", None)}
KIND = {"decider": "decision model", "nimble": "decision model", "gemini": "decision model", "gpt": "general model", "haiku": "general model",
        "logistic": "trained classifier", "xgboost": "trained classifier"}
models = {}
for k, (path, prov) in SRC.items():
    P = preds(path, prov); s = res["systems"][k]; assert len(P) == N
    prob = [(p.get("probabilities") or {}).get("included") if "probabilities" in p else p["p"] for p in P]
    reported = sorted({p["model_reported"] for p in P if p.get("model_reported")})
    requested = sorted({p["model_requested"] for p in P if p.get("model_requested")})
    hosted = k not in ("logistic", "xgboost")
    models[k] = {
        "label": s["label"], "kind": KIND[k], "status": "ok",
        "versions": reported or ([r + " (as requested; returned identifier not logged)" for r in requested] if hosted else []),
        "balanced_accuracy": s["balanced_accuracy"], "low": s["interval"][0], "high": s["interval"][1],
        "accuracy_included": s["accuracy_included"], "accuracy_excluded": s["accuracy_excluded"], "record_accuracy": s["record_accuracy"],
        "auc": s["auc"], "brier": s["brier_valid_only"], "invalid_or_missing": s["invalid_or_missing"],
        "include_rate": sum(x >= .5 for x in prob) / N,
        "confident_quarter_accuracy": res["confidence"][k][0], "unsure_quarter_accuracy": res["confidence"][k][1],
        "cost_usd_first_pass": s["cost_usd_first_pass"] if hosted else None,
        "cost_per_1k_usd": s["cost_usd_first_pass"] / N * 1000 if hosted else None,
    }
pass2_cost = {k: sum(p.get("cost_usd") or 0 for p in preds(*v)) for k, v in PASS2.items()}
first_cost = sum(m["cost_usd_first_pass"] or 0 for m in models.values())
started = min(json.loads(l)["at"] for l in open(TP / "final-pass1-direct/attempts.jsonl") if '"start"' in l)

def diff(key, t=None):
    t = t or res["secondary_differences"][key]; return {"points": pts(t[0]), "low": pts(t[1]), "high": pts(t[2])}
q1, q3, q5s = res["q1"], res["q3"], sens["q5"]
import re
_txt = open(TP / "final-sensitivity.txt").read()
refit = {k: float(re.search(rf"refitting {k} on the unchanged training set reproduces the frozen predictions to within ([0-9.e+-]+)", _txt).group(1)) for k in ("logistic", "xgboost")}
assert open(TP / "final_analysis.py").read().count("DRAW[:2000]") == 2   # the locked script's shortfall for questions 4 and 5
sd = sens["differences"]
import numpy, scipy, sklearn, xgboost
locked = {
    "run_id": "locked-run-20261125", "started_utc": started, "plan_frozen": freeze["frozen_at"],
    "dataset": {"name": "TrialPanorama study_screening, open-licence subset (locked sample)", "rows": N,
                "license_note": "TrialPanorama benchmark (Apache-2.0); membership labels from published review reference lists; abstracts under CC0, CC BY, CC BY-SA or CC BY-ND only.",
                "files_sha256": {Path(f).name: h for f, h in freeze["files"].items() if Path(f).name in ("sample.jsonl", "reviews.json", "questions.json", "final_analysis.py", "Locked run plan.md")},
                "external_processing_allowed": True, "licences": manifest["licences"]},
    "scored_cases": N, "families": res["sample"]["families"], "included": res["sample"]["included"], "excluded": N - res["sample"]["included"],
    "families_considered": manifest["families_considered_after_title_adjudication"], "families_not_qualifying": manifest["families_not_qualifying"],
    "min_per_label": 6, "max_per_label": 10, "chance": 0.5,
    "bootstrap": {"resamples": freeze["bootstrap_draws"], "seed": freeze["seed"], "method": "whole review families resampled, paired across systems, percentile interval"},
    "versions_note": "Versions of the environment that exported this evidence file; the versions used at run time were not recorded.",
    "versions": {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "scikit-learn": sklearn.__version__, "xgboost": xgboost.__version__},
    "models": models, "keyword_auc": res["keyword_auc"],
    "best_hosted_accuracy": max(m["balanced_accuracy"] for k, m in models.items() if k not in ("logistic", "xgboost")),
    "lowest_six_accuracy": sorted(m["balanced_accuracy"] for m in models.values())[1], "highest_accuracy": max(m["balanced_accuracy"] for m in models.values()),
    "q1": {"points": pts(q1["difference"]), "low": pts(q1["interval"][0]), "high": pts(q1["interval"][1]), "margin_points": pts(q1["margin"]),
           "margin_abs_points": abs(pts(q1["margin"])), "low_abs_points": abs(pts(q1["interval"][0])), "cleared_by_points": pts(q1["interval"][0] - q1["margin"]), "verdict": q1["verdict"]},
    "q2": {**res["q2"], "times_cheaper": 1 / res["q2"]["ratio"], "limit_ratio": 0.2},
    "q3": {"logistic": diff(0, [q3["logistic"]["difference"], *q3["logistic"]["interval"]]), "xgboost": diff(0, [q3["xgboost"]["difference"], *q3["xgboost"]["interval"]]), "met": q3["met"]},
    "q4": {k: {"same": sens["q4"][k]["same"], "of": sens["q4"][k]["of"], "changed": sens["q4"][k]["of"] - sens["q4"][k]["same"], "rate": sens["q4"][k]["same"] / sens["q4"][k]["of"],
               "low": sens["q4"][k]["family"][0], "high": sens["q4"][k]["family"][1], "identical_probability": res["q4"][k]["identical_probability"]} for k in sens["q4"]},
    "q4_benchmark": 0.98,
    "q5": {n.split()[-1]: {"correct": v["correct"], "decisions": v["decisions"], "wrong": v["decisions"] - v["correct"], "reliability": v["correct"] / v["decisions"],
                           "coverage": v["decisions"] / N, "low": v["family"][0], "high": v["family"][1], "families": res["q5"][n]["families"],
                           "locked_output_low": res["q5"][n]["interval"][0], "locked_output_high": res["q5"][n]["interval"][1]} for n, v in q5s.items()},
    "q5_coverage_total": sum(v["decisions"] for v in q5s.values()) / N,
    "q5_cutoffs": {"exclude_at_or_below": freeze["cutoffs"]["exclude_le"], "include_at_or_above": freeze["cutoffs"]["include_ge"]},
    "q5_decisions_total": sum(v["decisions"] for v in q5s.values()), "q5_wrong_total": sum(v["decisions"] - v["correct"] for v in q5s.values()),
    "q45_original_resamples": 2000, "refit_check": {"logistic_max_difference": refit["logistic"], "xgboost_max_difference": refit["xgboost"]},
    "margin_not_met_example_points": 4, "accuracy_spread_all_points": pts(max(m["balanced_accuracy"] for m in models.values()) - min(m["balanced_accuracy"] for m in models.values())),
    "accuracy_spread_top_six_points": pts(max(m["balanced_accuracy"] for m in models.values()) - sorted(m["balanced_accuracy"] for m in models.values())[1]),
    "abstract_min_characters": 200, "classic_prior_exposure_families": freeze["classic_baseline"]["prior_exposure_candidate_families_in_old_training"],
    "classic_frozen_at": freeze["classic_baseline"]["added_at"],
    "q6": {"observed_sd_points": pts(res["q6"]["observed_sd"]), "sampling_sd_points": pts(res["q6"]["sampling_noise_sd"]), "underlying_sd_points": pts(res["q6"]["estimated_underlying_sd"]),
           "largest_decision_model_gap_points": max(abs(pts(v[0])) for v in res["q6"]["gaps"].values()),
           "gaps": {k.replace("-", "_minus_"): {"points": pts(v[0]), "low": pts(v[1]), "high": pts(v[2])} for k, v in res["q6"]["gaps"].items()}},
    "differences": {"decider_minus_gpt": diff(0, [q1["difference"], *q1["interval"]]), "decider_minus_xgboost": diff(0, [q3["xgboost"]["difference"], *q3["xgboost"]["interval"]]),
                    "decider_minus_logistic": diff(0, [q3["logistic"]["difference"], *q3["logistic"]["interval"]]), "nimble_minus_gpt": diff("nimble-gpt"), "gemini_minus_gpt": diff("gemini-gpt"),
                    "gpt_minus_haiku": diff("gpt-haiku"), "gpt_minus_xgboost": diff("gpt-xgboost"), "decider_minus_haiku": diff("decider-haiku")},
    "agreement": {"unanimous_share": res["disagreement"]["unanimous_share"], "accuracy_unanimous": res["disagreement"]["accuracy_unanimous"], "accuracy_split_majority": res["disagreement"]["accuracy_split_majority"]},
    "brier_constant_half": 0.25, "systems_worse_than_constant": sum(1 for k, m in models.items() if k not in ("logistic", "xgboost") and m["brier"] > .25),
    "hosted_systems": 5,
    "spend": {"first_pass_usd": first_cost, "repeat_pass_usd": sum(pass2_cost.values()), "recorded_total_usd": first_cost + sum(pass2_cost.values()), "failed_calls_unknown_charge": 3, "cap_usd": 25},
    "classic_training": {**selection["training_counts"], "chosen": selection["chosen"]},
    "sensitivity": {
        "records_with_registration_number": 531, "clusters": sens["linkage"]["clusters"], "cross_family_trial_numbers": len(sens["linkage"]["cross_family_trial_numbers"]),
        "cross_family_records": 16, "cross_family_families": 9,
        "training_rows_removed": sens["linkage"]["training_rows_removed"], "trial_numbers_shared_with_training": len(sens["linkage"]["trial_numbers_shared_with_training"]),
        "trial_numbers_shared_with_pilots": len(sens["linkage"]["trial_numbers_shared_with_pilots"]), "pilot_linked_records": 11,
        "q1_linked": {"points": pts(sd["decider-gpt"]["cluster"][0]), "low": pts(sd["decider-gpt"]["cluster"][1]), "high": pts(sd["decider-gpt"]["cluster"][2])},
        "q1_without_pilot_linked": {"points": pts(sens["q1_without_pilot_linked_records"][0]), "low": pts(sens["q1_without_pilot_linked_records"][1]), "high": pts(sens["q1_without_pilot_linked_records"][2])},
        "xgboost_clean_accuracy": sens["classic"]["xgboost_clean"][0], "logistic_clean_accuracy": sens["classic"]["logistic_clean"][0],
        "decider_minus_xgboost_clean": {"points": pts(sd["decider-xgboost_clean"]["cluster"][0]), "low": pts(sd["decider-xgboost_clean"]["cluster"][1]), "high": pts(sd["decider-xgboost_clean"]["cluster"][2])},
        "decider_minus_logistic_clean": {"points": pts(sd["decider-logistic_clean"]["cluster"][0]), "low": pts(sd["decider-logistic_clean"]["cluster"][1]), "high": pts(sd["decider-logistic_clean"]["cluster"][2])},
    },
}
# the two counts typed above are checked against the sensitivity text output
txt = open(TP / "final-sensitivity.txt").read()
assert "registration number: 531 of 1210" in txt and "families involved: 9; records involved: 16" in txt and "sample records affected: 11)" in txt

# ---------- exploratory pilots ----------
pc, info, rep, pil = J(TP / "prompt-comparison.json"), J(TP / "info-test-scores.json"), J(TP / "repeat-scores.json"), J(TP / "tp-pilot-scores.json")
LLM = {"llm_openai", "llm_anthropic"}
dec = [k for k in pc if k not in LLM]
swing = {k: max(v[s]["accuracy"] for s in v) - min(v[s]["accuracy"] for s in v) for k, v in pc.items() if len(v) == 3}
rdec = {k: v for k, v in rep.items() if k not in LLM}
idec = [k for k in info if k not in LLM and info[k].get("title") and info[k].get("criteria")]
pilot_hard = {
    "run_id": "pilot-hard-cases-202611", "status": "exploratory",
    "dataset": {"name": "TrialPanorama study_screening, open-licence subset (development pilot)", "rows": 400, "reviews": 20, "external_processing_allowed": True},
    "systems": len(pc), "decision_models": len(dec), "prompt_styles": 3,
    "mean_accuracy": {s: st.mean(pc[k][s]["accuracy"] for k in dec) for s in ("detailed", "evidence", "minimal")},
    "median_swing_points": pts(st.median(swing.values())), "systems_within_3_points": sum(1 for v in swing.values() if v <= 0.03 + 1e-9), "systems_compared": len(swing),
    "largest_swing_points": pts(max(swing.values())),
    "decider_accuracy": pc["pplx_decider_v13"]["detailed"]["accuracy"], "best_accuracy": max(pc[k]["detailed"]["accuracy"] for k in dec),
    "lowest_accuracy": min(pc[k]["detailed"]["accuracy"] for k in dec), "best_accuracy_any_prompt": max(pc[k][s]["accuracy"] for k in dec for s in pc[k]),
    "repeat": {"decision_models": len(rdec), "identical_answers": sum(1 for v in rdec.values() if v["same_answer"] == 1.0),
               "identical_answers_all_400": sum(1 for v in rdec.values() if v["same_answer"] == 1.0 and v["n"] == 400),
               "identical_probabilities": sum(1 for v in rdec.values() if v.get("exact_probabilities")),
               "lowest_rate": min(v["same_answer"] for v in rdec.values()), "gpt_rate": rep["llm_openai"]["same_answer"], "haiku_rate": rep["llm_anthropic"]["same_answer"], "llm_subset": rep["llm_openai"]["n"]},
}
pilot_info = {
    "run_id": "pilot-criteria-202611", "status": "exploratory",
    "dataset": {"name": "TrialPanorama study_screening, 11 CC BY reviews (development pilot)", "rows": 392, "reviews": 11, "non_trial_reviews": 4, "external_processing_allowed": True},
    "decision_models": len(idec),
    "title_mean_accuracy": st.mean(info[k]["title"]["accuracy"] for k in idec), "criteria_mean_accuracy": st.mean(info[k]["criteria"]["accuracy"] for k in idec),
    "gain_points": pts(st.mean(info[k]["criteria"]["accuracy"] for k in idec) - st.mean(info[k]["title"]["accuracy"] for k in idec)),
    "improved": sum(1 for k in idec if info[k]["criteria"]["accuracy"] > info[k]["title"]["accuracy"]),
    "best_criteria_accuracy": max(info[k]["criteria"]["accuracy"] for k in idec),
    "title_lowest_accuracy": min(info[k]["title"]["accuracy"] for k in idec), "title_best_accuracy": max(info[k]["title"]["accuracy"] for k in idec),
    "gpt": {c: info["llm_openai"][c]["accuracy"] for c in ("title", "criteria")}, "haiku": {c: info["llm_anthropic"][c]["accuracy"] for c in ("title", "criteria")},
}
scr = J(E / "screening/pilot-scores.json")
SCR_LABEL = {"pplx_decider_v13": "Perplexity Decider 1.3", "jev": "TypeSafe Jev 1.14", "clef": "Cloudflare Clef", "openai_decisions": "OpenAI Decisions", "keyword_bm25": "Keyword ranking (BM25)", "keyword_tfidf": "Keyword ranking (TF-IDF)"}
pilot_screening = {
    "run_id": "pilot-screening-20261121", "status": "exploratory",
    "dataset": {"name": "SYNERGY, open-licence abstracts (development pilot)", "rows": 584, "reviews": 6, "test_reviews": 3, "external_processing_allowed": True},
    "pass_mark_rejected": 0.40, "target_kept": 0.95,
    "models": {k: {"label": SCR_LABEL[k], "versions": [], "relevant_kept": v["test_relevant_kept"], "irrelevant_rejected": v["test_irrelevant_rejected"], "ranking_auc": v["test_ranking_auc"]} for k, v in scr.items() if k in SCR_LABEL},
    "best_rejected": max(v["test_irrelevant_rejected"] for k, v in scr.items() if not k.startswith("keyword")),
    "lowest_rejected": min(v["test_irrelevant_rejected"] for k, v in scr.items() if not k.startswith("keyword")),
    "decision_models": sum(1 for k in scr if not k.startswith("keyword") and k in SCR_LABEL),
}
reg = J(E / "scores-human-checked-regenerated.json")
key = J(ROOT / "review/reference-labels-human-checked.json")
ta = lambda s, v: reg["treatments"][s][v]["a"]
real_total, fa_total = ta("pplx_decider_v13", "v2")["real_total"], ta("pplx_decider_v13", "v2")["false_alarms_total"]
pilot_registry = {
    "run_id": "pilot-registry-202611", "status": "exploratory",
    "dataset": {"name": "ClinicalTrials.gov records, free text against structured fields (development pilot)", "rows": reg["items"], "external_processing_allowed": True},
    "human_checked_items": sum(1 for r in key if r["human_checked"]), "not_human_checked_items": sum(1 for r in key if not r["human_checked"]),
    "rule_flags": reg["rule_flags"], "real_in_answer_key": reg["real"], "real_missed_by_rules": reg["real"] - real_total, "real": real_total, "false_alarms": fa_total, "configurations_tried": reg["configurations_tried"], "prompt_versions": 3,
    "decider_v2": {"real_kept": ta("pplx_decider_v13", "v2")["real_kept"], "false_alarms_removed": fa_total - ta("pplx_decider_v13", "v2")["false_alarms_kept"]},
    "openai_decisions": {"v1_real_kept": ta("openai_decisions", "v1")["real_kept"], "v2_real_kept": ta("openai_decisions", "v2")["real_kept"]},
}

# ---------- display values for charts (percent, one decimal; the same numbers as above, rounded) ----------
r1 = lambda x: round(x * 100, 1)
for m in locked["models"].values():
    m["chart"] = {"balanced_accuracy_pct": r1(m["balanced_accuracy"]), "low_pct": r1(m["low"]), "high_pct": r1(m["high"]),
                  "included": r1(m["accuracy_included"]), "excluded": r1(m["accuracy_excluded"])}
for v in locked["q5"].values(): v["chart"] = {"reliability_pct": r1(v["reliability"]), "low_pct": r1(v["low"]), "high_pct": r1(v["high"])}
pilot_info["chart"] = {"title": {"accuracy_pct": r1(pilot_info["title_mean_accuracy"])}, "criteria": {"accuracy_pct": r1(pilot_info["criteria_mean_accuracy"])}}
for v in pilot_screening["models"].values(): v["chart"] = {"rejected_pct": r1(v["irrelevant_rejected"]), "kept_pct": r1(v["relevant_kept"])}
pilot_hard["chart"] = {s: {"accuracy_pct": r1(v)} for s, v in pilot_hard["mean_accuracy"].items()}
bundle = {"schema": "smh-research-data/1", "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "generator": {"tool": "clinical-trial-decision-lab export_report_data.py", "version": "0.1.0"},
          "experiments": {"locked": locked, "pilot_hard": pilot_hard, "pilot_info": pilot_info, "pilot_screening": pilot_screening, "pilot_registry": pilot_registry}}
out = Path(sys.argv[1]); out.parent.mkdir(parents=True, exist_ok=True)
json.dump(bundle, open(out, "w"), indent=1)
print("written", out, out.stat().st_size, "bytes")
for k in ("pilot_hard", "pilot_info", "pilot_screening", "pilot_registry"):
    print(k, json.dumps({a: b for a, b in bundle["experiments"][k].items() if a not in ("dataset", "models")})[:900])
