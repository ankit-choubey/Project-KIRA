import logging
from typing import Any, Dict, List, Tuple
import polars as pl
import numpy as np

try:
    import torch
    # We delay torch_geometric import so static validation passes locally without it
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger(__name__)

def compute_causal_aggregates(df: pl.DataFrame, entity_col: str, t_col: str = "timestamp") -> pl.DataFrame:
    """
    Computes causal historical aggregates strictly UP TO t (exclusive).
    """
    # Sort strictly by timestamp and then txn_id to maintain causal order
    df = df.sort([t_col, "txn_id"])
    
    # We want features like: count_past, sum_amount_past
    # We must not include the current row in the aggregate for the current row.
    
    # We use a window function over the entity
    res = df.with_columns([
        (pl.col("txn_id").cum_count().over(entity_col) - 1).alias("historical_count"),
        (pl.col("amount").cum_sum().over(entity_col) - pl.col("amount")).alias("historical_amount_sum")
    ])
    
    # Ensure no negative counts (for the first transaction)
    res = res.with_columns(
        pl.when(pl.col("historical_count") < 0).then(0).otherwise(pl.col("historical_count")).alias("historical_count")
    )
    return res

def build_temporal_graph(
    transactions_df: pl.DataFrame,
    features_df: pl.DataFrame,
    train_end_t: int,
    val_end_t: int
):
    """
    Constructs a causal temporal PyG HeteroData graph.
    transactions_df: raw transactions including entity relationships and timestamp
    features_df: the exact 28 canonical features for each transaction
    """
    if not HAS_TORCH:
        raise ImportError("PyTorch required for graph construction.")
    from torch_geometric.data import HeteroData
    
    # Ensure order
    txns = transactions_df.sort(["timestamp", "txn_id"])
    feats = features_df.join(txns.select(["txn_id", "timestamp"]), on="txn_id").sort(["timestamp", "txn_id"])
    
    # 1. Map string IDs to integers
    txn_mapping = {tid: i for i, tid in enumerate(txns["txn_id"].to_list())}
    cust_mapping = {cid: i for i, cid in enumerate(txns["customer_id"].unique().to_list())}
    merch_mapping = {mid: i for i, mid in enumerate(txns["merchant_id"].unique().to_list())}
    dev_mapping = {did: i for i, did in enumerate(txns["device_id"].unique().to_list())}
    
    # Agents only exist for some transactions
    agents = txns.filter(pl.col("is_agent_initiated") == True)["agent_id"].drop_nulls().unique().to_list()
    agent_mapping = {aid: i for i, aid in enumerate(agents)}
    
    # 2. Extract strictly causal features for entity nodes
    # For a static graph representing the whole timeline, PyG needs static node features.
    # To maintain strict causality in a full static graph, each node's features must represent 
    # its state *before* it's involved in any future edge.
    # However, since nodes evolve, a transaction-centric approach is better:
    # Instead of static entity nodes, we can use the transaction node itself to hold the entity's 
    # causal state at time T, or we just use static structural edges and let the GNN aggregate.
    # For Phase 2, we assign standard structural causal aggregates to entity nodes based on their 
    # ENTIRE history up to the training cutoff to avoid leaking validation/test information,
    # OR we use temporal graph networks (TGN).
    # Since we are using GraphSAGE (static GNN), we must be very careful.
    # The requirement: "G(t) may contain only nodes, edges, aggregates, and features that were available strictly before the prediction timestamp."
    # Standard GraphSAGE on a static graph will pass messages from future transactions!
    # Therefore, we MUST mask out future edges during message passing.
    
    data = HeteroData()
    
    # For this implementation, we will construct edge tensors and timestamp tensors.
    # The actual temporal masking will be done during the forward pass or neighbor sampling.
    
    # Node features (transaction: 28 dims)
    # We assume features_df contains only the 28 numerical features.
    feature_cols = [c for c in feats.columns if c not in ("txn_id", "timestamp")]
    data['transaction'].x = torch.tensor(feats[feature_cols].to_numpy(), dtype=torch.float32)
    data['transaction'].timestamp = torch.tensor(txns["timestamp"].to_numpy(), dtype=torch.long)
    data['transaction'].y = torch.tensor(txns["is_fraud"].to_numpy(), dtype=torch.float32)
    data['transaction'].txn_id = txns["txn_id"].to_list()
    
    # Entity features (For now, simple aggregates up to train_end_t to strictly avoid future leak)
    # Customer features
    cust_aggs = compute_causal_aggregates(txns, "customer_id").filter(pl.col("timestamp") < train_end_t)
    cust_final = cust_aggs.group_by("customer_id").last()
    
    cust_feat_matrix = np.zeros((len(cust_mapping), 2), dtype=np.float32)
    for row in cust_final.iter_rows(named=True):
        idx = cust_mapping[row["customer_id"]]
        cust_feat_matrix[idx, 0] = row["historical_count"]
        cust_feat_matrix[idx, 1] = row["historical_amount_sum"]
    data['customer'].x = torch.tensor(cust_feat_matrix, dtype=torch.float32)
    
    # Merchant features
    merch_aggs = compute_causal_aggregates(txns, "merchant_id").filter(pl.col("timestamp") < train_end_t)
    merch_final = merch_aggs.group_by("merchant_id").last()
    merch_feat_matrix = np.zeros((len(merch_mapping), 2), dtype=np.float32)
    for row in merch_final.iter_rows(named=True):
        idx = merch_mapping[row["merchant_id"]]
        merch_feat_matrix[idx, 0] = row["historical_count"]
        merch_feat_matrix[idx, 1] = row["historical_amount_sum"]
    data['merchant'].x = torch.tensor(merch_feat_matrix, dtype=torch.float32)
    
    # Device features
    dev_aggs = compute_causal_aggregates(txns, "device_id").filter(pl.col("timestamp") < train_end_t)
    dev_final = dev_aggs.group_by("device_id").last()
    dev_feat_matrix = np.zeros((len(dev_mapping), 2), dtype=np.float32)
    for row in dev_final.iter_rows(named=True):
        idx = dev_mapping[row["device_id"]]
        dev_feat_matrix[idx, 0] = row["historical_count"]
        dev_feat_matrix[idx, 1] = row["historical_amount_sum"]
    data['device'].x = torch.tensor(dev_feat_matrix, dtype=torch.float32)
    
    # Agent features
    agent_aggs = compute_causal_aggregates(txns.filter(pl.col("is_agent_initiated")==True), "agent_id").filter(pl.col("timestamp") < train_end_t)
    agent_final = agent_aggs.group_by("agent_id").last()
    agent_feat_matrix = np.zeros((len(agent_mapping), 2), dtype=np.float32)
    for row in agent_final.iter_rows(named=True):
        idx = agent_mapping[row["agent_id"]]
        agent_feat_matrix[idx, 0] = row["historical_count"]
        agent_feat_matrix[idx, 1] = row["historical_amount_sum"]
    data['agent'].x = torch.tensor(agent_feat_matrix, dtype=torch.float32) if len(agent_mapping) > 0 else torch.empty((0, 2), dtype=torch.float32)

    # 3. Edges
    # customer -> transaction
    c_src, t_dst = [], []
    for c_id, t_id in zip(txns["customer_id"], txns["txn_id"]):
        c_src.append(cust_mapping[c_id])
        t_dst.append(txn_mapping[t_id])
    data['customer', 'initiates', 'transaction'].edge_index = torch.tensor([c_src, t_dst], dtype=torch.long)
    
    # transaction -> merchant
    t_src, m_dst = [], []
    for t_id, m_id in zip(txns["txn_id"], txns["merchant_id"]):
        t_src.append(txn_mapping[t_id])
        m_dst.append(merch_mapping[m_id])
    data['transaction', 'to', 'merchant'].edge_index = torch.tensor([t_src, m_dst], dtype=torch.long)
    
    # transaction -> device
    t_src_d, d_dst = [], []
    for t_id, d_id in zip(txns["txn_id"], txns["device_id"]):
        t_src_d.append(txn_mapping[t_id])
        d_dst.append(dev_mapping[d_id])
    data['transaction', 'from', 'device'].edge_index = torch.tensor([t_src_d, d_dst], dtype=torch.long)
    
    # agent -> transaction
    a_src, t_dst_a = [], []
    agent_txns = txns.filter(pl.col("is_agent_initiated") == True)
    for a_id, t_id in zip(agent_txns["agent_id"], agent_txns["txn_id"]):
        if a_id in agent_mapping:
            a_src.append(agent_mapping[a_id])
            t_dst_a.append(txn_mapping[t_id])
    if len(a_src) > 0:
        data['agent', 'facilitates', 'transaction'].edge_index = torch.tensor([a_src, t_dst_a], dtype=torch.long)
        
    # Create masks
    t_tensor = data['transaction'].timestamp
    data['transaction'].train_mask = t_tensor < train_end_t
    data['transaction'].val_mask = (t_tensor >= train_end_t) & (t_tensor < val_end_t)
    data['transaction'].test_mask = t_tensor >= val_end_t
    
    return data, {
        "transaction": 28,
        "customer": 2,
        "merchant": 2,
        "device": 2,
        "agent": 2
    }

