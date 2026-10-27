# -*- coding: utf-8 -*-
"""
:Module:            obforce.sync.reporting
:Synopsis:          Returns bounded redacted internal plan reports without I/O
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from obforce import constants as const
from obforce.errors import ExitCode, ModelError, exit_code
from obforce.models import Coverage, CoverageStatus
from obforce.sync.planner import ActionKind, ChangeAction, ChangePlan, DashboardAction, Diagnostic


@dataclass(frozen=True)
class PlanReport:
    """Hold safe display text and the existing terminal outcome without printing."""

    text: str
    outcome: ExitCode


def report_plan(plan: ChangePlan, *, details: bool = False, outcomes: tuple[ExitCode, ...] = ()) -> PlanReport:
    """Format fixed summaries and opt-in UUID/action details, never content or paths.

    :raises ModelError: For invalid inputs or excessive requested output; no truncation.
    """
    if (
        not isinstance(plan, ChangePlan)
        or type(plan.actions) is not tuple
        or not all(isinstance(action, ChangeAction) for action in plan.actions)
        or not isinstance(plan.outcome, ExitCode)
        or type(plan.blocked) is not bool
        or (plan.coverage is not None and not isinstance(plan.coverage, Coverage))
        or type(details) is not bool
        or type(outcomes) is not tuple
        or len(outcomes) > 5
        or any(not isinstance(code, ExitCode) for code in outcomes)
        or len(plan.actions) > const.MAX_PLAN_ACTIONS
        or (plan.diagnostic is not None and not isinstance(plan.diagnostic, Diagnostic))
        or (plan.dashboard is not None and not isinstance(plan.dashboard, DashboardAction))
    ):
        raise ModelError('Invalid report inputs')
    if details and len(plan.actions) > const.MAX_REPORT_ACTIONS:
        raise ModelError('Detailed report exceeds action bound')
    for action in plan.actions:
        if (
            not isinstance(action.kind, ActionKind)
            or type(action.content_changed) is not bool
            or type(action.state_changed) is not bool
        ):
            raise ModelError('Invalid report action')
        if action.identity is not None:
            try:
                if type(action.identity) is not str or str(UUID(action.identity)) != action.identity:
                    raise ValueError
            except (ValueError, TypeError, AttributeError):
                raise ModelError('Invalid report identity') from None
    outcome = exit_code((plan.outcome, *outcomes))
    lines = [
        f'Plan: {"blocked" if plan.blocked or outcome in (1, 2, 3) else "candidate"}; outcome: {int(outcome)}',
        '; '.join(f'{kind.value}: {count}' for kind, count in plan.counts),
    ]
    lines.append('Counts above describe notes; moves reconcile locations without renaming files.')
    if plan.dashboard is not None:
        lines.append(f'Dashboard: {plan.dashboard.kind.value}; state file changed: {str(plan.state_changed).lower()}')
    if plan.diagnostic is not None:
        lines.append(f'Diagnostic: {plan.diagnostic.value}')
        lines.append(
            {
                Diagnostic.CONFLICT: 'Resolve edited/missing managed content or ownership/scope collisions; then preview again.',
                Diagnostic.INVALID: 'Check explicit options, configuration and documented input/output limits.',
                Diagnostic.READ: 'Check permissions and stable input ancestry; no automatic retry is performed.',
            }[plan.diagnostic]
        )
    if plan.coverage is not None:
        for name in ('inventory', 'audit', 'relationships'):
            facet = getattr(plan.coverage, name)
            lines.append(
                f'{name}: {facet.status.value}; requested: {str(facet.requested).lower()}; warnings: {len(facet.warnings)}'
            )
            if facet.requested and facet.status != CoverageStatus.COMPLETE:
                lines.append(f'Warning: requested {name} coverage is {facet.status.value}.')
            if not facet.requested and facet.status != CoverageStatus.COMPLETE:
                lines.append(f'{name}: excluded from this collection; absence is not a negative fact.')
        if not plan.coverage.selection.include_namespaced:
            lines.append('Namespaced components excluded by selection.')
        if plan.coverage.binding.mode == 'local':
            lines.append('Local inventory covers declared project files only; Salesforce audit/dependencies are unavailable.')
        lines.append('Warning counts describe collection limitations; raw private warnings are omitted.')
        lines.append('Relationship coverage does not prove runtime dependencies or comprehensive impact.')
    if details:
        for index, action in enumerate(plan.actions, 1):
            lines.append(
                f'{index}: {action.kind.value}; id: {action.identity or "unavailable"}; '
                f'content_changed: {str(action.content_changed).lower()}; state_changed: {str(action.state_changed).lower()}'
            )
    text = '\n'.join(lines) + '\n'
    if len(text.encode('utf-8')) > const.MAX_REPORT_BYTES:
        raise ModelError('Report exceeds byte bound')
    return PlanReport(text, outcome)
