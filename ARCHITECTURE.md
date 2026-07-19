# AI Resume Analyzer & Interview Assistant — Architecture v3.0

**Backend: Complete ✅ | Auth: Complete ✅ | Frontend: Next**
**Tests: 20/20 auth + 52/52 unit = 72 total passing**

---

## QUICK START

```bash
# Start server
cd D:\RAG-RESUME\backend
..\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# API docs
http://localhost:8000/docs
```

---

## ALL ENDPOINTS

### Auth (no token needed)
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/auth/signup` | Register — sends OTP to email |
| POST | `/api/auth/verify-email` | Verify email with OTP |
| POST | `/api/auth/resend-otp` | Resend OTP |
| POST | `/api/auth/login` | Login → returns JWT |
| POST | `/api/auth/forgot-password` | Send reset OTP |
| POST | `/api/auth/reset-password` | Set new password with OTP |
| GET  | `/api/auth/me` | Get own profile 🔒 |

### Resume Features (all require `Authorization: Bearer <token>`)
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/resumes` | Upload + index PDF |
| POST | `/api/resumes/{id}/chat` | Q&A grounded in resume |
| POST | `/api/resumes/{id}/interview-questions` | Generate interview questions |
| POST | `/api/resumes/{id}/interview-questions/answer` | First-person sample answer |
| POST | `/api/resumes/{id}/ats-suggestions` | ATS improvement feedback |
| POST | `/api/resumes/{id}/jd-match` | Match against job description |
| GET  | `/api/resumes/{id}/matches` | JD match history |
| POST | `/api/resumes/{id}/mock-interview/critique` | Grade your practice answer |
| GET  | `/health` | Server health |

---

## AUTH FLOW (how it works end-to-end)

```
1. POST /api/auth/signup  {email, password, full_name}
   → hashes password with bcrypt
   → creates User row (is_verified=False)
   → generates 6-digit OTP (valid 10 min), stores in otp_codes table
   → sends OTP via SMTP email (or logs it in dev mode if SMTP not configured)
   → returns 201

2. POST /api/auth/verify-email  {email, otp}
   → looks up unused, unexpired OTP for this user + purpose=verify_email
   → marks OTP used, sets user.is_verified=True
   → returns 200

3. POST /api/auth/login  {email, password}
   → rejects if user doesn't exist or password wrong → 401
   → rejects if not verified → 403
   → creates JWT signed with SECRET_KEY, expiry 24h
   → returns {access_token, user_id, email, full_name}

4. Every protected route:
   → reads Authorization: Bearer <token> header
   → decodes JWT → extracts user_id
   → loads User from DB, injects as current_user
   → all queries use WHERE user_id = current_user.id
   → one user can NEVER access another user's resumes

5. POST /api/auth/forgot-password  {email}
   → creates OTP (purpose=reset_password), sends email
   → always returns same message (prevents email enumeration)

6. POST /api/auth/reset-password  {email, otp, new_password}
   → verifies OTP → hashes new password → saves
```

---

## RAG PIPELINE FLOW

```
Upload:
  PDF bytes → validate → extract text (PyMuPDF) → clean_text()
           → chunk_text() [200-word sliding window, section-aware]
           → embed_texts() [all-MiniLM-L6-v2, 384-dim vectors]
           → ChromaDB.store() [collection "resume-{uuid}"]
           → MySQL INSERT resumes(id, user_id, filename, full_text)

Query (Chat / Interview / JD Match / Critique):
  user query → embed_query() → ChromaDB.query(top_k=5)
             → prompt_builder(chunks + query)
             → OllamaProvider.generate() [llama3:8b via localhost:11434]
             → strip_llm_preamble() → return to client

ATS:
  MySQL SELECT full_text → build_ats_prompt(text[:4000])
  → OllamaProvider.generate() → return suggestions
  (uses full text, not retrieval — needs whole doc)
```

---

## FILE STRUCTURE

```
backend/
├── .env                           ← secrets (never commit)
├── .env.example                   ← template
├── requirements.txt
├── Dockerfile
│
└── app/
    ├── main.py                    ← FastAPI app, lifespan, CORS, all handlers
    ├── config.py                  ← Pydantic Settings (reads .env)
    │
    ├── models/
    │   ├── db.py                  ← 5 ORM tables: users, otp_codes, resumes,
    │   │                             job_descriptions, matches
    │   └── schemas.py             ← All Pydantic request/response models
    │
    ├── core/
    │   ├── exceptions.py          ← 12 domain exceptions
    │   ├── errors.py              ← FastAPI handlers → HTTP codes
    │   └── dependencies.py        ← get_current_user (JWT → User)
    │
    ├── utils/
    │   └── text_utils.py          ← clean_text, strip_llm_preamble, parse_llm_json
    │
    ├── services/
    │   ├── auth_service.py        ← bcrypt, JWT, OTP, SMTP email
    │   ├── pdf_service.py         ← validate, extract, save
    │   ├── chunking_service.py    ← section-aware 200-word chunker
    │   ├── embedding_service.py   ← MiniLM singleton
    │   ├── vectorstore_service.py ← ChromaDB (one collection per resume)
    │   ├── retrieval_service.py   ← embed query → search → top-k chunks
    │   ├── ats_service.py         ← read full_text from MySQL
    │   └── llm/
    │       ├── base.py            ← abstract LLMProvider
    │       ├── ollama_provider.py ← Ollama /api/generate
    │       └── provider.py        ← singleton: llm = OllamaProvider()
    │
    ├── prompts/
    │   ├── chat_prompt.py
    │   ├── interview_prompt.py
    │   ├── answer_prompt.py
    │   ├── ats_prompt.py
    │   ├── jd_match_prompt.py
    │   └── mock_interview_critique_prompt.py
    │
    └── api/routes/
        ├── auth.py                ← signup, verify, login, forgot, reset, me
        ├── upload.py              ← POST /api/resumes
        ├── chat.py                ← POST /api/resumes/{id}/chat
        ├── interview.py           ← questions + answer
        ├── ats.py                 ← ats-suggestions
        ├── jd_match.py            ← jd-match + matches history
        └── mock_interview.py      ← critique

tests/
├── conftest.py                    ← shared app/client/make_resume/make_db
├── test_api_chat.py
├── test_chunking_service.py
├── test_jd_match.py
├── test_mock_interview.py
├── test_pdf_service.py
└── test_text_utils.py
```

---

## DATABASE TABLES

```
users
  id, email (unique), hashed_password, full_name, is_verified, created_at

otp_codes
  id, user_id (FK→users), code, purpose, expires_at, used, created_at

resumes
  id, user_id (FK→users), filename, full_text, uploaded_at

job_descriptions
  id, resume_id (FK→resumes), user_id, jd_text, created_at

matches
  id, resume_id (FK→resumes), user_id, job_description_id,
  match_percentage, matching_skills (JSON), missing_skills (JSON),
  suggestions (JSON), created_at
```

---

## SECURITY MODEL

- Passwords: bcrypt (cost factor 12, salted per-password)
- Tokens: HS256 JWT, 24-hour expiry, `sub` = user_id
- OTPs: 6-digit random, 10-minute expiry, single-use, invalidated on new request
- All resume routes: `WHERE user_id = current_user.id` — cross-user access impossible
- Forgot password: identical response whether email exists or not (no enumeration)
- No raw stack traces ever reach the client

---

## EMAIL / OTP IN DEV MODE

If `SMTP_USER` / `SMTP_PASSWORD` are blank in `.env`, the OTP is **logged to the server console** instead of emailed. Look for:

```
WARNING app.services.auth_service: [DEV MODE] No SMTP configured. OTP for user@email.com (verify_email): 123456
```

For production, set up Gmail App Password:
1. Enable 2FA on your Google account
2. Go to `myaccount.google.com/apppasswords`
3. Generate a password for "Mail"
4. Set `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` in `.env`

---

## HOW TO USE FROM POSTMAN

```
1. POST /api/auth/signup        body: {email, password, full_name}
2. Check server log for OTP (dev) or email (prod)
3. POST /api/auth/verify-email  body: {email, otp}
4. POST /api/auth/login         body: {email, password}
   → copy access_token from response

5. Set header on all further requests:
   Authorization: Bearer <access_token>

6. POST /api/resumes            form-data, file = your PDF
   → copy resume_id

7. POST /api/resumes/{resume_id}/chat
   body: {"question": "What skills does this candidate have?"}
```

---

## SWAP LLM (one file change)

```python
# backend/app/services/llm/provider.py — change ONE line:
from app.services.llm.openai_provider import OpenAIProvider
llm = OpenAIProvider()
# Zero changes to any route, prompt, or service.
```
