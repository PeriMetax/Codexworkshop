import io
import json
from typing import Any

import pandas as pd
from fastapi import UploadFile


SUPPORTED_EXTENSIONS = {"csv", "xlsx", "json"}


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


def read_tabular_file(upload: UploadFile) -> list[dict[str, Any]]:
    ext = _extension(upload.filename or "")
    content = upload.file.read()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == "csv":
        df = pd.read_csv(io.BytesIO(content))
        return df.fillna("").to_dict(orient="records")
    if ext == "xlsx":
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        return df.fillna("").to_dict(orient="records")
    if ext == "json":
        return json.loads(content.decode("utf-8"))

    return []


def parse_mapping(mapping_obj: dict[str, Any]) -> dict[str, Any]:
    required = ["delimiter", "components"]
    missing = [key for key in required if key not in mapping_obj]
    if missing:
        raise ValueError(f"Mapping missing required keys: {missing}")
    return mapping_obj
