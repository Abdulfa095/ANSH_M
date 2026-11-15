import torch
import torch.nn as nn
import torch.nn.functional as F

class GatedResidualNetwork(nn.Module):
    """
    Gated Residual Network (GRN) as used in TFT.
    """
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.1):
        super(GatedResidualNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        self.gate = nn.Linear(input_dim, output_dim)
        self.layernorm = nn.LayerNorm(output_dim)
        
    def forward(self, x):
        # x: [Batch, Input_Dim]
        residual = self.gate(x)
        x = self.fc1(x)
        x = F.elu(x)
        x = self.fc2(x)
        x = self.dropout(x)
        x = F.glu(torch.cat((x, x), dim=-1), dim=-1) # Simplified GLU logic or explicit Gating?
        # Actually TFT uses GLU(Linear(x))
        # Here assuming standard GLU usage: input split in half
        # But let's follow standard implementation for GRN:
        # a = ELU(Linear(x))
        # b = Linear(a)
        # c = GLU(b)
        # out = LayerNorm(residual + c)
        return self.layernorm(residual + x) 
        # Note: Above is simplified. Real GRN has more gates. 
        # For prototype, a ResNet block with Gating is sufficient.

class TFT(nn.Module):
    """
    Temporal Fusion Transformer (Simplified).
    """
    def __init__(self, input_dim, hidden_dim, output_dim, num_heads=4):
        super(TFT, self).__init__()
        self.hidden_dim = hidden_dim
        
        # Variable Selection (Simplified to projection)
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # LSTM Encoder
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        
        # Multi-Head Attention
        self.attention = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True)
        
        # Quantile Output
        # Predicting 3 quantiles: P10, P50, P90
        self.output_proj = nn.Linear(hidden_dim, 3) 
        
    def forward(self, x):
        """
        Args:
            x: [Batch, Seq_Len, Input_Dim]
        """
        # Project inputs
        x = self.input_proj(x)
        
        # LSTM Encoding
        # enc_out: [Batch, Seq_Len, Hidden]
        enc_out, _ = self.lstm(x)
        
        # Attention
        # query=enc_out, key=enc_out, value=enc_out
        attn_out, _ = self.attention(enc_out, enc_out, enc_out)
        
        # Residual + Norm
        x = enc_out + attn_out
        
        # Output Project to Quantiles
        out = self.output_proj(x) # [Batch, Seq_Len, 3]
        
        return out

if __name__ == "__main__":
    model = TFT(input_dim=10, hidden_dim=32, output_dim=1)
    x = torch.randn(2, 20, 10) # Batch=2, Seq=20, Feat=10
    out = model(x)
    print("Output shape:", out.shape) # [2, 20, 3]
