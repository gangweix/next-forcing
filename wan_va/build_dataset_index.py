"""Build reusable latent sample indexes without loading the training model."""

import argparse

from .configs import VA_CONFIGS
from .dataset import MultiLatentLeRobotDataset


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-name', default='robotwin_train')
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Validate all latent paths again and replace the matching caches.',
    )
    parser.add_argument('--init-worker', type=int)
    return parser.parse_args()


def main():
    args = parse_args()
    config = VA_CONFIGS[args.config_name]
    config.rank = 0
    config.world_size = 1
    config.rebuild_dataset_index_cache = args.rebuild
    if args.init_worker is not None:
        config.init_worker = args.init_worker

    dataset = MultiLatentLeRobotDataset(config=config)
    print(
        f'Dataset index ready: {len(dataset)} samples from '
        f'{len(dataset._datasets)} datasets '
        f'({dataset.index_cache_hits} cache hits, '
        f'{dataset.hf_cache_hits} direct Arrow loads, '
        f'{dataset.index_cache_misses} rebuilt)'
    )


if __name__ == '__main__':
    main()
