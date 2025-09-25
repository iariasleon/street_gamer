import json
from pathlib import Path


def read_json_from_file(path):
    """Return JSON file read from a given path.

    :param path: dir where to read the file
    :return: dict with the info
    """
    file = Path(path)
    if not file.is_file():
        raise IOError(f"File {path} could not be found")
    try:
        return json.loads(file.read_text(encoding="utf8"))
    except ValueError as error:
        raise ValueError(f"Decoding file {path} to JSON failed") from error
