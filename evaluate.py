import random
import yaml
from generator.generate import generate, make_noise
from degrader.degrade import degrade
from engine.chain import build_chains
from engine.baseline import Baseline
from engine.attribution import attribute

base_cfg = yaml.safe_load(open("configs/scenario.yaml"))
rows = []   # (scenario type, predicted probability, was it really the attack?)

def key(e):
    return (e["time"], e["user"], e["dest"], e["action"])

TYPES = ["standard", "mimic_admin", "admin_account", "admin_ldap"]

for seed in range(400):
    rng = random.Random(seed)
    cfg = dict(base_cfg)
    cfg["seed"] = seed
    cfg["edr_sampling"] = rng.choice([1, 5, 20, 50])
    cfg["log_loss"] = rng.choice([0.0, 0.05, 0.2, 0.4])
    cfg["clock_skew_sec"] = rng.choice([10, 30, 120])
    cfg["concurrent_admin"] = rng.random() < 0.7
    cfg["historian_accessed"] = rng.random() < 0.7

    stype = TYPES[seed % len(TYPES)]
    cfg["mimic_admin"] = (stype == "mimic_admin")
    cfg["admin_account"] = (stype == "admin_account")
    cfg["admin_ldap"] = (stype == "admin_ldap")
    if stype in ("admin_account", "admin_ldap"):
        cfg["concurrent_admin"] = True

    # learn routine behaviour from 7 days of noise (no attack)
    baseline = Baseline()
    history = []
    for day in range(7):
        history += make_noise(cfg, random.Random(seed * 100 + day + 1000))
    baseline.fit(history)

    truth = generate(cfg)
    degraded = degrade(truth, cfg)
    # ground truth is kept here, outside the engine
    labels = {key(e): e["label"] for e in degraded}
    # the engine only sees events without the label
    evidence = [{k: v for k, v in e.items() if k != "label"} for e in degraded]

    for chain in build_chains(evidence):
        for a in chain:
            if a["dest"] == "HISTORIAN1":
                prob, _ = attribute(a, chain, baseline)
                rows.append((stype, prob, labels[key(a)] == "attack"))

def summarize(sel):
    n = len(sel)
    acc = sum((p > 0.5) == y for _, p, y in sel) / n
    brier = sum((p - (1 if y else 0)) ** 2 for _, p, y in sel) / n
    return n, acc, brier

print("=== Per scenario type ===")
print(f"{'type':14} {'count':>6} {'accuracy':>9} {'brier':>7}")
for t in TYPES:
    sel = [r for r in rows if r[0] == t]
    if sel:
        n, acc, brier = summarize(sel)
        print(f"{t:14} {n:6d} {acc:9.1%} {brier:7.3f}")
n, acc, brier = summarize(rows)
print(f"{'ALL':14} {n:6d} {acc:9.1%} {brier:7.3f}\n")

print("=== Reliability table (stated confidence vs real accuracy) ===")
print(f"{'stated range':14} {'count':>6} {'avg stated':>11} {'really attack':>14}")
bins = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
for lo, hi in bins:
    sel = [(p, y) for _, p, y in rows if lo <= p < hi]
    if not sel:
        continue
    avg_p = sum(p for p, _ in sel) / len(sel)
    real = sum(1 for _, y in sel if y) / len(sel)
    print(f"{lo:.1f} - {min(hi, 1.0):.1f}      {len(sel):6d} {avg_p:11.0%} {real:14.0%}")