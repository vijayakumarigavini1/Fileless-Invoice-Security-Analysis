import random
import yaml
from generator.generate import generate, make_noise
from degrader.degrade import degrade
from engine.chain import build_chains
from engine.baseline import Baseline
from engine.attribution import attribute

base_cfg = yaml.safe_load(open("configs/scenario.yaml"))

def key(e):
    return (e["time"], e["user"], e["dest"], e["action"])

rows = []   # (log_loss, really attack?, clerk-pc login visible?, probability)
for seed in range(2, 800, 4):   # seed % 4 == 2 is the admin_account scenario
    rng = random.Random(seed)
    cfg = dict(base_cfg)
    cfg["seed"] = seed
    cfg["edr_sampling"] = rng.choice([1, 5, 20, 50])
    cfg["log_loss"] = rng.choice([0.0, 0.05, 0.2, 0.4])
    cfg["clock_skew_sec"] = rng.choice([10, 30, 120])
    cfg["historian_accessed"] = rng.random() < 0.7
    cfg["admin_account"] = True
    cfg["concurrent_admin"] = True

    baseline = Baseline()
    history = []
    for day in range(7):
        history += make_noise(cfg, random.Random(seed * 100 + day + 1000))
    baseline.fit(history)

    degraded = degrade(generate(cfg), cfg)
    labels = {key(e): e["label"] for e in degraded}
    evidence = [{k: v for k, v in e.items() if k != "label"} for e in degraded]

    for chain in build_chains(evidence):
        for a in chain:
            if a["dest"] == "HISTORIAN1":
                prob, _ = attribute(a, chain, baseline)
                prior = [e for e in chain if e["time"] <= a["time"]]
                visible = any(e["host"] == "CLERK-PC" and e["dest"] == "JUMPHOST1"
                              for e in prior)
                rows.append((cfg["log_loss"], labels[key(a)] == "attack", visible, prob))

def report(title, groups):
    print(title)
    print(f"{'group':34} {'count':>6} {'accuracy':>9} {'avg prob':>9}")
    for name, sel in groups:
        if sel:
            acc = sum((r[3] > 0.5) == r[1] for r in sel) / len(sel)
            avg = sum(r[3] for r in sel) / len(sel)
            print(f"{name:34} {len(sel):6d} {acc:9.1%} {avg:9.0%}")
    print()

report("=== By log loss ===",
       [(f"log_loss = {ll}", [r for r in rows if r[0] == ll])
        for ll in [0.0, 0.05, 0.2, 0.4]])

report("=== By truth and visibility of the CLERK-PC login ===",
       [("attack, CLERK-PC login visible", [r for r in rows if r[1] and r[2]]),
        ("attack, CLERK-PC login lost", [r for r in rows if r[1] and not r[2]]),
        ("routine admin, CLERK-PC login visible", [r for r in rows if not r[1] and r[2]]),
        ("routine admin, CLERK-PC login absent", [r for r in rows if not r[1] and not r[2]])])