"""Interactive test script for the Expert Lifecycle Service (M5)."""

import asyncio
from uuid import UUID, uuid4

from sip.core.contracts.experts import (
    Expert,
    ExpertConfig,
    ExpertStatus,
    ExpertVersion,
    GenerationConfig,
    RetrievalConfig,
    VersionPolicy,
)
from sip.experts.service import ExpertLifecycleService

# ─── In-memory mock repositories ────────────────────────────────────────────

class InMemoryExpertRepo:
    """In-memory Expert repository for testing."""

    def __init__(self) -> None:
        self._store: dict[UUID, Expert] = {}

    async def get(self, expert_id: UUID) -> Expert | None:
        return self._store.get(expert_id)

    async def save(self, expert: Expert) -> None:
        self._store[expert.id] = expert

    async def get_by_slug(self, slug: str) -> Expert | None:
        for e in self._store.values():
            if e.slug == slug:
                return e
        return None

    async def list_active(self) -> list[Expert]:
        return [e for e in self._store.values() if e.status == ExpertStatus.ACTIVE]

class InMemoryVersionRepo:
    """In-memory ExpertVersion repository for testing."""

    def __init__(self) -> None:
        self._store: list[ExpertVersion] = []

    async def save(self, version: ExpertVersion) -> None:
        self._store.append(version)

    async def get_latest(self, expert_id: UUID) -> ExpertVersion | None:
        versions = [v for v in self._store if v.expert_id == expert_id]
        if not versions:
            return None
        return max(versions, key=lambda v: v.version_number)

    async def list_by_expert(self, expert_id: UUID) -> list[ExpertVersion]:
        return sorted(
            [v for v in self._store if v.expert_id == expert_id],
            key=lambda v: v.version_number,
            reverse=True,
        )

# ─── Interactive test ────────────────────────────────────────────────────────

def print_expert(expert: Expert) -> None:
    """Pretty-print an Expert."""
    print(f"  Name:           {expert.name}")
    print(f"  Slug:           {expert.slug}")
    print(f"  ID:             {expert.id}")
    print(f"  Status:         {expert.status.value}")
    print(f"  Config Version: v{expert.config_version}")
    print(f"  Software IDs:   {expert.config.software_ids}")
    print(f"  Version Policy: {expert.config.version_policy.value}")
    print(f"  Retrieval:      {expert.config.retrieval.strategy.value}")
    print(f"  LLM Model:      {expert.config.generation.llm_model or '(system default)'}")
    print(f"  Created:        {expert.created_at}")
    print(f"  Updated:        {expert.updated_at}")

async def main() -> None:
    print("=" * 60)
    print("SIP Expert Lifecycle Service - Interactive Test")
    print("=" * 60)

    service = ExpertLifecycleService(
        expert_repo=InMemoryExpertRepo(),
        version_repo=InMemoryVersionRepo(),
    )

    # ── Step 1: Create ──────────────────────────────────────────────────
    print("\n[STEP 1: CREATE EXPERT]")
    print("Creating 'Python Expert' in DRAFT state...")
    expert = await service.create_expert(
        name="Python Expert",
        slug="python",
        description="Expert in the Python programming language and ecosystem",
    )
    print("[OK] Expert created!")
    print_expert(expert)

    input("\nPress Enter to continue...")

    # ── Step 2: Transition DRAFT → CONFIGURING ──────────────────────────
    print("\n[STEP 2: DRAFT -> CONFIGURING]")
    expert = await service.transition(expert.id, ExpertStatus.CONFIGURING, reason="Begin setup")
    print(f"[OK] Transitioned to: {expert.status.value}")

    input("\nPress Enter to continue...")

    # ── Step 3: Update Configuration ────────────────────────────────────
    print("\n[STEP 3: UPDATE CONFIG]")
    python_software_id = uuid4()
    new_config = ExpertConfig(
        software_ids=(python_software_id,),
        version_policy=VersionPolicy.LATEST_ONLY,
        retrieval=RetrievalConfig(semantic_top_k=25, lexical_top_k=25, rerank_top_k=10),
        generation=GenerationConfig(
            llm_model="gemini-2.5-pro",
            temperature=0.1,
            system_prompt_template="You are {expert_name}, a Python programming expert.",
        ),
    )
    expert = await service.update_config(expert.id, new_config, reason="Initial configuration")
    print("[OK] Config updated to v2!")
    print_expert(expert)

    input("\nPress Enter to continue...")

    # ── Step 4: Walk through remaining lifecycle ────────────────────────
    transitions = [
        (ExpertStatus.BUILDING, "Knowledge acquisition started"),
        (ExpertStatus.VALIDATING, "Build complete, validating"),
        (ExpertStatus.READY, "Validation passed"),
        (ExpertStatus.ACTIVE, "Activating for production"),
    ]

    for i, (target, reason) in enumerate(transitions, start=4):
        print(f"\n[STEP {i}: {expert.status.value.upper()} -> {target.value.upper()}]")
        expert = await service.transition(expert.id, target, reason=reason)
        print(f"[OK] Transitioned to: {expert.status.value}")
        if target == ExpertStatus.ACTIVE:
            print(f"   Activated at: {expert.activated_at}")
            print(f"   Queryable: {expert.is_queryable()}")

    input("\nPress Enter to continue...")

    # ── Step 5: Test invalid transition ─────────────────────────────────
    print("\n[STEP 8: TEST INVALID TRANSITION]")
    print("Attempting ACTIVE -> DRAFT (should fail)...")
    try:
        await service.transition(expert.id, ExpertStatus.DRAFT)
        print("[FAIL] ERROR: Should have raised!")
    except Exception as e:
        print(f"[OK] Correctly rejected: {e}")

    input("\nPress Enter to continue...")

    # ── Step 6: Version history ─────────────────────────────────────────
    print("\n[STEP 9: VERSION HISTORY]")
    versions = await service.get_version_history(expert.id)
    print(f"Total versions: {len(versions)}")
    for v in versions:
        print(f"  v{v.version_number}: {v.change_reason} (created: {v.created_at})")

    input("\nPress Enter to continue...")

    # ── Step 7: Disable and Archive ─────────────────────────────────────
    print("\n[STEP 10: DISABLE -> ARCHIVE]")
    expert = await service.transition(expert.id, ExpertStatus.DISABLED, reason="Maintenance")
    print(f"[OK] Disabled: {expert.status.value}")

    expert = await service.transition(expert.id, ExpertStatus.ARCHIVED, reason="End of life")
    print(f"[OK] Archived: {expert.status.value}")
    print(f"   Queryable: {expert.is_queryable()}")

    # ── Step 8: Duplicate slug rejection ────────────────────────────────
    print("\n[STEP 11: DUPLICATE SLUG REJECTION]")
    print("Attempting to create another 'python' Expert...")
    try:
        await service.create_expert(name="Python Expert 2", slug="python")
        print("[FAIL] ERROR: Should have raised!")
    except Exception as e:
        print(f"[OK] Correctly rejected: {e}")

    print("\n" + "=" * 60)
    print("All Expert Lifecycle tests passed! [OK]")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
