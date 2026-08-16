import json
from types import SimpleNamespace

from wan_va.dataset.lerobot_latent_dataset import (
    LatentLeRobotDataset,
    dataset_indexes_ready,
)


class FakeMetadata:
    episodes = {
        0: {
            'episode_index': 0,
            'tasks': ['pick up the block'],
            'action_config': [
                {
                    'start_frame': 0,
                    'end_frame': 12,
                    'action_text': 'pick up the block',
                }
            ],
        }
    }

    @staticmethod
    def get_episode_chunk(_episode_index):
        return 0


def make_dataset(tmp_path):
    dataset = LatentLeRobotDataset.__new__(LatentLeRobotDataset)
    dataset.root = tmp_path
    dataset.latent_path = tmp_path / 'latents'
    dataset.used_video_keys = ['cam_high', 'cam_wrist']
    dataset.meta = FakeMetadata()
    dataset.config = SimpleNamespace(
        enable_dataset_index_cache=True,
        rebuild_dataset_index_cache=False,
    )
    meta_path = tmp_path / 'meta'
    meta_path.mkdir(exist_ok=True)
    (meta_path / 'info.json').write_text('{}\n', encoding='utf-8')
    episodes_path = meta_path / 'episodes.jsonl'
    if not episodes_path.exists():
        episodes_path.write_text(
            json.dumps(next(iter(FakeMetadata.episodes.values()))) + '\n',
            encoding='utf-8',
        )
    for camera in dataset.used_video_keys:
        latent_dir = dataset.latent_path / 'chunk-000' / camera
        latent_dir.mkdir(parents=True, exist_ok=True)
        (latent_dir / 'episode_000000_0_12.pth').touch()
    return dataset


def test_parse_meta_reuses_validated_index(tmp_path):
    first_dataset = make_dataset(tmp_path)
    assert first_dataset.parse_meta() is False
    assert len(first_dataset.new_metas) == 1

    second_dataset = make_dataset(tmp_path)

    def fail_if_rescanned(*_args):
        raise AssertionError('latent paths were scanned despite a valid cache')

    second_dataset._check_meta = fail_if_rescanned
    assert second_dataset.parse_meta() is True
    assert second_dataset.new_metas == first_dataset.new_metas


def test_parse_meta_rebuilds_when_episode_metadata_changes(tmp_path):
    first_dataset = make_dataset(tmp_path)
    assert first_dataset.parse_meta() is False

    episodes_path = tmp_path / 'meta' / 'episodes.jsonl'
    episodes_path.write_text(
        episodes_path.read_text(encoding='utf-8') + '\n',
        encoding='utf-8',
    )
    second_dataset = make_dataset(tmp_path)
    calls = 0

    def count_scan(*_args):
        nonlocal calls
        calls += 1
        return True

    second_dataset._check_meta = count_scan
    assert second_dataset.parse_meta() is False
    assert calls == 1


def test_dataset_indexes_ready_requires_available_arrow_cache(tmp_path):
    dataset = make_dataset(tmp_path)
    assert dataset.parse_meta() is False
    config = SimpleNamespace(
        dataset_path=str(tmp_path),
        obs_cam_keys=dataset.used_video_keys,
        enable_dataset_index_cache=True,
        rebuild_dataset_index_cache=False,
    )
    assert dataset_indexes_ready(config) is False

    fingerprint = dataset._dataset_index_fingerprint()
    cache_path = dataset._dataset_index_cache_path(fingerprint)
    payload = json.loads(cache_path.read_text(encoding='utf-8'))
    arrow_path = tmp_path / 'cached.arrow'
    arrow_path.touch()
    payload['hf_cache_files'] = [str(arrow_path)]
    cache_path.write_text(json.dumps(payload), encoding='utf-8')

    assert dataset_indexes_ready(config) is True
