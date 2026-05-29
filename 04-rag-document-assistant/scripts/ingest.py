import argparse
import asyncio

from api.app.database import init_db
from api.app.ingestion import ingest_document


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a Markdown, text, or PDF document.")
    parser.add_argument("path", help="Path to the document to ingest.")
    parser.add_argument("--title", default=None)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    init_db()
    result = await ingest_document(path=args.path, title=args.title)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
