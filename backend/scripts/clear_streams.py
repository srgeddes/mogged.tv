"""Clear all stream records from the database.

Deletes from child tables first to respect FK constraints:
  stream_metrics → chat_messages → stream_participants → stream_invite_links → streams
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import delete, func, select

from core.database import async_session_factory, engine
from streams.models import (
    ChatMessage,
    Stream,
    StreamInviteLink,
    StreamMetrics,
    StreamParticipant,
)


async def clear_all_streams() -> None:
    tables = [
        ("stream_metrics", StreamMetrics),
        ("chat_messages", ChatMessage),
        ("stream_participants", StreamParticipant),
        ("stream_invite_links", StreamInviteLink),
        ("streams", Stream),
    ]

    async with async_session_factory() as session:
        for name, model in tables:
            count_result = await session.execute(select(func.count()).select_from(model))
            count = count_result.scalar_one()
            await session.execute(delete(model))
            print(f"  Deleted {count} rows from {name}")

        await session.commit()
        print("\nAll stream records cleared.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(clear_all_streams())
