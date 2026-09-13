import asyncio
import os
import sys
from typing import Optional
from loguru import logger

from memory.session_store import redis_store
from agents.orchestrator import orchestrator

class ScrapeWorker:
    """
    H-05 Durable Scrape Queue Worker:
    Continuously processes queued scrape tasks from Redis.
    Ensures scraping jobs survive container restarts and deployments.
    """
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the worker polling loop."""
        if self._running:
            return
        self._running = True
        logger.info("Starting ScrapeWorker polling loop...")
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Signals the worker loop to stop gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("ScrapeWorker stopped.")

    async def _run_loop(self):
        while self._running:
            try:
                job = await redis_store.dequeue_scrape_job(timeout=2)
                if not job:
                    await asyncio.sleep(0.5)
                    continue

                job_id = job.get("job_id")
                target_url = job.get("target_url")
                extraction_goal = job.get("extraction_goal")
                owner_id = job.get("owner_id")

                if (
                    not isinstance(job_id, str)
                    or not isinstance(target_url, str)
                    or not isinstance(extraction_goal, str)
                    or not isinstance(owner_id, str)
                ):
                    logger.warning(f"[Worker] Skipping invalid job payload: {job}")
                    continue

                logger.info(f"[Worker] Processing job {job_id} for {target_url}")
                await redis_store.update_job_status(job_id, status="running")

                try:
                    result = await orchestrator.execute_pipeline(
                        user_request=extraction_goal,
                        target_url=target_url,
                        session_id=job_id,
                        owner_id=owner_id
                    )
                    status = "done" if result.get("status") == "success" else "failed"
                    await redis_store.update_job_status(
                        job_id=job_id,
                        status=status,
                        result=result
                    )
                    logger.info(f"[Worker] Job {job_id} finished with status: {status}")
                except Exception as ex:
                    logger.error(f"[Worker] Job {job_id} failed during execution: {ex}", exc_info=True)
                    await redis_store.update_job_status(
                        job_id=job_id,
                        status="failed",
                        error=str(ex) or "Internal extraction error"
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Worker] Unhandled error in ScrapeWorker loop: {e}", exc_info=True)
                await asyncio.sleep(2)

scrape_worker = ScrapeWorker()

if __name__ == "__main__":
    async def main():
        print("Starting standalone ScrapeWorker...")
        await scrape_worker.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await scrape_worker.stop()

    asyncio.run(main())
