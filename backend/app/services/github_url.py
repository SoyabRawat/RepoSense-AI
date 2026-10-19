"""GitHub URL validation, sanitization, and SSRF prevention."""

import re
from urllib.parse import urlparse
from typing import Tuple


class InvalidRepositoryURLError(ValueError):
    """Raised when repository URL is malformed or violates security policies."""
    pass


# Strict regex for valid GitHub owner and repository names
# GitHub username: alphanumeric and single hyphens, 1-39 chars, cannot start/end with hyphen
# GitHub repo: alphanumeric, hyphens, underscores, dots, 1-100 chars
OWNER_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
REPO_NAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{1,100}$")

BLOCKED_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "169.254.169.254",  # AWS/GCP metadata
    "metadata.google.internal",
    "instance-data",
}


def parse_and_validate_github_url(raw_url: str) -> Tuple[str, str, str]:
    """
    Validate, sanitize, and extract owner, repository name, and canonical URL from user input.

    Returns:
        (owner, repo, canonical_url)

    Raises:
        InvalidRepositoryURLError if validation fails.
    """
    if not raw_url or not isinstance(raw_url, str):
        raise InvalidRepositoryURLError("Repository URL must be a non-empty string.")

    cleaned_url = raw_url.strip()

    # Reject URLs with leading/trailing control characters or whitespace
    if any(ord(c) < 32 or ord(c) == 127 for c in cleaned_url):
        raise InvalidRepositoryURLError("URL contains invalid control characters.")

    # Parse URL
    try:
        parsed = urlparse(cleaned_url)
    except Exception as exc:
        raise InvalidRepositoryURLError(f"Malformed URL structure: {exc}")

    # Enforce HTTPS scheme
    if parsed.scheme.lower() not in ("https", "http"):
        raise InvalidRepositoryURLError(
            f"Unsupported URL scheme '{parsed.scheme}'. Only 'https://' is supported."
        )

    # Reject credentials in URL
    if parsed.username or parsed.password:
        raise InvalidRepositoryURLError("URLs with embedded authentication credentials are not permitted.")

    # Validate Hostname
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise InvalidRepositoryURLError("URL must contain a valid hostname.")

    # SSRF & Private host protection
    if hostname in BLOCKED_HOSTNAMES or hostname.startswith("127.") or hostname.startswith("10.") or hostname.startswith("192.168."):
        raise InvalidRepositoryURLError("Access to private, loopback, or metadata addresses is strictly forbidden.")

    # Exact hostname validation: must be github.com or www.github.com
    if hostname not in ("github.com", "www.github.com"):
        raise InvalidRepositoryURLError(
            f"Invalid repository host '{hostname}'. Only public 'github.com' repositories are supported."
        )

    # Reject non-standard ports
    if parsed.port and parsed.port not in (80, 443):
        raise InvalidRepositoryURLError(f"Non-standard port '{parsed.port}' is not permitted.")

    # Extract path parts
    path = parsed.path.strip("/")
    parts = [p for p in path.split("/") if p]

    if len(parts) < 2:
        raise InvalidRepositoryURLError(
            "GitHub URL must specify both owner and repository (e.g., https://github.com/owner/repository)."
        )

    owner = parts[0].strip()
    repo = parts[1].strip()

    # Strip .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Validate owner and repo syntax
    if not OWNER_REGEX.match(owner):
        raise InvalidRepositoryURLError(
            f"Invalid GitHub owner name '{owner}'. Must contain only alphanumeric characters and non-repeating hyphens."
        )

    if not REPO_NAME_REGEX.match(repo) or repo in (".", ".."):
        raise InvalidRepositoryURLError(
            f"Invalid GitHub repository name '{repo}'."
        )

    canonical_url = f"https://github.com/{owner}/{repo}"
    return owner, repo, canonical_url
