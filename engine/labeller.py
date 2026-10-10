OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
PLAUSIBLE = "PLAUSIBLE HYPOTHESIS"
UNRECOVERABLE = "UNRECOVERABLE"


def label_claim(direct, support, prob):
    """
    direct  : True if a log line directly shows the claim
    support : number of independent pieces of evidence behind the claim
    prob    : probability from the attribution model (0 to 1)
    Returns a label, or None when the claim is too weak to be stated at all.
    """
    if direct:
        return OBSERVED
    if support >= 2 and prob >= 0.8:
        return INFERRED
    if support >= 1 and prob >= 0.5:
        return PLAUSIBLE
    return None   # unsupported: must NOT be presented as having occurred


# Things no log in this environment could ever tell us
ALWAYS_UNRECOVERABLE = [
    "The attacker's actual code or payload (no sample, no memory image)",
    "Contents of any file read on the historian (no file-level auditing)",
    "Secrets held only in memory (passwords, tokens, keys)",
    "How the invoice was opened and what it contained (no email or document logs)",
    "Whether data left the network (only proxy volume could hint at this)",
]