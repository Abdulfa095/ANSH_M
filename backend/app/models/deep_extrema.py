import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepExtrema(nn.Module):
    """
    DeepExtrema Network.
    Predicts GEV parameters (mu, sigma, xi) for Block Maxima.
    """
    def __init__(self, input_dim, hidden_dim):
        super(DeepExtrema, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        
        # Output heads for GEV parameters
        self.mu_head = nn.Linear(hidden_dim, 1)
        self.sigma_head = nn.Linear(hidden_dim, 1)
        self.xi_head = nn.Linear(hidden_dim, 1)
        
    def forward(self, x):
        # x: [Batch, Seq_Len, Input_Dim] -> We want to predict for the *next* window
        # For simplicity, we pool the sequence or take last state
        x = x[:, -1, :] # Take last time step
        
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        mu = self.mu_head(x)
        sigma = F.softplus(self.sigma_head(x)) # Sigma must be positive
        xi = self.xi_head(x)
        
        return mu, sigma, xi

def extreme_value_loss(y_true, mu, sigma, xi):
    """
    Negative Log Likelihood of the GEV distribution.
    With numerical stability guards to prevent NaN.
    """
    # Clamp sigma and xi for stability
    sigma = torch.clamp(sigma, min=1e-4)
    xi = torch.clamp(xi, min=-0.5, max=0.5)  # Restrict xi range
    
    # Avoid division by zero: if xi is too close to 0, use Gumbel approximation
    xi_safe = torch.where(torch.abs(xi) < 1e-6, torch.ones_like(xi) * 1e-6, xi)
    
    t = 1 + xi_safe * (y_true - mu) / sigma
    t = torch.clamp(t, min=1e-6)  # Must be positive for log/power
    
    term1 = torch.log(sigma)
    term2 = (1 + 1/xi_safe) * torch.log(t)
    term3 = t ** (-1/xi_safe)
    
    nll = term1 + term2 + term3
    
    # Clamp final loss to prevent NaN/Inf from propagating
    nll = torch.clamp(nll, min=-100, max=100)
    
    return torch.mean(nll)

if __name__ == "__main__":
    model = DeepExtrema(input_dim=10, hidden_dim=32)
    x = torch.randn(5, 20, 10)
    mu, sigma, xi = model(x)
    print(f"Mu: {mu.shape}, Sigma: {sigma.shape}, Xi: {xi.shape}")
