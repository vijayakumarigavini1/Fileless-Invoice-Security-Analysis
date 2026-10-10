def answer_regulatory(historian_prob):
    if historian_prob > 0.8:
        ans = "Yes"
    elif historian_prob > 0.5:
        ans = "Partially"
    else:
        ans = "Cannot determine"
    return [
        ("Did the attacker reach the historian?", ans,
         f"estimated probability {historian_prob:.0%}"),
        ("What data was read on the historian?", "No",
         "no file-level logging"),
        ("Was data exfiltrated?", "Depends",
         "only proxy volume gives a hint"),
        ("What was the attacker's actual code?", "No",
         "no sample and no memory image"),
    ]