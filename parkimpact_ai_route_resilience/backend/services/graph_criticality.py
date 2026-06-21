import random
import pandas as pd

class GraphCriticality:
    """
    Mock implementation of Graph-Theoretic Criticality for the Hackathon.
    In production, this would use NetworkX / OSMnx to build the true Bangalore road network.
    """
    def __init__(self):
        self.nodes_count = 125
        self.edges_count = 200
        
    def get_graph_data(self):
        # Generate mock nodes
        nodes = []
        lats = [12.9716 + random.uniform(-0.05, 0.05) for _ in range(self.nodes_count)]
        lons = [77.5946 + random.uniform(-0.05, 0.05) for _ in range(self.nodes_count)]
        for i in range(self.nodes_count):
            nodes.append({"id": f"N{i}", "name": f"Junction {i}", "lat": lats[i], "lon": lons[i]})
            
        # Generate mock edges
        edges = []
        for i in range(self.edges_count):
            n1 = random.randint(0, self.nodes_count - 1)
            n2 = random.randint(0, self.nodes_count - 1)
            b_score = random.uniform(0.1, 0.9)
            edges.append({
                "id": f"E{i}", 
                "start_node": f"N{n1}", 
                "end_node": f"N{n2}",
                "start_lat": lats[n1], "start_lon": lons[n1],
                "end_lat": lats[n2], "end_lon": lons[n2],
                "betweenness": b_score,
                "connectivity_loss": b_score * 0.8,
                "resilience": random.uniform(2, 8),
                "score": round((0.4 * b_score) + (0.3 * (b_score * 0.8)) + (0.2 * 5) + 0.1, 2)
            })
            
        return pd.DataFrame(nodes), pd.DataFrame(edges)

    def get_critical_edges(self, edges_df, top_n=10):
        # Return IDs of top N critical edges
        return edges_df.nlargest(top_n, 'score')['id'].tolist()
