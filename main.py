import yaml
import random
from generator.generate import generate, make_noise
from degrader.degrade import degrade
from engine.chain import build_chains
from engine.capability import map_capabilities
from engine.baseline import Baseline
from engine.attribution import attribute
from engine.labeller import label_claim, ALWAYS_UNRECOVERABLE
from engine.regulatory import answer_regulatory

cfg = yaml.safe_load(open("configs/scenario.yaml"))

# learn routine behaviour from 7 days of noise (no attack)
baseline = Baseline()
history = []
for day in range(7):
    history += make_noise(cfg, random.Random(cfg["seed"] * 100 + day + 1000))
baseline.fit(history)

truth = generate(cfg)
# remove the ground-truth label so the detective cannot see it
evidence = [{k: v for k, v in e.items() if k != "label"}
            for e in degrade(truth, cfg)]
print(f"Events: {len(truth)} -> {len(evidence)} (after evidence degradation)\n")

claims = []          # (label, text, confidence text)
extra_unrecoverable = []
best_prob = 0.0
attack_chain_found = False

for chain in build_chains(evidence):
    accesses = [e for e in chain if e["dest"] == "HISTORIAN1"]
    if not accesses:
        continue
    for a in accesses:
        prob, reasons = attribute(a, chain, baseline)
        best_prob = max(best_prob, prob)
        prior = [e for e in chain if e["time"] <= a["time"]]
        support = len([c for c in map_capabilities(prior)
                       if c["capability"] in ("Discovery", "Execution", "Lateral Movement")])
        label = label_claim(direct=False, support=support, prob=prob)

        if label is None:
            claims.append(("NOT CLAIMED",
                           f"Historian access at {a['time']} by {a['user']} "
                           f"is NOT attributed to this execution",
                           f"P(attack) = {prob:.0%}"))
            continue

        attack_chain_found = True
        # the log lines themselves are directly observed
        for c in map_capabilities(prior):
            claims.append(("OBSERVED",
                           f"Log shows {c['capability']} ({c['reason']}) "
                           f"by {c['user']} -> {c['dest']} at {c['time']}",
                           "log entry present"))
        claims.append((label,
                       f"Historian access at {a['time']} by {a['user']} "
                       f"was part of this execution",
                       f"P(attack) = {prob:.0%}"))
        print(f"Why for access at {a['time']}:")
        for r in reasons:
            print(f"   - {r}")
        print()

        if not any(e["action"] == "script_host_spawn" for e in chain):
            extra_unrecoverable.append(
                "Initial scripting-host launch is not in the surviving evidence "
                f"(EDR keeps 1 in {cfg['edr_sampling']} events)")

print("=== Claims ===")
for label, text, conf in claims:
    print(f"[{label:20}] {text}  ({conf})")

print("\n=== Unrecoverable ===")
for u in ALWAYS_UNRECOVERABLE + sorted(set(extra_unrecoverable)):
    print(f"[UNRECOVERABLE] {u}")

print("\n=== Regulator questions ===")
for q, a, why in answer_regulatory(best_prob):
    print(f"{q} -> {a}  ({why})")