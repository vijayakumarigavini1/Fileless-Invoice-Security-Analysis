from collections import Counter

class Baseline:
    """Learns which (user, destination) and (user, host) pairs are routine."""

    def fit(self, events):
        self.pairs = Counter((e["user"], e["dest"]) for e in events)
        self.hosts = Counter((e["user"], e["host"]) for e in events)

    def seen(self, user, dest):
        return self.pairs.get((user, dest), 0) > 0

    def host_seen(self, user, host):
        return self.hosts.get((user, host), 0) > 0