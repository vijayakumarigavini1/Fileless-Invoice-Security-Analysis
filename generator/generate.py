import random

def make_noise(cfg, rng):
    ev = []
    for i in range(cfg["users"]):
        for _ in range(rng.randint(5, 15)):
            ev.append(dict(
                time=rng.randint(8 * 3600, 18 * 3600),
                source=rng.choice(["auth", "dns", "proxy"]),
                user=f"user{i}", host=f"PC{i}",
                dest=rng.choice(["FILESRV1", "FILESRV2", "DC1"]),
                action="access", label="routine"))
    for a in range(cfg["admins"]):
        for _ in range(rng.randint(3, 8)):
            ev.append(dict(
                time=rng.randint(0, 86400), source="auth",
                user=f"admin{a}", host="ADMINPC",
                dest=rng.choice(["JUMPHOST1", "DC1", "FILESRV1"]),
                action="login", label="routine"))
    return ev

def make_admin_historian(cfg, rng):
    if not cfg["concurrent_admin"]:
        return []
    t = cfg["attack_start"] + rng.randint(-600, 900)
    ev = []
    if cfg.get("admin_ldap", False):
        # misleading: a real admin also queries the directory before the historian
        ev.append(dict(time=t - 120, source="auth", user="admin1", host="ADMINPC",
                       dest="DC1", action="ldap_burst", label="routine_historian"))
    ev.append(dict(time=t, source="auth", user="admin1", host="ADMINPC",
                   dest="JUMPHOST1", action="login", label="routine_historian"))
    ev.append(dict(time=t + 60, source="flow", user="admin1", host="JUMPHOST1",
                   dest="HISTORIAN1", action="connect", label="routine_historian"))
    return ev

def make_attack(cfg):
    t0 = cfg["attack_start"]
    user = "admin1" if cfg.get("admin_account", False) else "clerk01"
    scan_action = "access" if cfg.get("mimic_admin", False) else "ldap_burst"
    steps = [
        (0,   "edr",  "script_host_spawn", "CLERK-PC", "CLERK-PC"),
        (480, "auth", scan_action,         "CLERK-PC", "DC1"),
        (600, "auth", "access",            "CLERK-PC", "FILESRV1"),
        (780, "auth", "login",             "CLERK-PC", "JUMPHOST1"),
    ]
    if cfg["historian_accessed"]:
        steps.append((1080, "flow", "connect", "JUMPHOST1", "HISTORIAN1"))
    return [dict(time=t0 + dt, source=s, user=user, host=h, dest=d,
                 action=a, label="attack") for dt, s, a, h, d in steps]

def generate(cfg):
    rng = random.Random(cfg["seed"])
    events = make_noise(cfg, rng) + make_admin_historian(cfg, rng) + make_attack(cfg)
    events.sort(key=lambda e: e["time"])
    return events