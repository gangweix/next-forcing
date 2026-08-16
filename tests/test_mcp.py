# Copyright 2024-2025 The Robbyant Team Authors. All rights reserved.
import importlib.util
from pathlib import Path

import pytest
import torch


MCP_PATH = Path(__file__).parents[1] / 'wan_va' / 'mcp.py'
SPEC = importlib.util.spec_from_file_location('wan_va_mcp', MCP_PATH)
MCP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MCP)


def test_shift_latents_for_mcp_moves_targets_and_masks_tail():
    latents = torch.arange(5).reshape(1, 1, 5, 1, 1)

    shifted, valid_mask = MCP.shift_latents_for_mcp(latents, frame_shift=2)

    assert shifted.flatten().tolist() == [2, 3, 4, 4, 4]
    assert valid_mask.flatten().tolist() == [True, True, True, False, False]


def test_shift_latents_for_mcp_handles_shift_beyond_sequence():
    latents = torch.arange(5).reshape(1, 1, 5, 1, 1)

    shifted, valid_mask = MCP.shift_latents_for_mcp(latents, frame_shift=8)

    assert shifted.flatten().tolist() == [4, 4, 4, 4, 4]
    assert not valid_mask.any()


def test_validate_mcp_settings_accepts_default_architecture():
    MCP.validate_mcp_settings(
        num_mcp_depths=3,
        mcp_blocks_per_depth=3,
        mcp_hidden_collect_layers=[3, 11, 19, 29],
        mcp_loss_weights=[0.5, 0.2, 0.1],
        num_layers=30,
    )


@pytest.mark.parametrize(
    'kwargs, message',
    [
        ({'mcp_loss_weights': [0.5]}, 'mcp_loss_weights'),
        ({'mcp_loss_weights': [0.5, -0.2, 0.1]}, 'non-negative'),
        ({'mcp_blocks_per_depth': 31}, 'cannot exceed'),
        ({'mcp_hidden_collect_layers': [3, 11, 30]}, 'smaller than'),
    ],
)
def test_validate_mcp_settings_rejects_invalid_values(kwargs, message):
    settings = {
        'num_mcp_depths': 3,
        'mcp_blocks_per_depth': 3,
        'mcp_hidden_collect_layers': [3, 11, 19],
        'mcp_loss_weights': [0.5, 0.2, 0.1],
        'num_layers': 30,
    }
    settings.update(kwargs)

    with pytest.raises(ValueError, match=message):
        MCP.validate_mcp_settings(**settings)
