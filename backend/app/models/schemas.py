"""
Pydantic request/response schemas for all API routes.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, EmailStr


# --------------------------------------------------------------------------- #
#  Upload                                                                       #
# --------------------------------------------------------------------------- #

class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    chunk_count: int
    message: str = "Resume uploaded and indexed successfully."


# --------------------------------------------------------------------------- #
#  Chat                                                                         #
# --------------------------------------------------------------------------- #

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class SourceChunk(BaseModel):
    id: str
    text: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources_used: List[SourceChunk]


# --------------------------------------------------------------------------- #
#  Interview Questions                                                          #
# --------------------------------------------------------------------------- #

CategoryType = Literal["technical", "hr", "project", "behavioral"]


class InterviewQuestionsRequest(BaseModel):
    category: CategoryType = "technical"
    count: int = Field(default=5, ge=1, le=15)


class InterviewQuestionsResponse(BaseModel):
    category: str
    questions: List[str]


class AnswerQuestionRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)


class AnswerQuestionResponse(BaseModel):
    question: str
    answer: str
    sources_used: List[SourceChunk]


# --------------------------------------------------------------------------- #
#  ATS Suggestions                                                              #
# --------------------------------------------------------------------------- #

class ATSSuggestionsResponse(BaseModel):
    suggestions: str
    disclaimer: str = (
        "This is AI-generated feedback based on resume content analysis. "
        "It does not represent a score from any commercial ATS system."
    )


# --------------------------------------------------------------------------- #
#  Error (for OpenAPI docs)                                                     #
# --------------------------------------------------------------------------- #

class ErrorResponse(BaseModel):
    detail: str


# --------------------------------------------------------------------------- #
#  JD Matching                                                                  #
# --------------------------------------------------------------------------- #

class JDMatchRequest(BaseModel):
    jd_text: str = Field(..., min_length=50, max_length=8000,
                         description="Paste the full job description text here.")


class JDMatchResponse(BaseModel):
    match_id: str
    resume_id: str
    match_percentage: int
    matching_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]
    created_at: datetime


# --------------------------------------------------------------------------- #
#  Match History                                                                #
# --------------------------------------------------------------------------- #

class MatchHistoryItem(BaseModel):
    match_id: str
    jd_label: str           # first 60 chars of jd_text
    match_percentage: int
    created_at: datetime


class MatchHistoryResponse(BaseModel):
    resume_id: str
    total: int
    matches: List[MatchHistoryItem]


# --------------------------------------------------------------------------- #
#  Mock Interview Critique                                                      #
# --------------------------------------------------------------------------- #

class MockInterviewCritiqueRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    user_answer: str = Field(..., min_length=10, max_length=3000)


class MockInterviewCritiqueResponse(BaseModel):
    question: str
    rating: str
    strengths: List[str]
    improvements: List[str]
    sources_used: List[SourceChunk]

# --------------------------------------------------------------------------- #
#  Auth                                                                         #
# --------------------------------------------------------------------------- #

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class SignupResponse(BaseModel):
    message: str
    email: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: Optional[str]


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=100)


class ResendOTPRequest(BaseModel):
    email: EmailStr
    purpose: Literal["verify_email", "reset_password"] = "verify_email"


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str]
    is_verified: bool
    created_at: datetime
