from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.config import settings
from backend.lib.assignment.methods.round_robin_load_aware import (
    RoundRobinLoadAwareStrategy,
)
from backend.models.lead import Lead
from backend.models.user import Agent


@dataclass(frozen=True)
class AgentLoad:
    agent_id: int
    lead_count: int


class AssignmentStrategy(Protocol):
    name: str

    def select_agent_id(
        self, db: Session, agent_loads: list[AgentLoad]
    ) -> int | None: ...


def _get_active_agent_loads(db: Session) -> list[AgentLoad]:
    rows = (
        db.query(Agent.id, func.count(Lead.id).label("lead_count"))
        .outerjoin(Lead, Lead.assigned_agent_id == Agent.id)
        .filter(Agent.is_active == 1)
        .group_by(Agent.id)
        .order_by(Agent.id.asc())
        .all()
    )
    return [AgentLoad(agent_id=row[0], lead_count=row[1]) for row in rows]


class AssignmentPipeline:
    def __init__(self, strategy: AssignmentStrategy):
        self.strategy = strategy

    def get_next_agent_id(self, db: Session) -> int | None:
        active_agent_loads = _get_active_agent_loads(db)
        return self.strategy.select_agent_id(db, active_agent_loads)


STRATEGIES: dict[str, AssignmentStrategy] = {
    RoundRobinLoadAwareStrategy.name: RoundRobinLoadAwareStrategy(),
}


def get_assignment_pipeline(strategy_name: str | None = None) -> AssignmentPipeline:
    selected_name = strategy_name or settings.assignment_strategy
    selected_strategy = STRATEGIES.get(selected_name)

    if not selected_strategy:
        selected_strategy = STRATEGIES[RoundRobinLoadAwareStrategy.name]

    return AssignmentPipeline(selected_strategy)


def get_next_assigned_agent_id(
    db: Session, strategy_name: str | None = None
) -> int | None:
    pipeline = get_assignment_pipeline(strategy_name)
    return pipeline.get_next_agent_id(db)
