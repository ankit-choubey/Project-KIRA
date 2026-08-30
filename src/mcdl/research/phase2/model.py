import logging

try:
    import torch
    import torch.nn.functional as F
    from torch_geometric.nn import SAGEConv, to_hetero
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger(__name__)

if HAS_TORCH:
    class BaseGraphSAGE(torch.nn.Module):
        def __init__(self, hidden_channels: int = 64, out_channels: int = 32):
            super().__init__()
            # We use lazy linear for heterogeneous input size resolution
            self.conv1 = SAGEConv((-1, -1), hidden_channels)
            self.bn1 = torch.nn.BatchNorm1d(hidden_channels)
            
            self.conv2 = SAGEConv((-1, -1), out_channels)
            self.bn2 = torch.nn.BatchNorm1d(out_channels)
            
        def forward(self, x, edge_index):
            x = self.conv1(x, edge_index)
            # ReLU before BatchNorm or BatchNorm before ReLU?
            # Standard: Conv -> BN -> ReLU
            x = self.bn1(x)
            x = F.relu(x)
            
            x = self.conv2(x, edge_index)
            x = self.bn2(x)
            x = F.relu(x)
            
            return x

    class HeteroGraphSAGE(torch.nn.Module):
        def __init__(self, metadata, hidden_channels: int = 64, out_channels: int = 32):
            super().__init__()
            # to_hetero transforms the homogeneous GNN to a heterogeneous one
            self.gnn = to_hetero(BaseGraphSAGE(hidden_channels, out_channels), metadata, aggr='mean')
            self.lin = torch.nn.Linear(out_channels, 1)
            
        def forward(self, x_dict, edge_index_dict):
            out_dict = self.gnn(x_dict, edge_index_dict)
            
            # We only care about predicting fraud probability for transactions
            txn_embed = out_dict['transaction']
            logits = self.lin(txn_embed).squeeze(-1)
            
            # Return sigmoid probabilities
            return torch.sigmoid(logits)
            
        def get_transaction_embeddings(self, x_dict, edge_index_dict):
            """Returns the 32-dimensional SAGE embeddings for transactions (for G-03 Fusion)"""
            out_dict = self.gnn(x_dict, edge_index_dict)
            return out_dict['transaction']

else:
    # Dummy mock for static validation locally without torch
    class HeteroGraphSAGE:
        def __init__(self, metadata, hidden_channels: int = 64, out_channels: int = 32):
            pass
        def forward(self, x_dict, edge_index_dict):
            pass

def get_parameter_count(model) -> int:
    """Returns actual parameter count."""
    if not HAS_TORCH:
        return 0
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

