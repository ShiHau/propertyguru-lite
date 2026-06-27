from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from backend.models.lead import Lead

if TYPE_CHECKING:
    from backend.lib.assignment.factory import AgentLoad

#TODO: Should be managed "globally" with redis for multi worker deployment
def _next_round_robin_id(db: Session, candidate_ids: list[int]) -> int | None:
    if not candidate_ids:
        return None

    sorted_candidates = sorted(candidate_ids)
    last_assigned = (
        db.query(Lead.assigned_agent_id)
        .filter(Lead.assigned_agent_id.in_(sorted_candidates))
        .order_by(Lead.id.desc())
        .first()
    )

    if not last_assigned or last_assigned[0] not in sorted_candidates:
        return sorted_candidates[0]

    current_index = sorted_candidates.index(last_assigned[0])
    next_index = (current_index + 1) % len(sorted_candidates)
    return sorted_candidates[next_index]


class RoundRobinLoadAwareStrategy:
    name = "round_robin_load_aware"

    def select_agent_id(self, db: Session, agent_loads: list["AgentLoad"]) -> int | None:
        if not agent_loads:
            return None

        load_values = [agent.lead_count for agent in agent_loads]
        min_load = min(load_values)
        max_load = max(load_values)

        # Catch-up mode: underloaded agents are selected until loads are balanced.
        if min_load < max_load:
            candidate_ids = [
                agent.agent_id for agent in agent_loads if agent.lead_count == min_load
            ]
            return _next_round_robin_id(db, candidate_ids)

        # Once balanced, continue standard round robin among all active agents.
        all_agent_ids = [agent.agent_id for agent in agent_loads]
        return _next_round_robin_id(db, all_agent_ids)
