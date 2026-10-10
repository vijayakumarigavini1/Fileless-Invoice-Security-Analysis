def build_chains(events, window=1800):
    by_user = {}
    for e in sorted(events, key=lambda x: x["time"]):
        by_user.setdefault(e["user"], []).append(e)
    chains = []
    for user, evs in by_user.items():
        cur = [evs[0]]
        for e in evs[1:]:
            if e["time"] - cur[-1]["time"] <= window:
                cur.append(e)
            else:
                chains.append(cur)
                cur = [e]
        chains.append(cur)
    return [c for c in chains if len(c) >= 2]