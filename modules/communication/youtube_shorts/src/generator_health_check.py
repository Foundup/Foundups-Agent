"""
Generator health checks for Veo3 and Sora2.

Keeps tests isolated from upload/scheduler flows.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneratorHealthResult:
    name: str
    ok: bool
    details: str
    output_path: Optional[str] = None


def check_veo3(test_generate: bool = False) -> GeneratorHealthResult:
    """Check Veo3 generator availability and optionally generate a short clip."""
    try:
        from .veo3_generator import Veo3Generator, Veo3GenerationError, InsufficientCreditsError

        previous = os.environ.get("FOUNDUPS_ENABLE_KEY_HYGIENE")
        os.environ["FOUNDUPS_ENABLE_KEY_HYGIENE"] = "0"
        gen = Veo3Generator()
        if not test_generate:
            _restore_key_hygiene(previous)
            return GeneratorHealthResult(
                name="veo3",
                ok=True,
                details="Initialized OK (no generation requested)",
            )

        prompt = "Abstract neon shapes slowly morphing on a dark background."
        path = gen.generate_video(prompt=prompt, duration=8, fast_mode=True)
        _restore_key_hygiene(previous)
        return GeneratorHealthResult(
            name="veo3",
            ok=True,
            details="Generated test clip",
            output_path=path,
        )
    except (Veo3GenerationError, InsufficientCreditsError) as e:
        return GeneratorHealthResult(name="veo3", ok=False, details=str(e))
    except Exception as e:
        return GeneratorHealthResult(name="veo3", ok=False, details=str(e))


def _restore_key_hygiene(previous: Optional[str]) -> None:
    if previous is None:
        os.environ.pop("FOUNDUPS_ENABLE_KEY_HYGIENE", None)
    else:
        os.environ["FOUNDUPS_ENABLE_KEY_HYGIENE"] = previous


def check_sora2(test_generate: bool = False) -> GeneratorHealthResult:
    """Check Sora2 generator availability and optionally generate a short clip."""
    try:
        from .sora2_generator import Sora2Generator, Sora2GenerationError

        gen = Sora2Generator()
        if not test_generate:
            return GeneratorHealthResult(
                name="sora2",
                ok=True,
                details="Initialized OK (no generation requested)",
            )

        prompt = "Cinematic slow pan across a futuristic city at dusk."
        path = gen.generate_video(prompt=prompt, duration=5, fast_mode=True, aspect_ratio="9:16")
        return GeneratorHealthResult(
            name="sora2",
            ok=True,
            details="Generated test clip",
            output_path=path,
        )
    except Sora2GenerationError as e:
        return GeneratorHealthResult(name="sora2", ok=False, details=str(e))
    except Exception as e:
        return GeneratorHealthResult(name="sora2", ok=False, details=str(e))
