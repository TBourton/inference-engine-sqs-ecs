"""Fast API wrapper for Consumer.

The app contains routes to probe the consumer state:
    * /ready - indicates if the consumer is running and consuming messages
    * /health - indicates if the consumer is healthy
    * /busy - indicates if the consumer is currently processing a message

"""
from contextlib import asynccontextmanager

import fastapi
from fastapi import status
from fastapi.exceptions import HTTPException

from .. import __version__
from .consumer import Consumer, ConsumerAlreadyConsumingError, ConsumerError


def get_app(consumer: Consumer, **kwargs) -> fastapi.FastAPI:
    """Get a FastAPI app wrapper for this Consumer.

    The app contains routes to probe the consumer state:
     * /ready - indicates if the consumer is running and consuming messages
     * /health - indicates if the consumer is healthy
     * /busy - indicates if the consumer is currently processing a message

    Parameters
    ----------
    consumer : Consumer
        The Consumer instance to wrap.
    kwargs : Any
        Addditional kwargs passed onto fastapi.FastAPI

    Returns
    -------
    fastapi.FastAPI
        The FastAPI wrapper api.

    """

    @asynccontextmanager
    async def lifespan(_: fastapi.FastAPI):
        try:
            consumer.start_consuming()
        except ConsumerAlreadyConsumingError:
            pass

        yield
        consumer.stop_consuming()

    _kws = {"title": "Consumer", "version": __version__}
    _kws.update(kwargs)
    app = fastapi.FastAPI(lifespan=lifespan, **_kws)

    router = get_router(consumer)
    app.include_router(router)
    return app


def get_router(consumer: Consumer) -> fastapi.APIRouter:
    """Get a FastAPI router wrapping this Consumer.

    Parameters
    ----------
    consumer : Consumer
        The Consumer instance to wrap.

    Returns
    -------
    fastapi.APIRouter
        The FastAPI router.

    """
    router = fastapi.APIRouter()

    def _raise_for_not_running() -> None:
        if not consumer.is_running:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Consumer is not running",
            )

    def _raise_for_queue_ping_fail() -> None:
        try:
            consumer.ping_queue()
        except Exception as exp:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Queue can't be reached: {exp}",
            ) from exp

    def _raise_for_is_processing_message() -> None:
        try:
            _isprocessing = consumer.is_processing_message
        except ConsumerError as exp:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Consumer error: {exp}",
            ) from exp

        if _isprocessing:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Consumer is already processing a message",
            )

    @router.get("/busy", status_code=status.HTTP_200_OK)
    def busy():
        """Determine if the Consumer is busy."""
        _raise_for_is_processing_message()
        return {"status": "ready"}

    @router.get("/ready", status_code=status.HTTP_200_OK)
    def ready():
        """Determine if the Consumer is ready."""
        _raise_for_not_running()
        _raise_for_queue_ping_fail()
        return {"status": "ready"}

    @router.get("/health", status_code=status.HTTP_200_OK)
    def health():
        """Determine if the Consumer is healthy."""
        _raise_for_not_running()
        return {"status": "healthy"}

    return router
