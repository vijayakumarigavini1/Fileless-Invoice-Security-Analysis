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

def run(max_cases=4):
    shown = 0
    for seed in range(2, 800, 4):   # admin_account scenarios
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
                if a["dest"] != "HISTORIAN1":
                    continue
                prob, _ = attribute(a, chain, baseline)
                truth_is_attack = labels[key(a)] == "attack"
                # show only routine admin accesses that the system wrongly flagged
                if (not truth_is_attack) and prob > 0.5:
                    print(f"seed {seed}, log_loss {cfg['log_loss']}, skew {cfg['clock_skew_sec']}")
                    for e in chain:
                        mark = "   <== wrongly flagged" if e is a else ""
                        print(f"  {e['time']}  {e['host']:10} -> {e['dest']:10} "
                              f"{e['action']:18} true={labels[key(e)]}{mark}")
                    print(f"  system said P(attack) = {prob:.0%}\n")
                    shown += 1
                    if shown >= max_cases:
                        return

run()