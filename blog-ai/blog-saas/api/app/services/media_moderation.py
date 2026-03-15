"""
Moderación de imágenes y videos via Sightengine
"""
import os
import requests

SIGHTENGINE_USER = os.getenv("SIGHTENGINE_USER", "131120284")
SIGHTENGINE_SECRET = os.getenv("SIGHTENGINE_SECRET", "FPKCnucbF6ZFjqcrtupgxDHJu3Adiz5b")

MODELS = "nudity-2.1,violence,gore,weapon,drug,hate-symbols"

THRESHOLDS = {
    "nudity": 0.4,
    "violence": 0.5,
    "gore": 0.5,
    "weapon": 0.7,
    "drug": 0.7,
}

def moderate_image(url: str) -> dict:
    """
    Modera una imagen via URL.
    Returns: {"approved": bool, "reason": str | None}
    """
    try:
        res = requests.get(
            "https://api.sightengine.com/1.0/check.json",
            params={
                "url": url,
                "models": MODELS,
                "api_user": SIGHTENGINE_USER,
                "api_secret": SIGHTENGINE_SECRET,
            },
            timeout=10,
        )
        data = res.json()
        if data.get("status") != "success":
            print(f"[moderation] error: {data}")
            return {"approved": True, "reason": None}  # fail open

        # Nudity
        nudity = data.get("nudity", {})
        nudity_score = max(
            nudity.get("sexual_activity", 0),
            nudity.get("sexual_display", 0),
            nudity.get("erotica", 0),
            nudity.get("very_suggestive", 0),
        )
        if nudity_score > THRESHOLDS["nudity"]:
            return {"approved": False, "reason": "nudity"}

        # Violence
        violence = data.get("violence", {}).get("prob", 0)
        if violence > THRESHOLDS["violence"]:
            return {"approved": False, "reason": "violence"}

        # Gore
        gore = data.get("gore", {}).get("prob", 0)
        if gore > THRESHOLDS["gore"]:
            return {"approved": False, "reason": "gore"}

        # Weapons
        weapon = data.get("weapon", {})
        if weapon.get("classes", {}).get("firearm", 0) > THRESHOLDS["weapon"]:
            return {"approved": False, "reason": "weapons"}

        # Drugs
        drug = data.get("drug", {})
        if drug.get("prob", 0) > THRESHOLDS["drug"]:
            return {"approved": False, "reason": "drugs"}

        # Hate symbols
        hate = data.get("hate-symbol", {})
        if hate.get("prob", 0) > 0.7:
            return {"approved": False, "reason": "hate_symbols"}

        return {"approved": True, "reason": None}

    except Exception as e:
        print(f"[moderation] exception: {e}")
        return {"approved": True, "reason": None}  # fail open


def moderate_video(url: str) -> dict:
    """
    Modera un video via URL — usa el primer frame como imagen.
    Returns: {"approved": bool, "reason": str | None}
    """
    try:
        # Para videos cortos, analizar como imagen el thumbnail
        # Primero intentar con check-sync
        res = requests.post(
            "https://api.sightengine.com/1.0/video/check-sync.json",
            data={
                "stream_url": url,
                "models": "nudity-2.1,violence,gore,weapon,drug",
                "api_user": SIGHTENGINE_USER,
                "api_secret": SIGHTENGINE_SECRET,
                "callback_url": "",
            },
            timeout=30,
        )
        data = res.json()
        if data.get("status") != "success":
            print(f"[moderation] video error: {data}")
            return {"approved": True, "reason": None}

        # Check frames
        frames = data.get("data", {}).get("frames", [])
        for frame in frames:
            nudity = frame.get("nudity", {})
            nudity_score = max(
                nudity.get("sexual_activity", 0),
                nudity.get("sexual_display", 0),
                nudity.get("erotica", 0),
                nudity.get("very_suggestive", 0),
            )
            if nudity_score > THRESHOLDS["nudity"]:
                return {"approved": False, "reason": "nudity"}
            if frame.get("violence", {}).get("prob", 0) > THRESHOLDS["violence"]:
                return {"approved": False, "reason": "violence"}
            if frame.get("gore", {}).get("prob", 0) > THRESHOLDS["gore"]:
                return {"approved": False, "reason": "gore"}

        return {"approved": True, "reason": None}

    except Exception as e:
        print(f"[moderation] video exception: {e}")
        return {"approved": True, "reason": None}


def moderate_media(url: str, media_type: str) -> dict:
    if media_type == "video":
        return moderate_video(url)
    return moderate_image(url)
