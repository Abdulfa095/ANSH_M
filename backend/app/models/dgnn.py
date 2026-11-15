import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class DynamicGraphLearning(nn.Module):
    """
    Dynamic Graph Learning (DGL) Module.
    Learns the adjacency matrix A_t dynamically based on node states.
    Equation: A_t = Softmax(Q * K^T / sqrt(d))
    """
    def __init__(self, input_dim, hidden_dim, num_nodes, dropout=0.1):
        super(DynamicGraphLearning, self).__init__()
        self.num_nodes = num_nodes
        self.hidden_dim = hidden_dim
        
        # Node embeddings (static features)
        self.node_embeddings = nn.Parameter(torch.randn(num_nodes, hidden_dim))
        
        # Transformation layers for Query and Key
        self.linear_q = nn.Linear(input_dim + hidden_dim, hidden_dim)
        self.linear_k = nn.Linear(input_dim + hidden_dim, hidden_dim)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        """
        Args:
            x (torch.Tensor): Input features [Batch, Num_Nodes, Time, Input_Dim]
            or [Batch, Num_Nodes, Input_Dim] for a single step.
            
        Returns:
            adj (torch.Tensor): Learned Adjacency Matrix [Batch, Num_Nodes, Num_Nodes]
        """
        # x: [Batch, N, D]
        batch_size, num_nodes, _ = x.size()
        
        # Expand node embeddings to batch
        # node_emb: [1, N, H] -> [B, N, H]
        node_emb = self.node_embeddings.unsqueeze(0).expand(batch_size, -1, -1)
        
        # Concatenate input features with node embeddings
        # We assume x is the current state. If x has time dimension, we might take the last step
        # or process sequence. Here assuming x is [Batch, N, Input_Dim] (current step)
        combined = torch.cat([x, node_emb], dim=-1) # [B, N, I+H]
        
        q = self.linear_q(combined) # [B, N, H]
        k = self.linear_k(combined) # [B, N, H]
        
        # Compute Attention Scores
        # [B, N, H] @ [B, H, N] -> [B, N, N]
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.hidden_dim)
        
        # Apply Softmax to get probabilities (adjacency weights)
        adj = F.softmax(scores, dim=-1)
        adj = self.dropout(adj)
        
        return adj

class GraphConvolution(nn.Module):
    """
    Simple GCN layer that uses the dynamic adjacency matrix.
    H' = activation(A * H * W)
    """
    def __init__(self, in_features, out_features):
        super(GraphConvolution, self).__init__()
        self.linear = nn.Linear(in_features, out_features)
        
    def forward(self, x, adj):
        """
        Args:
            x: Node features [Batch, N, In_Features]
            adj: Adjacency matrix [Batch, N, N]
        """
        # Message Passing: A * X
        # [B, N, N] @ [B, N, In] -> [B, N, In]
        support = torch.matmul(adj, x)
        
        # Transform: X * W
        output = self.linear(support)
        
        return F.relu(output)

class DGNN(nn.Module):
    def __init__(self, num_nodes, input_dim, hidden_dim, output_dim):
        super(DGNN, self).__init__()
        self.dgl = DynamicGraphLearning(input_dim, hidden_dim, num_nodes)
        self.gcn1 = GraphConvolution(input_dim, hidden_dim)
        self.gcn2 = GraphConvolution(hidden_dim, output_dim)
        
    def forward(self, x):
        # x: [Batch, N, Input_Dim]
        adj = self.dgl(x)
        x = self.gcn1(x, adj)
        x = self.gcn2(x, adj)
        return x, adj

if __name__ == "__main__":
    # Test
    num_nodes = 5
    input_dim = 10
    hidden_dim = 16
    batch = 2
    
    model = DGNN(num_nodes, input_dim, hidden_dim, hidden_dim)
    x = torch.randn(batch, num_nodes, input_dim)
    
    out, adj = model(x)
    print("Output shape:", out.shape) # Should be [2, 5, 16]
    print("Adj shape:", adj.shape)   # Should be [2, 5, 5]
