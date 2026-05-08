from __future__ import annotations

import io
from typing import Any


def preprocess_input(
    study_metadata: dict[str, Any],
    raw_bytes: bytes | None,
) -> dict[str, Any]:
    """
    Normaliza metadatos del estudio y, si aplica, extrae información básica
    desde píxeles (RX/PNG/JPEG típicos demo).
    """
    out: dict[str, Any] = {
        "modality": study_metadata.get("modality", "CT"),
        "study_instance_uid": study_metadata.get("study_instance_uid"),
        "has_pixel_data": raw_bytes is not None and len(raw_bytes) > 0,
    }
    if not out["has_pixel_data"] or raw_bytes is None:
        return out

    try:
        from PIL import Image  # type: ignore[import-untyped]

        with Image.open(io.BytesIO(raw_bytes)) as img:
            im = img.convert("L")
            w, h = im.size
            out["pil_width"], out["pil_height"] = w, h
            arr = []
            px = list(im.resize((96, 96)).getdata())
            if px:
                out["pil_mean_gray"] = sum(px) / len(px)
    except ImportError:
        out["pil_unavailable"] = True
    except Exception as exc:
        out["pil_error"] = str(exc)
    return out
