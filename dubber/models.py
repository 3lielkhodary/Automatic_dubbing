from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DubbingResult:
    

    output_path: str
    source_language: str
    target_language: str
    original_text: str
    translated_text: str

    # Runtime metrics populated by the pipeline
    original_duration_s: float = 0.0
    dubbed_duration_s: float = 0.0
    tempo_factor: float = 1.0

    def __str__(self) -> str:
        return (
            f"DubbingResult(\n"
            f"  output        : {self.output_path}\n"
            f"  {self.source_language} → {self.target_language}\n"
            f"  original      : {self.original_text[:80]}…\n"
            f"  translated    : {self.translated_text[:80]}…\n"
            f"  duration      : {self.original_duration_s:.1f}s → {self.dubbed_duration_s:.1f}s "
            f"(tempo ×{self.tempo_factor:.2f})\n"
            f")"
        )
