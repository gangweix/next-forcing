# Copyright 2024-2025 The Robbyant Team Authors. All rights reserved.
from easydict import EasyDict
from .mcp_train_config import mcp_train_cfg
from .va_robotwin_cfg import va_robotwin_cfg
import os

va_robotwin_train_cfg = EasyDict(__name__='Config: VA robotwin train')
va_robotwin_train_cfg.update(va_robotwin_cfg)
va_robotwin_train_cfg.update(mcp_train_cfg)

va_robotwin_train_cfg.wan22_pretrained_model_name_or_path = os.environ.get(
    'NEXT_FORCING_PRETRAINED_MODEL_PATH',
    '/path/to/pretrained/model',
)
va_robotwin_train_cfg.dataset_path = os.environ.get(
    'NEXT_FORCING_DATASET_PATH',
    '/path/to/your/dataset',
)
va_robotwin_train_cfg.empty_emb_path = os.path.join(
    va_robotwin_train_cfg.dataset_path, 'empty_emb.pt')
va_robotwin_train_cfg.save_root = os.environ.get(
    'NEXT_FORCING_SAVE_ROOT',
    '/path/to/your/output',
)
va_robotwin_train_cfg.enable_wandb = False
va_robotwin_train_cfg.init_worker = 1
va_robotwin_train_cfg.load_worker = 16
va_robotwin_train_cfg.save_interval = 1000
va_robotwin_train_cfg.gc_interval = 50
va_robotwin_train_cfg.cfg_prob = 0.1

# Training parameters
va_robotwin_train_cfg.learning_rate = 2e-5
va_robotwin_train_cfg.beta1 = 0.9
va_robotwin_train_cfg.beta2 = 0.95
va_robotwin_train_cfg.weight_decay = 0.1
va_robotwin_train_cfg.warmup_steps = 100
va_robotwin_train_cfg.batch_size = 1 
va_robotwin_train_cfg.gradient_accumulation_steps = 1
va_robotwin_train_cfg.num_steps = 50000 
