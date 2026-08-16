#!/usr/bin/env python3
"""Create an open-format LeRobot view over separately stored latents."""

import argparse
import json
import os
import re
from collections import defaultdict
from pathlib import Path


EPISODE_FILE_RE = re.compile(r"^episode_(\d+)_(\d+)_(\d+)\.pth$")
VIEW_MARKER = ".next_forcing_data_view.json"
VIEW_FORMAT_VERSION = 2


def read_jsonl(path):
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path} at line {line_number}: {exc}"
                ) from exc
    return records


def ensure_symlink(link_path, target_path):
    target_path = target_path.resolve(strict=True)
    if os.path.lexists(link_path):
        if not link_path.is_symlink():
            raise FileExistsError(f"Refusing to replace existing path: {link_path}")
        current_target = Path(os.readlink(link_path))
        if not current_target.is_absolute():
            current_target = link_path.parent / current_target
        if current_target.resolve(strict=True) != target_path:
            raise FileExistsError(
                f"Symlink target mismatch for {link_path}: "
                f"{current_target} != {target_path}"
            )
        return
    link_path.symlink_to(target_path, target_is_directory=target_path.is_dir())


def write_json(path, value, replace_existing=False):
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return
        if not replace_existing:
            raise FileExistsError(f"Refusing to replace different file: {path}")
    temporary_path = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary_path.write_text(content, encoding="utf-8")
    os.replace(temporary_path, path)


def scan_latent_segments(latent_root):
    chunk_dirs = sorted(path for path in latent_root.glob("chunk-*") if path.is_dir())
    if not chunk_dirs:
        raise FileNotFoundError(f"No chunk-* directories found under {latent_root}")

    camera_names = sorted(
        {
            camera_dir.name
            for chunk_dir in chunk_dirs
            for camera_dir in chunk_dir.iterdir()
            if camera_dir.is_dir()
        }
    )
    if not camera_names:
        raise FileNotFoundError(f"No camera latent directories found under {latent_root}")

    segments_by_camera = {camera: set() for camera in camera_names}
    for chunk_dir in chunk_dirs:
        for camera_name in camera_names:
            camera_dir = chunk_dir / camera_name
            if not camera_dir.is_dir():
                continue
            for latent_file in camera_dir.glob("episode_*.pth"):
                match = EPISODE_FILE_RE.match(latent_file.name)
                if match is None:
                    continue
                segments_by_camera[camera_name].add(
                    tuple(map(int, match.groups()))
                )

    shared_segments = set.intersection(
        *(segments_by_camera[camera] for camera in camera_names)
    )
    if not shared_segments:
        raise FileNotFoundError(
            f"No latent segments are shared by all cameras under {latent_root}"
        )
    segments = defaultdict(set)
    for episode_index, start_frame, end_frame in shared_segments:
        segments[episode_index].add((start_frame, end_frame))
    return {key: sorted(value) for key, value in segments.items()}, camera_names


def action_text_for_episode(record):
    tasks = record.get("tasks", [])
    if isinstance(tasks, list) and tasks:
        return str(tasks[0])
    if isinstance(tasks, str):
        return tasks
    return ""


def action_text_for_segment(record, start_frame, end_frame):
    source_configs = record.get("action_config") or []
    for source_config in source_configs:
        if (
            int(source_config["start_frame"]) == start_frame
            and int(source_config["end_frame"]) == end_frame
        ):
            return str(source_config.get("action_text", ""))

    source_texts = {
        str(source_config.get("action_text", ""))
        for source_config in source_configs
        if source_config.get("action_text")
    }
    if len(source_texts) == 1:
        return source_texts.pop()
    return action_text_for_episode(record)


def build_episodes_file(
    source_path,
    destination_path,
    latent_root,
    replace_existing=False,
):
    latent_segments, camera_names = scan_latent_segments(latent_root)
    records = read_jsonl(source_path)
    prepared_records = []
    included_episodes = 0
    latent_segment_count = 0
    source_action_config_count = 0

    for record in records:
        episode_index = int(record["episode_index"])
        segments = latent_segments.get(episode_index, [])
        source_action_config_count += len(record.get("action_config") or [])
        action_config = [
            {
                "start_frame": start_frame,
                "end_frame": end_frame,
                "action_text": action_text_for_segment(
                    record,
                    start_frame,
                    end_frame,
                ),
            }
            for start_frame, end_frame in segments
        ]
        output_record = dict(record)
        output_record["action_config"] = action_config
        prepared_records.append(output_record)
        included_episodes += bool(action_config)
        latent_segment_count += len(action_config)

    temporary_path = destination_path.with_name(
        f".{destination_path.name}.tmp-{os.getpid()}"
    )
    with temporary_path.open("w", encoding="utf-8") as handle:
        for record in prepared_records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    if destination_path.exists():
        if destination_path.read_bytes() == temporary_path.read_bytes():
            temporary_path.unlink()
        elif not replace_existing:
            temporary_path.unlink()
            raise FileExistsError(
                f"Refusing to replace different file: {destination_path}"
            )
        else:
            os.replace(temporary_path, destination_path)
    else:
        os.replace(temporary_path, destination_path)

    return {
        "episodes": len(prepared_records),
        "episodes_with_latents": included_episodes,
        "latent_segment_count": latent_segment_count,
        "source_action_config_count": source_action_config_count,
        "camera_names": camera_names,
    }


def prepare_dataset_view(
    source_repo,
    latent_root,
    destination,
    replace_existing=False,
):
    source_repo = source_repo.resolve(strict=True)
    latent_root = latent_root.resolve(strict=True)
    source_meta = source_repo / "meta"
    if not source_meta.is_dir():
        raise FileNotFoundError(f"Missing metadata directory: {source_meta}")

    source_episodes = source_meta / "episodes.jsonl"
    if not source_episodes.is_file():
        source_episodes = source_meta / "episodes_ori.jsonl"
    if not source_episodes.is_file():
        raise FileNotFoundError(
            f"Missing episodes.jsonl or episodes_ori.jsonl under {source_meta}"
        )

    destination.mkdir(parents=True, exist_ok=True)
    for directory_name in ("data", "videos"):
        source_directory = source_repo / directory_name
        if source_directory.exists():
            ensure_symlink(destination / directory_name, source_directory)
    ensure_symlink(destination / "latents", latent_root)

    destination_meta = destination / "meta"
    destination_meta.mkdir(exist_ok=True)
    for source_path in sorted(source_meta.iterdir()):
        if source_path.name == "episodes.jsonl":
            continue
        ensure_symlink(destination_meta / source_path.name, source_path)

    return build_episodes_file(
        source_episodes,
        destination_meta / "episodes.jsonl",
        latent_root,
        replace_existing=replace_existing,
    )


def manifest_destinations(manifest_path, records, output_root):
    repo_paths = [Path(record["repo_id"]).resolve(strict=True) for record in records]
    if len(repo_paths) == 1:
        common_root = repo_paths[0].parent
    else:
        common_root = Path(os.path.commonpath([str(path) for path in repo_paths]))

    manifest_root = output_root / "datasets" / manifest_path.stem
    for record, repo_path in zip(records, repo_paths):
        relative_path = repo_path.relative_to(common_root)
        yield record, manifest_root / relative_path


def summarize_view(output_root, summaries):
    return {
        "output_root": str(output_root),
        "dataset_count": len(summaries),
        "episode_count": sum(item["episodes"] for item in summaries),
        "episodes_with_latents": sum(
            item["episodes_with_latents"] for item in summaries
        ),
        "latent_segment_count": sum(
            item["latent_segment_count"] for item in summaries
        ),
        "datasets": summaries,
    }


def validate_managed_view(output_root):
    marker_path = output_root / VIEW_MARKER
    if not marker_path.is_file():
        raise FileExistsError(
            f"Output root is not a managed data view: {output_root}"
        )
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("type") != "next-forcing-lerobot-view":
        raise ValueError(f"Unexpected data view marker: {marker_path}")
    return marker_path


def write_view_marker(output_root):
    marker_path = output_root / VIEW_MARKER
    marker = {
        "format_version": VIEW_FORMAT_VERSION,
        "type": "next-forcing-lerobot-view",
    }
    write_json(marker_path, marker, replace_existing=True)


def create_data_view(manifest_paths, output_root, empty_embedding):
    output_root = output_root.resolve()
    existed_before = output_root.exists()
    output_root.mkdir(parents=True, exist_ok=True)
    if existed_before:
        validate_managed_view(output_root)

    write_view_marker(output_root)
    ensure_symlink(output_root / "empty_emb.pt", empty_embedding)

    summaries = []
    destinations = {}
    for manifest_path in manifest_paths:
        manifest_path = manifest_path.resolve(strict=True)
        records = read_jsonl(manifest_path)
        for record, destination in manifest_destinations(
            manifest_path, records, output_root
        ):
            source_repo = Path(record["repo_id"])
            latent_root = Path(record["latent_path"])
            previous_source = destinations.get(destination)
            if previous_source is not None and previous_source != source_repo:
                raise ValueError(f"Destination collision at {destination}")
            destinations[destination] = source_repo
            summary = prepare_dataset_view(
                source_repo,
                latent_root,
                destination,
                replace_existing=True,
            )
            summary.update(
                {
                    "dataset": str(destination.relative_to(output_root)),
                    "source_repo": str(source_repo),
                    "latent_root": str(latent_root),
                }
            )
            summaries.append(summary)

    result = summarize_view(output_root, summaries)
    write_json(
        output_root / "view_summary.json",
        result,
        replace_existing=True,
    )
    return result


def refresh_data_view(output_root):
    output_root = output_root.resolve(strict=True)
    validate_managed_view(output_root)
    summary_path = output_root / "view_summary.json"
    previous_summary = json.loads(summary_path.read_text(encoding="utf-8"))

    summaries = []
    for previous_dataset in previous_summary["datasets"]:
        destination = output_root / previous_dataset["dataset"]
        source_repo = Path(previous_dataset["source_repo"])
        latent_root = Path(previous_dataset["latent_root"])
        summary = prepare_dataset_view(
            source_repo,
            latent_root,
            destination,
            replace_existing=True,
        )
        summary.update(
            {
                "dataset": previous_dataset["dataset"],
                "source_repo": str(source_repo),
                "latent_root": str(latent_root),
            }
        )
        summaries.append(summary)

    write_view_marker(output_root)
    result = summarize_view(output_root, summaries)
    write_json(summary_path, result, replace_existing=True)
    return result


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--manifest",
        action="append",
        type=Path,
        help="JSONL manifest containing repo_id and latent_path fields; repeatable",
    )
    input_group.add_argument(
        "--refresh-view",
        type=Path,
        help="Refresh an existing managed view from its view_summary.json",
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--empty-emb", type=Path)
    args = parser.parse_args()
    if args.manifest and (args.output_root is None or args.empty_emb is None):
        parser.error("--manifest requires --output-root and --empty-emb")
    return args


def main():
    args = parse_args()
    if args.refresh_view is not None:
        result = refresh_data_view(args.refresh_view)
    else:
        result = create_data_view(args.manifest, args.output_root, args.empty_emb)
    print(
        json.dumps(
            {
                "output_root": result["output_root"],
                "dataset_count": result["dataset_count"],
                "episode_count": result["episode_count"],
                "episodes_with_latents": result["episodes_with_latents"],
                "latent_segment_count": result["latent_segment_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
