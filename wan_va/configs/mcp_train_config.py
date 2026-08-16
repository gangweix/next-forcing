# Copyright 2024-2025 The Robbyant Team Authors. All rights reserved.
from easydict import EasyDict


mcp_train_cfg = EasyDict()
mcp_train_cfg.enable_mcp = True
mcp_train_cfg.num_mcp_depths = 3
mcp_train_cfg.mcp_blocks_per_depth = 3
# Zero-based indices for Transformer layers 4, 12, 20, and 30 in the paper.
mcp_train_cfg.mcp_hidden_collect_layers = [3, 11, 19, 29]
mcp_train_cfg.mcp_snr_shift = 10.0
mcp_train_cfg.mcp_loss_weights = [0.5, 0.2, 0.1]
mcp_train_cfg.mcp_init_from_backbone = True
