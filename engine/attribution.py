import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def attribute(access, chain, baseline):
    """
    Returns (probability this historian access belongs to the attack, reasons).
    The weights are hand-set starting values. They will be calibrated later.
    """
    score = -1.0   # prior: most historian access is routine
    reasons = []
    prior = [e for e in chain if e["time"] <= access["time"]]

    if any(e["action"] == "ldap_burst" for e in prior):
        score += 2.0
        reasons.append("directory enumeration earlier in the same chain")
    if any(e["action"] == "script_host_spawn" for e in prior):
        score += 2.5
        reasons.append("scripting host launched earlier in the same chain")

    if baseline.seen(access["user"], "JUMPHOST1"):
        score -= 1.5
        reasons.append("user routinely uses the jump host (baseline)")
    else:
        score += 1.5
        reasons.append("user never used the jump host in baseline")

    # per-access feature: which host did the most recent jump host login come from?
    feeders = [e for e in prior if e["dest"] == "JUMPHOST1" and e["action"] == "login"]
    if feeders:
        src = feeders[-1]["host"]
        if baseline.host_seen(access["user"], src):
            score -= 1.0
            reasons.append(f"preceding jump host login came from {src}, a host this user normally uses")
        else:
            score += 2.0
            reasons.append(f"preceding jump host login came from {src}, a host this user never used in baseline")

    return sigmoid(score), reasons