class CollapseSimulator:
    def __init__(self):
        pass

    def simulate(self, blocked_edges):
        """
        Calculates urban collapse metrics based on the list of blocked edges.
        In production, this would use NetworkX to remove edges and recalculate shortest paths.
        """
        if not blocked_edges:
            return {
                "disconnected_nodes_pct": 0,
                "travel_time_increase": 0,
                "emergency_reachability": 100,
                "economic_loss": 0,
                "severity": 0
            }
            
        severity = min(len(blocked_edges) * 2.0, 10.0)
        
        return {
            "disconnected_nodes_pct": round(severity * 1.2, 1),
            "travel_time_increase": int(severity * 4.5),
            "emergency_reachability": round(100 - (severity * 3.3), 1),
            "economic_loss": int(severity * 4.5 * 10 * 5000), # min * 10 INR * 5000 cars
            "severity": round(severity, 1)
        }
