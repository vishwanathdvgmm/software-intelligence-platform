"""HTML and Markdown Parser for knowledge acquisition."""

from bs4 import BeautifulSoup

from sip.core.protocols.ingestion import Parser, RawArtifact

class HtmlParser(Parser):
    """Simple parser to extract text from HTML."""

    async def parse(self, artifact: RawArtifact) -> str:
        """Parse raw HTML content into plain text."""
        if not artifact.content_type.startswith("text/html"):
            # If it's not HTML, just decode as utf-8
            return artifact.content.decode("utf-8", errors="replace")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(artifact.content, "html.parser")

        # Remove scripts, styles, etc.
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)
        return text
