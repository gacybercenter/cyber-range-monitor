import time
from dataclasses import dataclass

import user_agents
from fastapi import Request, Response

from range_monitor import constant


@dataclass(slots=True)
class UserAgent:
    browser: str
    os: str
    device: str
    is_bot: bool
    raw_header: str | None

    def __repr__(self) -> str:
        return (
            f'UserAgent(browser={self.browser}, os={self.os}, '
            f'device={self.device}, is_bot={self.is_bot})'
        )

    def string(self) -> str:
        return self.raw_header or ''


@dataclass(slots=True)
class RequestRecord:
    """
    Records metadata about an incoming HTTP request and represents
    the structured log record for it.
    """

    id: str
    ip_address: str
    user_agent: UserAgent
    method: str
    url: str


@dataclass(slots=True)
class ResponseRecord:
    """
    Records metadata about an outgoing HTTP response and represents
    the structured log record for it.
    """

    status_code: int
    elapsed: float
    okay: bool
    headers: dict[str, str]


class RequestAuditor:
    @staticmethod
    def get_request_path(request: Request) -> str:
        """
        Extracts the path from the request URL.

        Parameters
        ----------
        request : Request

        Returns
        -------
        str
            The path of the request URL.
        """
        return (
            request.url.path
            if not request.url.query
            else request.url.path + '/' + request.url.query
        )

    @staticmethod
    def get_request_ip(request: Request) -> str:
        """
        Extracts the client's IP address from the request.

        Parameters
        ----------
        request : Request
        request_header : str | None, optional
            _if none uses X-Forwarded-For_, by default None

        Returns
        -------
        str
        """

        x_forwarded_for = request.headers.get(constant.REQUEST_IP_HEADER_NAME)
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.client.host  # type: ignore

        return ip

    @staticmethod
    def collect_user_agent(request: Request) -> UserAgent:
        """
        Collects and parses the User-Agent header from the request.

        Parameters
        ----------
        request : Request

        Returns
        -------
        UserAgent
        """
        ua_string = request.headers.get('User-Agent')
        ua = user_agents.parse(ua_string)
        return UserAgent(
            browser=f'{ua.browser.family} {ua.browser.version_string}',
            os=f'{ua.os.family} {ua.os.version_string}',
            device=f'{ua.device.family} {ua.device.brand} {ua.device.model}',
            is_bot=ua.is_bot,
            raw_header=ua_string,
        )

    @staticmethod
    def parse_request(request: Request) -> RequestRecord:
        """
        Audits an incoming request and extracts relevant metadata.

        Parameters
        ----------
        request : Request
            _description_
        ip_addr_header : str | None, optional
            _The name of the IP Address header_, by default None
        request_id_header : str | None, optional
            _The name of the request id header_, by default None

        Returns
        -------
        RequestRecord
        """

        ip_address = RequestAuditor.get_request_ip(request)
        user_agent = RequestAuditor.collect_user_agent(request)
        request_id = request.headers.get(constant.REQUEST_ID_HEADER_NAME) or 'unknown'
        return RequestRecord(
            id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            method=request.method,
            url=str(request.url),
        )

    @staticmethod
    def parse_response(
        *,
        response: Response,
        req_start: float,
    ) -> ResponseRecord:
        elapsed = time.perf_counter() - req_start
        return ResponseRecord(
            status_code=response.status_code,
            headers=dict(response.headers),
            elapsed=elapsed,
            okay=response.status_code < 400,
        )
