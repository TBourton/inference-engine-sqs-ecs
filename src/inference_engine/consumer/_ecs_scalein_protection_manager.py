"""ECS Scale In Protection manager."""
import os
from typing import Optional

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

from ..exceptions import (
    ECSScaleInProtectionManagerAgentError,
    ECSScaleInProtectionManagerRequestError,
)


class ECSScaleInProtectionManager:
    """ECS Scale In Protection manager.

    https://docs.aws.amazon.com/AmazonECS/latest/userguide/task-scale-in-protection-endpoint.html  # noqa: E501

    The methods .acquire & .release can be used to acquire and release ECS
    Scale in protection. These should be called before & after processing
    a message.

    """

    def __init__(
        self,
        ecs_agent_uri: Optional[str] = None,
        expires_in_minutes: Optional[int] = 60,
        *,
        raise_for_req_error: bool = True,
        raise_for_agent_error: bool = True,
        request_timeout: float = 15,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """Get a new ECSScaleInProtectionManager.

        Parameters
        ----------
        ecs_agent_uri : str, optional
            URI of the ECS agent. In ECS Tasks, this is found at the
            ECS_AGENT_URI environment var.
            If None, then ECS_AGENT_URI env var is used instead.
        expires_in_minutes : int, optional
            Number of minutes of expiry to set the scale in protection for.
        raise_for_req_error : bool
            Whether to raise Requests errors.
        raise_for_agent_error : bool
            Whether to raise expceptions if errors are found in the agent
            responses.
        request_timeout : float
            The timeout used for the request.
        retries : int
            The number of times to retry API calls to the ECS agent.
        backoff_factor : float
            The backoff factor to use for retries.

        """
        self.ecs_agent_uri = ecs_agent_uri or os.environ["ECS_AGENT_URI"]
        self.uri = f"{self.ecs_agent_uri}/task-protection/v1/state"
        self.expires_in_minutes = expires_in_minutes
        self.raise_for_agent_error = raise_for_agent_error
        self.raise_for_req_error = raise_for_req_error
        self._session = requests.Session()
        self._retries = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )
        self._adapter = HTTPAdapter(max_retries=self._retries)
        self._session.mount("http://", self._adapter)
        self._session.mount("https://", self._adapter)
        self._timeout = request_timeout
        self.logger = logger.bind(
            ecs_agent_uri=self.ecs_agent_uri, uri=self.uri
        )

    def acquire(self) -> None:
        """Acquire ECS Protection."""
        self.logger.info("Acquiring ECS protection")
        self._set_state_wrapped(
            protection_enabled=True,
        )

    def release(self) -> None:
        """Release ECS Protection."""
        self.logger.info("Releasing ECS protection")
        self._set_state_wrapped(protection_enabled=False)

    def _set_state_wrapped(
        self,
        protection_enabled: bool,
    ) -> None:
        try:
            resp = self._set_state(protection_enabled)
        except ECSScaleInProtectionManagerRequestError as exp:
            self.logger.opt(exception=True).error(str(exp))
            if self.raise_for_req_error:
                raise
        except ECSScaleInProtectionManagerAgentError as exp:
            self.logger.opt(exception=True).error(str(exp))
            if self.raise_for_agent_error:
                raise
        else:
            self.logger.debug(
                "Set protection_enabled={} successfully {}",
                protection_enabled,
                resp,
            )

    def _set_state(
        self,
        protection_enabled: bool,
    ) -> dict:
        json: dict[str, int | bool] = {"ProtectionEnabled": protection_enabled}
        if protection_enabled and self.expires_in_minutes:
            json["ExpiresInMinutes"] = self.expires_in_minutes

        resp = self._session.put(self.uri, json=json, timeout=self._timeout)
        try:
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as exp:
            raise ECSScaleInProtectionManagerRequestError(
                f"Set status request failed, text={resp.text}, "
                f"status_code={resp.status_code}: {str(exp)}"
            ) from exp

        if "failure" in data:
            failure = data["failure"]
            raise ECSScaleInProtectionManagerAgentError(
                f"Set status agent {failure=}"
            )

        if "error" in data:
            error = data["error"]
            raise ECSScaleInProtectionManagerAgentError(
                f"Set status agent {error=}"
            )

        return data

    def __enter__(self):
        """Enter the context and acquire scale in protection."""
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and release scale in protection."""
        self.release()
        self._session.close()
