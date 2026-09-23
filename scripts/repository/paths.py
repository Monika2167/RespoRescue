from pathlib import Path


def get_repository_paths(repository_id: int):
    base = Path("data") / "repositories" / str(repository_id)

    return {
        "base": base,
        "raw": base / "raw",
        "data": base / "data",
        "graph": base / "graph",
    }


def ensure_repository_dirs(repository_id: int):
    paths = get_repository_paths(repository_id)

    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    return paths
