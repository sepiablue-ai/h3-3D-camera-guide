"""Deterministic camera contract shared with web/camera.js. Y up, +Z front."""
import json
import math

DEFAULT = {"version": 1, "keys": [
    {"t": 0, "orbit": 0, "elevation": 85, "distance": 4, "target": [0, 1, 0], "fov": 45},
    {"t": 1, "orbit": 0, "elevation": 0, "distance": 4, "target": [0, 1, 0], "fov": 45},
    {"t": 5.125, "orbit": 90, "elevation": 0, "distance": 4, "target": [0, 1, 0], "fov": 45},
]}


def parse_state(value):
    state = json.loads(value) if isinstance(value, str) else value
    if state.get("version") != 1:
        raise ValueError("Camera state version must be 1")
    keys = state.get("keys", [])
    if not 1 <= len(keys) <= 200:
        raise ValueError("Use 1 to 200 camera keyframes")
    result = []
    for key in keys:
        k = {name: float(key[name]) for name in ("t", "orbit", "elevation", "distance", "fov")}
        k["target"] = list(map(float, key["target"]))
        if len(k["target"]) != 3 or not all(math.isfinite(x) for x in [*k["target"], *[k[n] for n in ("t", "orbit", "elevation", "distance", "fov")]]):
            raise ValueError("Camera values must be finite, with a three-component target")
        if not (0 <= k["t"] <= 120 and -89.9 <= k["elevation"] <= 89.9 and 0.5 <= k["distance"] <= 50 and 10 <= k["fov"] <= 100):
            raise ValueError("Camera keyframe is out of bounds")
        if any(abs(x) > 20 for x in k["target"]):
            raise ValueError("Target must be within +/-20 scene units")
        result.append(k)
    result.sort(key=lambda k: k["t"])
    if any(b["t"] - a["t"] < 1e-6 for a, b in zip(result, result[1:])):
        raise ValueError("Keyframe times must be unique")
    return {"version": 1, "keys": result}


def sample(state, t):
    keys = state["keys"]
    if t <= keys[0]["t"]:
        return dict(keys[0])
    if t >= keys[-1]["t"]:
        return dict(keys[-1])
    for a, b in zip(keys, keys[1:]):
        if a["t"] <= t <= b["t"]:
            u = (t - a["t"]) / (b["t"] - a["t"])
            u = u * u * (3 - 2 * u)  # C1 ease-in/out; explicit turns, no angle wrapping.
            k = {n: a[n] + (b[n] - a[n]) * u for n in ("orbit", "elevation", "distance", "fov")}
            k["target"] = [x + (y - x) * u for x, y in zip(a["target"], b["target"])]
            k["t"] = t
            return k


def basis(k):
    a, e = math.radians(k["orbit"]), math.radians(k["elevation"])
    back = [math.sin(a) * math.cos(e), math.sin(e), math.cos(a) * math.cos(e)]
    right = [math.cos(a), 0, -math.sin(a)]
    up = [-math.sin(a) * math.sin(e), math.cos(e), -math.cos(a) * math.sin(e)]
    pos = [v + k["distance"] * d for v, d in zip(k["target"], back)]
    return pos, right, up, [-x for x in back]
