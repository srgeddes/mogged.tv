"""Seed trivia categories and questions.

Usage: cd backend && make seed-trivia
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import json

import httpx
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_session_factory

from .constants import BRAIN_ROT_CATEGORIES, OPENTDB_CATEGORIES
from .models import Difficulty, QuestionSource, TriviaCategory, TriviaQuestion

OPENTDB_BASE = "https://opentdb.com/api.php"
OPENTDB_TOKEN_URL = "https://opentdb.com/api_token.php"
OPENTDB_COUNT_URL = "https://opentdb.com/api_count.php"
RATE_LIMIT_DELAY = 6.0
MAX_PER_REQUEST = 50


# ---------------------------------------------------------------------------
# Brain rot question bank
# ---------------------------------------------------------------------------
BRAIN_ROT_QUESTIONS: list[dict] = [
    # --- Slang & Vibes ---
    {
        "category": "slang-vibes",
        "question": "What does 'no cap' mean?",
        "correct": "No lie / for real",
        "incorrect": ["No hat allowed", "Stop talking", "No limit"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "If someone says you're 'mogging' them, what are you doing?",
        "correct": "Outshining them in looks or presence",
        "incorrect": ["Ignoring them", "Copying them", "Blocking them online"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'sus' mean?",
        "correct": "Suspicious or questionable",
        "incorrect": ["Super cool", "Sustainable", "A type of sushi"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'slay' mean in internet slang?",
        "correct": "To do something exceptionally well",
        "incorrect": ["To destroy something", "To sleep late", "To leave quickly"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What is a 'rizz' in internet slang?",
        "correct": "Charisma or charm, especially in flirting",
        "incorrect": ["A type of dance", "A card game", "A hairstyle"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'mid' mean?",
        "correct": "Average or mediocre",
        "incorrect": ["The middle of something", "Really good", "A midday nap"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'bussin' mean?",
        "correct": "Really good, especially food",
        "incorrect": ["Riding a bus", "Being busy", "Running fast"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does it mean to 'catch an L'?",
        "correct": "To take a loss or fail at something",
        "incorrect": ["To catch a train", "To win big", "To find a letter"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'bet' mean as a response?",
        "correct": "Okay / sounds good / agreement",
        "incorrect": ["I want to gamble", "I disagree", "I'm confused"],
        "difficulty": "easy",
    },
    {
        "category": "slang-vibes",
        "question": "What is 'aura' in internet slang?",
        "correct": "Your overall vibe or energy people perceive",
        "incorrect": ["A music genre", "A type of headache", "A weather pattern"],
        "difficulty": "medium",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'sigma' refer to in internet culture?",
        "correct": "A lone-wolf, self-reliant personality archetype",
        "incorrect": [
            "A math equation",
            "A fraternity ranking",
            "A type of camera lens",
        ],
        "difficulty": "medium",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'delulu' mean?",
        "correct": "Delusional",
        "incorrect": ["Delightful", "Sleepy", "Confused about directions"],
        "difficulty": "medium",
    },
    {
        "category": "slang-vibes",
        "question": "What does 'ate' mean when someone says 'she ate that'?",
        "correct": "She did an amazing job",
        "incorrect": ["She had a big meal", "She was hungry", "She left early"],
        "difficulty": "medium",
    },
    # --- Meme History ---
    {
        "category": "meme-history",
        "question": "What year did 'Doge' (the Shiba Inu meme) go viral?",
        "correct": "2013",
        "incorrect": ["2010", "2015", "2018"],
        "difficulty": "medium",
    },
    {
        "category": "meme-history",
        "question": "Which platform did Rickrolling originate on?",
        "correct": "4chan",
        "incorrect": ["YouTube", "Reddit", "MySpace"],
        "difficulty": "medium",
    },
    {
        "category": "meme-history",
        "question": "What is the name of the cat in the 'Woman Yelling at a Cat' meme?",
        "correct": "Smudge",
        "incorrect": ["Grumpy", "Whiskers", "Nyan"],
        "difficulty": "hard",
    },
    {
        "category": "meme-history",
        "question": "'This is fine' meme features a dog sitting in what?",
        "correct": "A room on fire",
        "incorrect": ["A bathtub", "A pile of snow", "An office cubicle"],
        "difficulty": "easy",
    },
    {
        "category": "meme-history",
        "question": "What animal is Harambe?",
        "correct": "A gorilla",
        "incorrect": ["A lion", "A chimpanzee", "An elephant"],
        "difficulty": "easy",
    },
    {
        "category": "meme-history",
        "question": "The 'Distracted Boyfriend' meme originated from what?",
        "correct": "A stock photo",
        "incorrect": ["A movie scene", "A TV show", "A music video"],
        "difficulty": "medium",
    },
    {
        "category": "meme-history",
        "question": "What does the 'Galaxy Brain' meme represent?",
        "correct": "Increasingly absurd or 'enlightened' ideas",
        "incorrect": [
            "Intelligence levels",
            "Space exploration",
            "A video game power-up",
        ],
        "difficulty": "medium",
    },
    {
        "category": "meme-history",
        "question": "What was the original 'Loss' meme from?",
        "correct": "Ctrl+Alt+Del webcomic",
        "incorrect": ["XKCD", "The Oatmeal", "Penny Arcade"],
        "difficulty": "hard",
    },
    {
        "category": "meme-history",
        "question": "What year did the 'Ice Bucket Challenge' go viral?",
        "correct": "2014",
        "incorrect": ["2012", "2016", "2013"],
        "difficulty": "medium",
    },
    {
        "category": "meme-history",
        "question": "The 'Stonks' meme features a mannequin in front of what?",
        "correct": "A stock market graph going up",
        "incorrect": ["A pile of money", "A bank vault", "A calculator"],
        "difficulty": "easy",
    },
    {
        "category": "meme-history",
        "question": "What was the name of the viral dress color debate in 2015?",
        "correct": "The Dress (blue/black vs white/gold)",
        "incorrect": ["The Shoe", "The Hat", "The Jacket"],
        "difficulty": "easy",
    },
    {
        "category": "meme-history",
        "question": "Who is 'Hide the Pain Harold'?",
        "correct": "András Arató, a Hungarian engineer turned stock photo model",
        "incorrect": [
            "A fictional character",
            "An American actor",
            "A British comedian",
        ],
        "difficulty": "hard",
    },
    # --- Creator Lore ---
    {
        "category": "creator-lore",
        "question": "What was MrBeast's first video to hit 1 million views about?",
        "correct": "Counting to 100,000",
        "incorrect": [
            "Giving away money",
            "A Minecraft challenge",
            "Opening a restaurant",
        ],
        "difficulty": "medium",
    },
    {
        "category": "creator-lore",
        "question": "What is PewDiePie's real first name?",
        "correct": "Felix",
        "incorrect": ["Karl", "Johan", "Erik"],
        "difficulty": "easy",
    },
    {
        "category": "creator-lore",
        "question": "What game made Ninja famous on Twitch?",
        "correct": "Fortnite",
        "incorrect": ["Minecraft", "League of Legends", "Call of Duty"],
        "difficulty": "easy",
    },
    {
        "category": "creator-lore",
        "question": "KSI and Logan Paul created which energy drink brand?",
        "correct": "Prime",
        "incorrect": ["G Fuel", "Celsius", "Ghost"],
        "difficulty": "easy",
    },
    {
        "category": "creator-lore",
        "question": "What does the 'Dream SMP' stand for?",
        "correct": "Survival Multiplayer (a Minecraft server)",
        "incorrect": [
            "Social Media Platform",
            "Strategic Mission Plan",
            "Super Mega Party",
        ],
        "difficulty": "medium",
    },
    {
        "category": "creator-lore",
        "question": "Which YouTuber is known for the phrase 'That's just a theory'?",
        "correct": "MatPat (Game Theory)",
        "incorrect": ["Vsauce", "Mark Rober", "Veritasium"],
        "difficulty": "medium",
    },
    {
        "category": "creator-lore",
        "question": "What was Markiplier's original career path before YouTube?",
        "correct": "Biomedical engineering",
        "incorrect": ["Computer science", "Film production", "Nursing"],
        "difficulty": "hard",
    },
    {
        "category": "creator-lore",
        "question": "IShowSpeed went viral for screaming about which soccer player?",
        "correct": "Cristiano Ronaldo",
        "incorrect": ["Lionel Messi", "Neymar Jr.", "Kylian Mbappé"],
        "difficulty": "easy",
    },
    {
        "category": "creator-lore",
        "question": "What type of content did Kai Cenat become famous for?",
        "correct": "Twitch streaming and marathon subathons",
        "incorrect": [
            "Cooking tutorials",
            "Tech reviews",
            "Music production",
        ],
        "difficulty": "easy",
    },
    {
        "category": "creator-lore",
        "question": "Which creator started the 'Sidemen' group?",
        "correct": "KSI",
        "incorrect": ["Miniminter", "Vikkstar123", "TBJZL"],
        "difficulty": "medium",
    },
    {
        "category": "creator-lore",
        "question": "What year did YouTube first launch?",
        "correct": "2005",
        "incorrect": ["2003", "2007", "2006"],
        "difficulty": "medium",
    },
    {
        "category": "creator-lore",
        "question": "What was the first video ever uploaded to YouTube?",
        "correct": "Me at the zoo",
        "incorrect": [
            "Charlie Bit My Finger",
            "Evolution of Dance",
            "Lazy Sunday",
        ],
        "difficulty": "hard",
    },
    # --- Internet Moments ---
    {
        "category": "internet-moments",
        "question": "What was the most-liked photo on Instagram before the egg?",
        "correct": "Kylie Jenner's baby announcement",
        "incorrect": [
            "Beyoncé's pregnancy photo",
            "A sunset photo",
            "Cristiano Ronaldo's selfie",
        ],
        "difficulty": "hard",
    },
    {
        "category": "internet-moments",
        "question": "What crashed the internet in 2014 with a selfie at the Oscars?",
        "correct": "Ellen DeGeneres' group selfie",
        "incorrect": [
            "Kim Kardashian's selfie",
            "Obama's victory tweet",
            "A Beyoncé performance",
        ],
        "difficulty": "medium",
    },
    {
        "category": "internet-moments",
        "question": "What game caused massive server crashes when it launched in 2016?",
        "correct": "Pokémon GO",
        "incorrect": ["Fortnite", "Among Us", "Clash Royale"],
        "difficulty": "easy",
    },
    {
        "category": "internet-moments",
        "question": "GameStop stock (GME) surged in 2021 due to which subreddit?",
        "correct": "r/WallStreetBets",
        "incorrect": ["r/stocks", "r/investing", "r/cryptocurrency"],
        "difficulty": "easy",
    },
    {
        "category": "internet-moments",
        "question": (
            "What was the name of the AI chatbot that Microsoft released"
            " and quickly took down in 2016?"
        ),
        "correct": "Tay",
        "incorrect": ["Cortana", "Zo", "Clippy"],
        "difficulty": "hard",
    },
    {
        "category": "internet-moments",
        "question": "Which social media platform was originally called 'Musically'?",
        "correct": "TikTok",
        "incorrect": ["Instagram Reels", "Snapchat", "Vine"],
        "difficulty": "easy",
    },
    {
        "category": "internet-moments",
        "question": "The 'Fyre Festival' disaster happened on which island?",
        "correct": "Great Exuma, Bahamas",
        "incorrect": ["Ibiza, Spain", "Bali, Indonesia", "Fiji"],
        "difficulty": "hard",
    },
    {
        "category": "internet-moments",
        "question": "What was Twitter's character limit when it first launched?",
        "correct": "140 characters",
        "incorrect": ["160 characters", "120 characters", "280 characters"],
        "difficulty": "medium",
    },
    {
        "category": "internet-moments",
        "question": (
            "Which streaming platform shut down in 2023 after being a major Twitch competitor?"
        ),
        "correct": "Mixer",
        "incorrect": ["DLive", "Caffeine", "Trovo"],
        "difficulty": "hard",
    },
    {
        "category": "internet-moments",
        "question": "What NFT collection sold for $69 million at Christie's in 2021?",
        "correct": "Beeple's 'Everydays: The First 5000 Days'",
        "incorrect": [
            "CryptoPunks",
            "Bored Ape Yacht Club",
            "World of Women",
        ],
        "difficulty": "hard",
    },
    {
        "category": "internet-moments",
        "question": "What app caused a global panic when it was almost banned in the US in 2020?",
        "correct": "TikTok",
        "incorrect": ["WeChat", "Huawei AppGallery", "Telegram"],
        "difficulty": "easy",
    },
    {
        "category": "internet-moments",
        "question": (
            "Which platform's outage in October 2021 took down Facebook,"
            " Instagram, and WhatsApp for 6 hours?"
        ),
        "correct": "Meta (Facebook)",
        "incorrect": ["Amazon AWS", "Google Cloud", "Cloudflare"],
        "difficulty": "medium",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _question_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]


async def _seed_categories(session: AsyncSession) -> dict[str, TriviaCategory]:
    """Create or update all trivia categories. Returns slug->category map."""
    categories: dict[str, TriviaCategory] = {}

    # Standard OpenTDB categories
    for _cat_id, (name, slug, icon) in OPENTDB_CATEGORIES.items():
        stmt = pg_insert(TriviaCategory).values(
            name=name, slug=slug, icon=icon, is_brain_rot=False, question_count=0
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={"name": name, "icon": icon},
        )
        await session.execute(stmt)

    # Brain rot categories
    for name, slug, icon in BRAIN_ROT_CATEGORIES:
        stmt = pg_insert(TriviaCategory).values(
            name=name, slug=slug, icon=icon, is_brain_rot=True, question_count=0
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={"name": name, "icon": icon},
        )
        await session.execute(stmt)

    await session.flush()

    # Reload all categories
    result = await session.execute(select(TriviaCategory))
    for cat in result.scalars().all():
        categories[cat.slug] = cat

    return categories


async def _get_session_token(client: httpx.AsyncClient) -> str:
    """Get an OpenTDB session token to avoid duplicate questions."""
    resp = await client.get(OPENTDB_TOKEN_URL, params={"command": "request"})
    data = resp.json()
    return data["token"]


async def _get_category_counts(client: httpx.AsyncClient, category_id: int) -> dict[str, int]:
    """Get available question counts per difficulty for a category."""
    resp = await client.get(OPENTDB_COUNT_URL, params={"category": category_id})
    data = resp.json()
    counts = data.get("category_question_count", {})
    return {
        "easy": counts.get("total_easy_question_count", 0),
        "medium": counts.get("total_medium_question_count", 0),
        "hard": counts.get("total_hard_question_count", 0),
    }


async def _fetch_opentdb_batch(
    client: httpx.AsyncClient,
    category_id: int,
    difficulty: str,
    amount: int,
    token: str,
) -> list[dict]:
    """Fetch a batch of questions from OpenTDB."""
    params = {
        "amount": min(amount, MAX_PER_REQUEST),
        "category": category_id,
        "difficulty": difficulty,
        "type": "multiple",
        "token": token,
    }
    resp = await client.get(OPENTDB_BASE, params=params)
    data = resp.json()
    code = data.get("response_code")
    # 0 = success, 4 = token exhausted (no more unique questions)
    if code not in (0, 4):
        print(f"    ⚠ OpenTDB code {code} for cat={category_id} diff={difficulty}")
    if code != 0:
        return []
    return data.get("results", [])


async def _seed_opentdb(
    session: AsyncSession,
    categories: dict[str, TriviaCategory],
) -> int:
    """Fetch ALL available questions from OpenTDB (~4000+)."""
    total = 0
    difficulties = ["easy", "medium", "hard"]
    request_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        token = await _get_session_token(client)
        print(f"  Got session token: {token[:12]}...")

        for cat_id, (_name, slug, _icon) in OPENTDB_CATEGORIES.items():
            category = categories.get(slug)
            if category is None:
                continue

            counts = await _get_category_counts(client, cat_id)
            await asyncio.sleep(1)

            for diff in difficulties:
                available = counts.get(diff, 0)
                if available == 0:
                    continue

                fetched = 0
                print(f"  {slug} / {diff} — {available} available")

                while fetched < available:
                    batch_size = min(MAX_PER_REQUEST, available - fetched)
                    # Rate limit
                    if request_count > 0:
                        await asyncio.sleep(RATE_LIMIT_DELAY)

                    questions = await _fetch_opentdb_batch(client, cat_id, diff, batch_size, token)
                    request_count += 1

                    if not questions:
                        break  # No more unique questions

                    for q in questions:
                        text = html.unescape(q["question"])
                        correct = html.unescape(q["correct_answer"])
                        incorrect = [html.unescape(a) for a in q["incorrect_answers"]]
                        ext_id = _question_hash(text)
                        diff_enum = Difficulty(diff)

                        stmt = pg_insert(TriviaQuestion).values(
                            category_id=category.id,
                            question_text=text,
                            correct_answer=correct,
                            incorrect_answers=json.dumps(incorrect),
                            difficulty=diff_enum,
                            source=QuestionSource.OPENTDB,
                            external_id=ext_id,
                            is_active=True,
                        )
                        stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])
                        result = await session.execute(stmt)
                        if result.rowcount:
                            total += 1

                    fetched += len(questions)
                    print(f"    Fetched {fetched}/{available} ({total} new total)")

    await session.flush()
    return total


async def _seed_brain_rot(
    session: AsyncSession,
    categories: dict[str, TriviaCategory],
) -> int:
    """Insert hardcoded brain rot questions."""
    total = 0

    for q in BRAIN_ROT_QUESTIONS:
        category = categories.get(q["category"])
        if category is None:
            print(f"  ⚠ Unknown brain rot category: {q['category']}")
            continue

        ext_id = _question_hash(q["question"])
        diff_enum = Difficulty(q["difficulty"])

        stmt = pg_insert(TriviaQuestion).values(
            category_id=category.id,
            question_text=q["question"],
            correct_answer=q["correct"],
            incorrect_answers=json.dumps(q["incorrect"]),
            difficulty=diff_enum,
            source=QuestionSource.CUSTOM,
            external_id=ext_id,
            is_active=True,
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])
        result = await session.execute(stmt)
        if result.rowcount:
            total += 1

    await session.flush()
    return total


async def _update_question_counts(
    session: AsyncSession,
    categories: dict[str, TriviaCategory],
) -> None:
    """Update question_count on each category."""
    from sqlalchemy import func as sa_func

    for _slug, category in categories.items():
        count_stmt = (
            select(sa_func.count())
            .select_from(TriviaQuestion)
            .where(
                TriviaQuestion.category_id == category.id,
                TriviaQuestion.is_active.is_(True),
            )
        )
        result = await session.execute(count_stmt)
        count = result.scalar_one()

        await session.execute(
            update(TriviaCategory)
            .where(TriviaCategory.id == category.id)
            .values(question_count=count)
        )

    await session.flush()


async def seed() -> None:
    """Main seed entrypoint."""
    print("🎯 Seeding trivia data...")

    async with async_session_factory() as session:
        # 1. Categories
        print("\n📂 Creating categories...")
        categories = await _seed_categories(session)
        print(f"  ✓ {len(categories)} categories")

        # 2. OpenTDB questions
        print("\n🌐 Fetching OpenTDB questions (this takes ~3.5 min)...")
        opentdb_count = await _seed_opentdb(session, categories)
        print(f"  ✓ {opentdb_count} OpenTDB questions inserted")

        # 3. Brain rot questions
        print("\n🧠 Inserting brain rot questions...")
        brain_rot_count = await _seed_brain_rot(session, categories)
        print(f"  ✓ {brain_rot_count} brain rot questions inserted")

        # 4. Update counts
        print("\n📊 Updating category question counts...")
        await _update_question_counts(session, categories)

        await session.commit()
        print("\n✅ Trivia seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
