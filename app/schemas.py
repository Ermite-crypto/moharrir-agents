from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class IntakeAnalysis(BaseModel):
    document_type: str
    goal: str
    issuing_authority: str | None = None
    recipient: str | None = None
    subject: str | None = None
    confirmed_facts: list[str] = Field(default_factory=list)
    missing_essential_fields: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    irrelevant_material: list[str] = Field(default_factory=list)
    execution_possible: bool = True


class EvidenceAudit(BaseModel):
    verified_facts: list[str] = Field(default_factory=list)
    unsupported_claims_to_forbid: list[str] = Field(default_factory=list)
    exact_names_numbers_dates_references: list[str] = Field(default_factory=list)
    missing_placeholders: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    reliability_notes: list[str] = Field(default_factory=list)


class FormalityPlan(BaseModel):
    document_type: str
    required_elements: list[str] = Field(default_factory=list)
    omitted_elements: list[str] = Field(default_factory=list)
    opening_formula: str | None = None
    closing_formula: str | None = None
    organization_logic: str
    register_notes: list[str] = Field(default_factory=list)


class LegalAudit(BaseModel):
    exact_legal_references: list[str] = Field(default_factory=list)
    unverifiable_legal_references: list[str] = Field(default_factory=list)
    forbidden_legal_inferences: list[str] = Field(default_factory=list)
    authority_or_competence_risks: list[str] = Field(default_factory=list)
    legal_placeholders: list[str] = Field(default_factory=list)


class DraftOutput(BaseModel):
    document_text: str
    completion_placeholders: list[str] = Field(default_factory=list)
    drafting_notes_for_next_agent: list[str] = Field(default_factory=list)


class LanguageReview(BaseModel):
    revised_document: str
    corrections_made: list[str] = Field(default_factory=list)
    unresolved_issues: list[str] = Field(default_factory=list)


class FinalDelivery(BaseModel):
    status: Literal["approved", "approved_with_placeholders"]
    document_text: str
    placeholders: list[str] = Field(default_factory=list)
    quality_summary: list[str] = Field(default_factory=list)
