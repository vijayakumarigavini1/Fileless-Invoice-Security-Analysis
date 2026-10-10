RULES = {
    "script_host_spawn": ("Execution", "scripting host launched"),
    "ldap_burst":        ("Discovery", "directory enumeration"),
    "login":             ("Lateral Movement", "login to another host"),
    "connect":           ("Lateral Movement", "connection to plant system"),
}

def map_capabilities(chain):
    out = []
    for e in chain:
        if e["action"] in RULES:
            cap, why = RULES[e["action"]]
            out.append(dict(time=e["time"], capability=cap,
                            reason=why, user=e["user"], dest=e["dest"]))
    return out