from __future__ import annotations

import json
import re
from statistics import pstdev

from agents import function_tool


@function_tool
def inspect_document_metrics(text: str) -> str:
    """Measure paragraph and sentence variation and return deterministic JSON metrics."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paragraph_lengths = [len(p) for p in paragraphs]
    sentence_counts = [len([s for s in re.split(r"[.!؟؛]+", p) if s.strip()]) for p in paragraphs]
    starts = [re.sub(r"\s+", " ", p)[:40] for p in paragraphs]
    repeated_adjacent_starts = [
        i for i in range(1, len(starts))
        if starts[i].split(" ")[:2] == starts[i - 1].split(" ")[:2]
    ]
    payload = {
        "paragraph_count": len(paragraphs),
        "paragraph_lengths": paragraph_lengths,
        "sentence_counts": sentence_counts,
        "paragraph_length_stddev": round(pstdev(paragraph_lengths), 2) if len(paragraph_lengths) > 1 else 0,
        "repeated_adjacent_start_indexes": repeated_adjacent_starts,
    }
    return json.dumps(payload, ensure_ascii=False)


@function_tool
def extract_completion_placeholders(text: str) -> str:
    """Extract explicit [يستكمل من طرف المستخدم: ...] placeholders from a document."""
    placeholders = re.findall(r"\[يستكمل من طرف المستخدم:[^\]]+\]", text)
    return json.dumps({"placeholders": placeholders}, ensure_ascii=False)


@function_tool
def scan_sensitive_assertions(text: str) -> str:
    """List dates, percentages, money amounts and legal-reference-like tokens for verification."""
    patterns = {
        "dates": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b",
        "percentages": r"\b\d+(?:[.,]\d+)?\s*%",
        "amounts": r"\b\d+(?:[.,]\d+)?\s*(?:درهم|دراهم|DH|MAD)\b",
        "legal_tokens": r"(?:القانون|المرسوم|الظهير|القرار|الدورية)\s+(?:رقم\s*)?[\w./-]+",
    }
    found = {name: re.findall(pattern, text, flags=re.IGNORECASE) for name, pattern in patterns.items()}
    return json.dumps(found, ensure_ascii=False)
