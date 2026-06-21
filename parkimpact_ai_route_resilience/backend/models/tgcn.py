class TGCNModel:
    """
    Mock implementation of a Temporal Graph Convolutional Network.
    In production, this would load weights from PyTorch Geometric.
    """
    def __init__(self):
        self.accuracy = 0.85

    def predict(self, hour, day, weather):
        # Simulate predictions
        zones = ["KR Market", "Silk Board", "Indiranagar", "MG Road", "Whitefield"]
        import random
        counts = [random.randint(50, 150) for _ in range(5)]
        # Sort descending
        counts.sort(reverse=True)
        
        return [{"zone": z, "violations": c} for z, c in zip(zones, counts)]
