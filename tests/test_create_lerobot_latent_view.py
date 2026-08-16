import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).parents[1] / "script" / "create_lerobot_latent_view.py"
)
SPEC = importlib.util.spec_from_file_location("create_lerobot_latent_view", SCRIPT_PATH)
VIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VIEW)


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def test_create_data_view_links_assets_and_generates_action_config(tmp_path):
    source_repo = tmp_path / "source" / "task-a"
    source_meta = source_repo / "meta"
    source_meta.mkdir(parents=True)
    (source_repo / "data").mkdir()
    (source_repo / "videos").mkdir()
    (source_meta / "info.json").write_text("{}\n", encoding="utf-8")
    write_jsonl(
        source_meta / "episodes_ori.jsonl",
        [
            {
                "episode_index": 0,
                "tasks": ["pick up the block"],
                "length": 12,
            },
            {"episode_index": 1, "tasks": ["unused"], "length": 9},
        ],
    )

    latent_root = tmp_path / "latents" / "task-a" / "latents"
    for camera in ("cam_high", "cam_wrist"):
        camera_dir = latent_root / "chunk-000" / camera
        camera_dir.mkdir(parents=True)
        (camera_dir / "episode_000000_0_12.pth").touch()

    manifest = tmp_path / "robotwin_clean.jsonl"
    write_jsonl(
        manifest,
        [{"repo_id": str(source_repo), "latent_path": str(latent_root)}],
    )
    empty_embedding = tmp_path / "empty_emb.pt"
    empty_embedding.touch()
    output_root = tmp_path / "view"

    result = VIEW.create_data_view([manifest], output_root, empty_embedding)
    repeated_result = VIEW.create_data_view([manifest], output_root, empty_embedding)

    dataset = output_root / "datasets" / manifest.stem / source_repo.name
    episodes = [
        json.loads(line)
        for line in (dataset / "meta" / "episodes.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert result == repeated_result
    assert result["dataset_count"] == 1
    assert result["episodes_with_latents"] == 1
    assert result["latent_segment_count"] == 1
    assert (output_root / "empty_emb.pt").resolve() == empty_embedding.resolve()
    assert (dataset / "data").resolve() == (source_repo / "data").resolve()
    assert (dataset / "latents").resolve() == latent_root.resolve()
    assert episodes[0]["action_config"] == [
        {
            "start_frame": 0,
            "end_frame": 12,
            "action_text": "pick up the block",
        }
    ]
    assert episodes[1]["action_config"] == []


def test_action_config_uses_segments_shared_by_all_cameras(tmp_path):
    source_repo = tmp_path / "source" / "task-a"
    source_meta = source_repo / "meta"
    source_meta.mkdir(parents=True)
    (source_meta / "info.json").write_text("{}\n", encoding="utf-8")
    write_jsonl(
        source_meta / "episodes.jsonl",
        [
            {
                "episode_index": 0,
                "tasks": ["pick up the block"],
                "length": 12,
                "action_config": [
                    {
                        "start_frame": 0,
                        "end_frame": 6,
                        "action_text": "lift the block",
                    },
                    {
                        "start_frame": 6,
                        "end_frame": 12,
                        "action_text": "lift the block",
                    },
                ],
            },
            {
                "episode_index": 1,
                "tasks": ["unused"],
                "length": 9,
            },
        ],
    )

    latent_root = tmp_path / "latents" / "task-a" / "latents"
    for camera in ("cam_high", "cam_wrist"):
        camera_dir = latent_root / "chunk-000" / camera
        camera_dir.mkdir(parents=True)
        (camera_dir / "episode_000000_0_12.pth").touch()
    high_camera = latent_root / "chunk-000" / "cam_high"
    (high_camera / "episode_000001_0_9.pth").touch()

    destination = tmp_path / "view" / "task-a"
    result = VIEW.prepare_dataset_view(source_repo, latent_root, destination)
    episodes = VIEW.read_jsonl(destination / "meta" / "episodes.jsonl")

    assert result["source_action_config_count"] == 2
    assert result["latent_segment_count"] == 1
    assert episodes[0]["action_config"] == [
        {
            "start_frame": 0,
            "end_frame": 12,
            "action_text": "lift the block",
        }
    ]
    assert episodes[1]["action_config"] == []


def test_refresh_data_view_adds_new_shared_segments(tmp_path):
    source_repo = tmp_path / "source" / "task-a"
    source_meta = source_repo / "meta"
    source_meta.mkdir(parents=True)
    (source_meta / "info.json").write_text("{}\n", encoding="utf-8")
    write_jsonl(
        source_meta / "episodes_ori.jsonl",
        [
            {"episode_index": 0, "tasks": ["first"], "length": 12},
            {"episode_index": 1, "tasks": ["second"], "length": 9},
        ],
    )
    latent_root = tmp_path / "latents" / "task-a" / "latents"
    for camera in ("cam_high", "cam_wrist"):
        camera_dir = latent_root / "chunk-000" / camera
        camera_dir.mkdir(parents=True)
        (camera_dir / "episode_000000_0_12.pth").touch()

    manifest = tmp_path / "robotwin.jsonl"
    write_jsonl(
        manifest,
        [{"repo_id": str(source_repo), "latent_path": str(latent_root)}],
    )
    empty_embedding = tmp_path / "empty_emb.pt"
    empty_embedding.touch()
    output_root = tmp_path / "view"
    VIEW.create_data_view([manifest], output_root, empty_embedding)

    for camera in ("cam_high", "cam_wrist"):
        camera_dir = latent_root / "chunk-000" / camera
        (camera_dir / "episode_000001_0_9.pth").touch()
    result = VIEW.refresh_data_view(output_root)

    dataset = output_root / "datasets" / manifest.stem / source_repo.name
    episodes = VIEW.read_jsonl(dataset / "meta" / "episodes.jsonl")
    assert result["episodes_with_latents"] == 2
    assert result["latent_segment_count"] == 2
    assert episodes[1]["action_config"] == [
        {
            "start_frame": 0,
            "end_frame": 9,
            "action_text": "second",
        }
    ]
