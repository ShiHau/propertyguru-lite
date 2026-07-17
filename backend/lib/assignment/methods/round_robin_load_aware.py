from typing import TYPE_CHECKING
import redis
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from backend.lib.assignment.factory import AgentLoad

# Initialize the Redis client (adjust host/port according to your settings)
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Central Redis key to track the last assigned agent globally across all strategy runs
REDIS_LAST_ASSIGNED_KEY = "assignment:last_assigned_agent_id"


def _next_round_robin_id(candidate_ids: list[int]) -> int | None:
    if not candidate_ids:
        return None

    sorted_candidates = sorted(candidate_ids)

    last_assigned_raw = redis_client.get(REDIS_LAST_ASSIGNED_KEY)
    last_assigned_id = int(last_assigned_raw) if last_assigned_raw else None

    if last_assigned_id is None or last_assigned_id not in sorted_candidates:
        next_agent_id = sorted_candidates[0]
    else:
        current_index = sorted_candidates.index(last_assigned_id)
        next_index = (current_index + 1) % len(sorted_candidates)
        next_agent_id = sorted_candidates[next_index]

    redis_client.set(REDIS_LAST_ASSIGNED_KEY, next_agent_id)
    return next_agent_id


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
            return _next_round_robin_id(candidate_ids)

        # Once balanced, continue standard round robin among all active agents.
        all_agent_ids = [agent.agent_id for agent in agent_loads]
        return _next_round_robin_id(all_agent_ids)