import random

def degrade(events, cfg):
    rng = random.Random(cfg["seed"] + 1)
    out = []
    for e in events:
        # EDR: 20 లో 1 మాత్రమే మిగులుతుంది
        if e["source"] == "edr" and rng.randint(1, cfg["edr_sampling"]) != 1:
            continue
        # యాదృచ్ఛికంగా logs మాయం
        if rng.random() < cfg["log_loss"]:
            continue
        e = dict(e)
        # clock skew
        e["time"] += rng.randint(-cfg["clock_skew_sec"], cfg["clock_skew_sec"])
        out.append(e)
    return out