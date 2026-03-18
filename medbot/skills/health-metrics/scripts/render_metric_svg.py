#!/usr/bin/env python3
"""Render a simple SVG line chart from a metric JSONL file."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Series:
    label: str
    color: str
    values: list[float]


def load_entries(path: Path) -> list[dict]:
    entries: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return entries


def build_series(entries: list[dict]) -> tuple[list[str], list[Series], str]:
    if not entries:
        raise ValueError("metric file is empty")

    labels = [str(entry.get("timestamp", "")) for entry in entries]
    first = entries[0]

    if "systolic" in first or "diastolic" in first:
        systolic = [float(entry["systolic"]) for entry in entries if "systolic" in entry]
        diastolic = [float(entry["diastolic"]) for entry in entries if "diastolic" in entry]
        unit = str(first.get("unit", ""))
        if len(systolic) != len(entries) or len(diastolic) != len(entries):
            raise ValueError("all blood pressure entries must include systolic and diastolic")
        return labels, [
            Series("Systolic", "#d73a49", systolic),
            Series("Diastolic", "#1f77b4", diastolic),
        ], unit

    values = [float(entry["value"]) for entry in entries if "value" in entry]
    if len(values) != len(entries):
        raise ValueError("all metric entries must include value")
    unit = str(first.get("unit", ""))
    return labels, [Series("Value", "#1f77b4", values)], unit


def _scale_points(values: list[float], width: int, height: int, padding: int, min_value: float, max_value: float) -> list[tuple[float, float]]:
    plot_width = width - padding * 2
    plot_height = height - padding * 2
    span = max(max_value - min_value, 1.0)
    points: list[tuple[float, float]] = []
    count = max(len(values) - 1, 1)
    for idx, value in enumerate(values):
        x = padding + (plot_width * idx / count)
        y = padding + plot_height - ((value - min_value) / span * plot_height)
        points.append((x, y))
    return points


def _polyline(points: Iterable[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render_svg(entries: list[dict], title: str) -> str:
    labels, series_list, unit = build_series(entries)
    width = 900
    height = 420
    padding = 50

    all_values = [value for series in series_list for value in series.values]
    min_value = min(all_values)
    max_value = max(all_values)
    if min_value == max_value:
        min_value -= 1
        max_value += 1

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{padding}" y="28" font-size="20" font-family="Arial, sans-serif" fill="#111">{title}</text>',
        f'<text x="{padding}" y="48" font-size="12" font-family="Arial, sans-serif" fill="#666">{len(labels)} points{" · " + unit if unit else ""}</text>',
        f'<line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#999"/>',
        f'<line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#999"/>',
    ]

    for idx, series in enumerate(series_list):
        points = _scale_points(series.values, width, height, padding, min_value, max_value)
        lines.append(
            f'<polyline fill="none" stroke="{series.color}" stroke-width="3" points="{_polyline(points)}"/>'
        )
        legend_x = padding + idx * 160
        lines.append(f'<rect x="{legend_x}" y="{height - 24}" width="14" height="14" fill="{series.color}"/>')
        lines.append(
            f'<text x="{legend_x + 20}" y="{height - 12}" font-size="12" font-family="Arial, sans-serif" fill="#222">{series.label}</text>'
        )

    lines.append(
        f'<text x="{padding}" y="{height - padding + 20}" font-size="11" font-family="Arial, sans-serif" fill="#666">{labels[0]}</text>'
    )
    lines.append(
        f'<text x="{width - padding}" y="{height - padding + 20}" text-anchor="end" font-size="11" font-family="Arial, sans-serif" fill="#666">{labels[-1]}</text>'
    )
    lines.append(
        f'<text x="{padding - 10}" y="{padding + 5}" text-anchor="end" font-size="11" font-family="Arial, sans-serif" fill="#666">{max_value:g}</text>'
    )
    lines.append(
        f'<text x="{padding - 10}" y="{height - padding + 5}" text-anchor="end" font-size="11" font-family="Arial, sans-serif" fill="#666">{min_value:g}</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines)


def render_file(input_path: Path, output_path: Path, title: str | None = None) -> Path:
    entries = load_entries(input_path)
    svg = render_svg(entries, title or input_path.stem.replace("_", " ").title())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a metric JSONL file into an SVG line chart")
    parser.add_argument("input_path", help="Path to metric JSONL file")
    parser.add_argument("output_path", help="Path to output SVG file")
    parser.add_argument("--title", default=None, help="Chart title")
    args = parser.parse_args()

    render_file(Path(args.input_path), Path(args.output_path), args.title)
    print(args.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
