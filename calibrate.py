import random
import yaml
from generator.generate import generate, make_noise
from degrader.degrade import degrade
from engine.chain import build_chains
from engine.baseline import Baseline
from engine.attribution import attribute

base_cfg = yaml.safe_load(open("configs/scenario.yaml"))
TYPES = ["standard", "mimic_admin", "admin_account", "admin_ldap"]

def key(e):
    return (e["time"], e["user"], e["dest"], e["action"])

def collect(seeds):
    rows = []   # (scenario type, predicted probability, really attack?)
    for seed in seeds:
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
                    rows.append((stype, prob, labels[key(a)] == "attack"))
    return rows

class Calibrator:
    """Histogram binning: map a raw probability to the real attack rate seen in training."""
    def __init__(self, n_bins=10):
        self.n_bins = n_bins

    def _bin(self, p):
        return min(int(p * self.n_bins), self.n_bins - 1)

    def fit(self, rows):
        stats = {}
        for _, p, y in rows:
            b = self._bin(p)
            hit, tot = stats.get(b, (0, 0))
            stats[b] = (hit + (1 if y else 0), tot + 1)
        # +1 / +2 smoothing so a bin is never exactly 0% or 100%
        self.map = {b: (h + 1) / (t + 2) for b, (h, t) in stats.items()}

    def predict(self, p):
        return self.map.get(self._bin(p), p)

def brier(pairs):
    return sum((p - (1 if y else 0)) ** 2 for p, y in pairs) / len(pairs)

def ece(pairs, n_bins=10):
    total = len(pairs)
    err = 0.0
    for b in range(n_bins):
        sel = [(p, y) for p, y in pairs if min(int(p * n_bins), n_bins - 1) == b]
        if sel:
            avg_p = sum(p for p, _ in sel) / len(sel)
            real = sum(1 for _, y in sel if y) / len(sel)
            err += len(sel) / total * abs(avg_p - real)
    return err

train = collect(range(0, 200))
test = collect(range(200, 400))

cal = Calibrator()
cal.fit(train)

raw = [(p, y) for _, p, y in test]
fixed = [(cal.predict(p), y) for _, p, y in test]

print(f"Train accesses: {len(train)}   Test accesses: {len(test)}\n")
print(f"{'':22} {'Brier':>8} {'ECE':>8}")
print(f"{'Before calibration':22} {brier(raw):8.3f} {ece(raw):8.3f}")
print(f"{'After calibration':22} {brier(fixed):8.3f} {ece(fixed):8.3f}\n")

print("=== Per scenario type, on test data only ===")
print(f"{'type':14} {'count':>6} {'brier before':>13} {'brier after':>12}")
for t in TYPES:
    sel = [(p, y) for s, p, y in test if s == t]
    if sel:
        b1 = brier(sel)
        b2 = brier([(cal.predict(p), y) for p, y in sel])
        print(f"{t:14} {len(sel):6d} {b1:13.3f} {b2:12.3f}")

print("\n=== Reliability table AFTER calibration (test data) ===")
print(f"{'stated range':14} {'count':>6} {'avg stated':>11} {'really attack':>14}")
for lo in [0.0, 0.2, 0.4, 0.6, 0.8]:
    hi = lo + 0.2
    sel = [(p, y) for p, y in fixed if lo <= p < hi + (0.01 if hi > 0.99 else 0)]
    if sel:
        avg_p = sum(p for p, _ in sel) / len(sel)
        real = sum(1 for _, y in sel if y) / len(sel)
        print(f"{lo:.1f} - {min(hi, 1.0):.1f}      {len(sel):6d} {avg_p:11.0%} {real:14.0%}")