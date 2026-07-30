from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents import Agent, handoff
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from .prompts import CORRECTION, DELIVERY, DRAFTER, EVIDENCE, FORMALITY, INTAKE, LANGUAGE, LEGAL, QUALITY
from .schemas import DraftOutput, EvidenceAudit, FinalDelivery, FormalityPlan, IntakeAnalysis, LanguageReview, LegalAudit
from .tools import extract_completion_placeholders, inspect_document_metrics, scan_sensitive_assertions


@dataclass
class WorkflowContext:
    job_id: str
    document_type: str
    user_request: str
    sources_text: str
    results: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)


intake_agent = Agent[WorkflowContext](
    name="محلل الطلب",
    handoff_description="يحلل الطلب ويصنف المعطيات قبل أي تحرير.",
    instructions=INTAKE,
    output_type=IntakeAnalysis,
)

evidence_agent = Agent[WorkflowContext](
    name="مدقق الموثوقية",
    handoff_description="يتحقق من الوقائع ويمنع إدراج أي معطى بلا سند.",
    instructions=EVIDENCE,
    tools=[scan_sensitive_assertions],
    output_type=EvidenceAudit,
)

formality_agent = Agent[WorkflowContext](
    name="خبير الشكليات المغربية",
    handoff_description="يحدد الشكل الإداري المغربي الملائم لنوع الوثيقة.",
    instructions=FORMALITY,
    output_type=FormalityPlan,
)

legal_agent = Agent[WorkflowContext](
    name="المراجع القانوني",
    handoff_description="يراجع الإحالات القانونية والاختصاص دون استكمال من الذاكرة.",
    instructions=LEGAL,
    tools=[scan_sensitive_assertions],
    output_type=LegalAudit,
)

drafter_agent = Agent[WorkflowContext](
    name="المحرر الإداري",
    handoff_description="يصوغ الوثيقة الإدارية النهائية اعتمادا على الوقائع المعتمدة.",
    instructions=DRAFTER,
    output_type=DraftOutput,
)

language_agent = Agent[WorkflowContext](
    name="المدقق اللغوي والأسلوبي",
    handoff_description="يراجع اللغة والأسلوب ويحافظ على الوقائع ودرجة الإلزام.",
    instructions=LANGUAGE,
    tools=[inspect_document_metrics],
    output_type=LanguageReview,
)

# تُربط هذه الوكلاء بعد إنشائها لإقامة حلقة handoff فعلية قابلة لإعادة المراجعة.
quality_agent = Agent[WorkflowContext](
    name="مراقب الجودة",
    handoff_description="يفحص بوابات الاعتماد ويقرر التصحيح أو التسليم.",
    instructions=prompt_with_handoff_instructions(QUALITY),
    tools=[inspect_document_metrics, extract_completion_placeholders, scan_sensitive_assertions],
)

correction_agent = Agent[WorkflowContext](
    name="وكيل التصحيح",
    handoff_description="يصحح العيوب المحددة ثم يعيد الوثيقة إلى مراقب الجودة.",
    instructions=prompt_with_handoff_instructions(CORRECTION),
    tools=[inspect_document_metrics, extract_completion_placeholders],
)

delivery_agent = Agent[WorkflowContext](
    name="وكيل التسليم النهائي",
    handoff_description="يسلم الوثيقة بعد اعتماد مراقب الجودة.",
    instructions=DELIVERY,
    tools=[extract_completion_placeholders],
    output_type=FinalDelivery,
)

quality_agent.handoffs = [
    handoff(
        agent=correction_agent,
        tool_name_override="transfer_to_correction_agent",
        tool_description_override="حوّل إلى وكيل التصحيح عند وجود أي عيب يمنع الاعتماد.",
        nest_handoff_history=True,
    ),
    handoff(
        agent=delivery_agent,
        tool_name_override="transfer_to_final_delivery_agent",
        tool_description_override="حوّل إلى وكيل التسليم النهائي فقط بعد اجتياز جميع بوابات الجودة.",
        nest_handoff_history=True,
    ),
]

correction_agent.handoffs = [
    handoff(
        agent=quality_agent,
        tool_name_override="return_to_quality_gate",
        tool_description_override="أعد الوثيقة المصححة إلى مراقب الجودة لإعادة الفحص.",
        nest_handoff_history=True,
    )
]

ALL_AGENTS = {
    agent.name: agent
    for agent in [
        intake_agent,
        evidence_agent,
        formality_agent,
        legal_agent,
        drafter_agent,
        language_agent,
        quality_agent,
        correction_agent,
        delivery_agent,
    ]
}
