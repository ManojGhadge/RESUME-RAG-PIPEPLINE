"""
Domain-level exceptions. Routes catch these and return the right HTTP status.
Never let raw stack traces reach the client.
"""


class PDFExtractionError(Exception):
    """Raised when PyMuPDF can't extract text (likely a scanned PDF)."""
    pass


class ResumeNotFoundError(Exception):
    """Raised when a resume_id doesn't exist in MySQL or Chroma."""
    pass


class NoChunksFoundError(Exception):
    """Raised when Chroma returns zero chunks for a query — never call LLM with empty context."""
    pass


class LLMError(Exception):
    """Raised when Ollama returns an error or is unreachable."""
    pass


class InvalidFileTypeError(Exception):
    """Raised when the uploaded file is not a PDF."""
    pass


class FileTooLargeError(Exception):
    """Raised when the uploaded file exceeds MAX_PDF_SIZE."""
    pass


class LLMParseError(Exception):
    """Raised when the LLM returns non-JSON where JSON is required (JD match, critique)."""
    pass


class JDNotFoundError(Exception):
    """Raised when a job_description_id doesn't exist in MySQL."""
    pass


class AuthError(Exception):
    """Raised for invalid credentials, expired tokens, etc."""
    pass


class UserAlreadyExistsError(Exception):
    """Raised when signup uses an already-registered email."""
    pass


class UserNotVerifiedError(Exception):
    """Raised when a non-verified user tries to log in."""
    pass


class InvalidOTPError(Exception):
    """Raised when OTP is wrong, expired, or already used."""
    pass
