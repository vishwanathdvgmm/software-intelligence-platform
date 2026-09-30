"""HTTP Fetcher for knowledge acquisition."""

import httpx

from sip.core.protocols.ingestion import Fetcher, RawArtifact


class HttpxFetcher(Fetcher):
    """Fetcher implementation using httpx for HTTP requests."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            follow_redirects=True,
            headers={
                "User-Agent": "SIP-Crawler/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

    async def fetch(self, url: str) -> RawArtifact:
        """Fetch a single URL.

        Args:
            url: The URL to fetch.

        Returns:
            A RawArtifact containing the response data.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = await self._client.get(url)
        response.raise_for_status()

        # Simple RawArtifact implementation
        class HttpArtifact(RawArtifact):
            def __init__(self, res: httpx.Response) -> None:
                self.url = str(res.url)
                self.content = res.content
                self.content_type = res.headers.get("Content-Type", "application/octet-stream")
                self.status_code = res.status_code

        return HttpArtifact(response)

    async def close(self) -> None:
        """Close the underlying client."""
        await self._client.aclose()
