import asyncio
import uuid
from pathlib import Path

import redis.asyncio as aioredis
from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from core.settings import settings
from db import sessionmanager
from models import Embedding, EmbeddingJob, File, JobStatus
from services.embeding_service import chunk_text, create_embedding
from services.file_service import download_file_from_supabase
from utils.extractor import DocumentExtractor
from utils.helper import with_temp_file
from utils.logger import get_logger

logger = get_logger()

_MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL_PATH = Path("models") / _MODEL_NAME


def load_model() -> SentenceTransformer:
    if _MODEL_PATH.exists():
        logger.info("Loading embedding model from disk")
        return SentenceTransformer(str(_MODEL_PATH))
    logger.info("Downloading embedding model from HuggingFace")
    model = SentenceTransformer(_MODEL_NAME)
    model.save(str(_MODEL_PATH))
    return model


async def recover_stuck_jobs(redis) -> None:
    """On startup, re-queue any jobs stuck in 'processing' state from a previous crash."""
    session = sessionmanager.session_factory
    if not session:
        raise ValueError("DB Session isnt initialized")

    async with session() as db:
        from sqlalchemy import select

        result = await db.execute(
            select(EmbeddingJob).where(EmbeddingJob.status == JobStatus.Processing)
        )
        stuck_jobs = result.scalars().all()
        for job in stuck_jobs:
            logger.warning("Recovering stuck job", extra={"file_id": str(job.file_id)})
            job.status = JobStatus.Pending
            await redis.lpush("embedding_jobs", str(job.file_id))
        await db.commit()
        logger.info("Recovered stuck jobs", extra={"len": len(stuck_jobs)})


async def process_jobs(model: SentenceTransformer, redis) -> None:
    logger.info("Worker started, waiting for jobs...")
    session_factory = sessionmanager.session_factory
    if session_factory is None:
        raise ValueError("DB Session isnt initialized")

    while True:
        try:
            _, file_id_bytes = await redis.brpop("embedding_jobs")
            file_id = uuid.UUID(file_id_bytes.decode())
            logger.info("Received job", extra={"file_id": str(file_id)})

            async with session_factory() as db:
                result = await db.execute(
                    select(EmbeddingJob).where(EmbeddingJob.file_id == file_id)
                )
                job = result.scalar_one_or_none()
                if not job:
                    logger.error("Job not found in DB", extra={"file_id": str(file_id)})
                    continue

                job.status = JobStatus.Processing
                await db.commit()

                try:
                    file_result = await db.execute(
                        select(File).where(File.id == file_id)
                    )
                    db_file = file_result.scalar_one_or_none()
                    if not db_file:
                        raise ValueError(f"File {file_id} not found in DB")

                    contents, suffix = await download_file_from_supabase(
                        settings.SUPABASE_BUCKET, db_file.filepath
                    )

                    async def process_file(tmp_path: str):
                        extractor = DocumentExtractor(tmp_path)
                        text = extractor.extract()
                        chunks = chunk_text(text)
                        embeddings = create_embedding(model, chunks)
                        for chunk, embedding in zip(chunks, embeddings):
                            db.add(
                                Embedding(
                                    file_id=file_id,
                                    chunks=chunk,
                                    embedding=embedding,
                                )
                            )
                        await db.commit()

                    await with_temp_file(contents, suffix, process_file)

                    job.status = JobStatus.Done
                    await db.commit()
                    logger.info("Job completed", extra={"file_id": str(file_id)})

                except Exception as e:
                    job.status = JobStatus.Failed
                    await db.commit()
                    logger.exception(
                        "Job failed", extra={"file_id": str(file_id), "error": str(e)}
                    )

        except Exception as e:
            logger.exception("Worker loop error", extra={"error": str(e)})
            await asyncio.sleep(2)


async def main():
    sessionmanager.init_db()
    redis = await aioredis.from_url(settings.REDIS_URL)

    try:
        model = load_model()
        await recover_stuck_jobs(redis)
        await process_jobs(model, redis)
    finally:
        await redis.close()
        await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(main())
