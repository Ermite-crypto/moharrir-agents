from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from agents import OpenAIProvider, RunConfig, Runner, SQLiteSession, trace
from pydantic import BaseModel

from .agents_system import (
    WorkflowContext,
    drafter_agent,
    evidence_agent,
    formality_agent,
    intake_agent,
    language_agent,
    legal_agent,
    quality_agent,
)
from .schemas import FinalDelivery


def serialize(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, dict):
        return {k: serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [serialize(v) for v in value]
    return value


async def run_stage(agent, prompt: str, ctx: WorkflowContext, session, run_config, max_turns: int = 5):
    result = await Runner.run(
        agent,
        prompt,
        context=ctx,
        session=session,
        run_config=run_config,
        max_turns=max_turns,
    )
    output = serialize(result.final_output)
    ctx.events.append({
        "stage": agent.name,
        "last_agent": result.last_agent.name,
        "output": output,
    })
    return result.final_output


async def execute_workflow(
    *,
    api_key: str,
    model: str,
    document_type: str,
    user_request: str,
    source_text: str,
    sessions_db: Path,
) -> dict[str, Any]:
    job_id = uuid4().hex
    ctx = WorkflowContext(
        job_id=job_id,
        document_type=document_type,
        user_request=user_request,
        sources_text=source_text,
    )

    provider = OpenAIProvider(api_key=api_key, use_responses=True)
    run_config = RunConfig(
        model=model,
        model_provider=provider,
        trace_include_sensitive_data=False,
        tracing={"api_key": api_key},
    )
    session = SQLiteSession(job_id, str(sessions_db))

    base_input = f"""نوع الوثيقة: {document_type}\n\nطلب المستخدم:\n{user_request}\n\nالمادة المصدرية المسموح اعتمادها:\n{source_text or '[لا توجد مرفقات نصية]'}"""

    with trace(
        "Moharrir Independent Agents Workflow",
        group_id=job_id,
        metadata={"document_type": document_type, "model": model},
    ):
        intake = await run_stage(intake_agent, base_input, ctx, session, run_config)
        ctx.results["intake"] = serialize(intake)

        evidence = await run_stage(
            evidence_agent,
            f"حلل الموثوقية انطلاقا من المادة الأصلية وهذا التحليل:\n{json.dumps(ctx.results['intake'], ensure_ascii=False)}\n\n{base_input}",
            ctx, session, run_config,
        )
        ctx.results["evidence"] = serialize(evidence)

        formality = await run_stage(
            formality_agent,
            f"ضع خطة الشكليات دون صياغة الوثيقة.\nنوع الوثيقة: {document_type}\nتحليل الطلب:\n{json.dumps(ctx.results['intake'], ensure_ascii=False)}",
            ctx, session, run_config,
        )
        ctx.results["formality"] = serialize(formality)

        legal = await run_stage(
            legal_agent,
            f"راجع الإحالات والاختصاص.\nتدقيق الموثوقية:\n{json.dumps(ctx.results['evidence'], ensure_ascii=False)}\n\nالمادة الأصلية:\n{source_text}",
            ctx, session, run_config,
        )
        ctx.results["legal"] = serialize(legal)

        draft = await run_stage(
            drafter_agent,
            "صغ الوثيقة النهائية اعتمادا حصرا على الحزمة التالية:\n" + json.dumps(ctx.results, ensure_ascii=False),
            ctx, session, run_config,
            max_turns=7,
        )
        ctx.results["draft"] = serialize(draft)

        language = await run_stage(
            language_agent,
            "راجع الوثيقة التالية دون تغيير الوقائع أو درجة الإلزام:\n" + json.dumps(ctx.results, ensure_ascii=False),
            ctx, session, run_config,
            max_turns=7,
        )
        ctx.results["language"] = serialize(language)

        reviewed_text = ctx.results["language"]["revised_document"]
        quality_prompt = f"""
افحص الوثيقة الآتية بوصفك بوابة الاعتماد. لديك تقارير الموثوقية والقانون والشكليات.
يجب أن تستخدم handoff إلى وكيل التصحيح أو وكيل التسليم النهائي، ولا تجب بنفسك.

الوثيقة:
{reviewed_text}

تقارير الضبط:
{json.dumps({k: ctx.results[k] for k in ['evidence', 'formality', 'legal']}, ensure_ascii=False)}
"""
        final_result = await Runner.run(
            quality_agent,
            quality_prompt,
            context=ctx,
            session=session,
            run_config=run_config,
            max_turns=14,
        )
        handoff_agents = []
        for item in final_result.new_items:
            agent = getattr(item, "agent", None)
            if agent is not None:
                handoff_agents.append(agent.name)
        ctx.events.append({
            "stage": "بوابة الجودة وعمليات handoff",
            "last_agent": final_result.last_agent.name,
            "agents_seen": handoff_agents,
            "output": serialize(final_result.final_output),
        })

        final_output = final_result.final_output
        if not isinstance(final_output, FinalDelivery):
            raise RuntimeError(
                "لم ينته مسار handoff عند وكيل التسليم النهائي. "
                f"آخر وكيل: {final_result.last_agent.name}"
            )

    return {
        "job_id": job_id,
        "status": final_output.status,
        "document_text": final_output.document_text,
        "placeholders": final_output.placeholders,
        "quality_summary": final_output.quality_summary,
        "events": ctx.events,
        "agent_architecture": {
            "sdk": "OpenAI Agents SDK (Python)",
            "independent_agents": 9,
            "orchestration": "code-orchestrated specialists + autonomous handoff quality loop",
            "session": "SQLiteSession",
            "tracing": True,
        },
    }
