# Step-by-Step Deployment Master Checklist

This guide provides a granular, click-by-click walkthrough to deploy the entire **AI Resume Analyzer & Interview Assistant** platform.

---

## Phase 0: Code Adjustments & Push to GitHub

Do these code adjustments on your local laptop **before** launching cloud services.

### 0.1 Update Frontend API Client (`frontend/src/api/client.js`)
Open `frontend/src/api/client.js` and ensure Axios uses `import.meta.env.VITE_API_BASE_URL`:
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
})

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
```

### 0.2 Update Backend Config & CORS Placeholder (`backend/app/main.py`)
In `backend/app/main.py`, make sure CORS allows origins (we will add the real Vercel URL later):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows initial connection, refined in Phase 4
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 0.3 Verify `.gitignore`
Open `.gitignore` at the project root and confirm the following lines exist:
```gitignore
backend/.env
frontend/.env
*.env
backend/data/
```

### 0.4 Push Code to GitHub
Run the following commands in your terminal:
```bash
git add .
git commit -m "Prepare for deployment: update client API base URL and gitignore"
git push origin main
```

---

## Phase 1: Deploy MySQL Database on Railway

### 1.1 Account Setup & Project Creation
1. Go to [railway.app](https://railway.app) and click **Login** (Sign in with GitHub).
2. On the Railway dashboard, click the **+ New Project** button.
3. Select **Provision MySQL** from the dropdown menu.
4. Railway will create a MySQL container inside your canvas (wait ~10 seconds until status turns green).

### 1.2 Get MySQL Connection String
1. Click on the **MySQL** service card in Railway.
2. Click on the **Variables** tab at the top.
3. Locate the variable named `MYSQL_URL` or `MYSQLPRIVATE_URL`.
   - *Alternative*: If shown as individual fields, construct the URL as:
     `mysql+pymysql://<MYSQLUSER>:<MYSQLPASSWORD>@<MYSQLHOST>:<MYSQLPORT>/<MYSQLDATABASE>`
4. **COPY THIS URL** to your clipboard or notepad.
   - *Example string*: `mysql+pymysql://root:wXyZ123@monorail.proxy.rlwy.net:34567/railway`

---

## Phase 2: Deploy Backend with Dockerfile on Render

### 2.1 Create Render Web Service
1. Go to [dashboard.render.com](https://dashboard.render.com) and log in.
2. Click **New +** (top right) -> Select **Web Service**.
3. Under **Connect a repository**, select your GitHub repository (`RAG-RESUME`).
4. Fill in the service configuration:
   - **Name**: `resume-rag-backend`
   - **Region**: Choose closest region (e.g., Singapore, Frankfurt, Oregon).
   - **Root Directory**: `backend`
   - **Runtime**: Select **Docker** (Render will automatically detect `backend/Dockerfile`).
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: `Free` (or starter plan).

### 2.2 Configure Render Environment Variables
Scroll down to the **Environment Variables** section on Render and click **Add Environment Variable** for each:

| Key | Value to Paste | Where to Get It |
| :--- | :--- | :--- |
| `MYSQL_URL` | `mysql+pymysql://root:wXyZ123@...` | Copied from Railway (Phase 1) |
| `SECRET_KEY` | `super-secret-jwt-key-99887766` | Generate any random string |
| `SMTP_HOST` | `smtp.gmail.com` | Standard Gmail SMTP server |
| `SMTP_PORT` | `587` | Standard TLS port |
| `SMTP_USER` | `your-email@gmail.com` | Your Gmail address |
| `SMTP_PASSWORD` | `xxxx xxxx xxxx xxxx` | Gmail App Password from Google Account |
| `SMTP_FROM` | `your-email@gmail.com` | Your Gmail address |
| `OLLAMA_URL` | `http://<your-remote-vps-ip>:11434` | Hosted remote Ollama IP/Domain |
| `CHROMA_PATH` | `/app/data/chroma` | Persistent disk vector directory |
| `UPLOAD_PATH` | `/app/data/uploads` | Persistent disk PDF upload directory |

### 2.3 Attach Persistent Volume Disk (For Uploads & ChromaDB Vectors)
1. On the left sidebar of your Render Web Service, click **Disks**.
2. Click **Add Disk**.
3. **Name**: `resume-data-disk`
4. **Mount Path**: `/app/data`
5. **Size**: `1 GB`
6. Click **Save Changes**.

### 2.4 Deploy Backend & Copy Live Backend URL
1. Click **Create Web Service** (or **Deploy**).
2. Wait 2-4 minutes while Render executes `Dockerfile` (`apt-get install gcc`, `pip install`, Uvicorn startup).
3. Check deployment logs until you see:
   `[INFO] === Backend ready ===`
4. At the top left under your service name, copy your **Live Backend URL**.
   - *Example live URL*: `https://resume-rag-backend.onrender.com`

---

## Phase 3: Deploy Frontend on Vercel

### 3.1 Import Project into Vercel
1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. On your dashboard, click **Add New...** -> **Project**.
3. Find your GitHub repository (`RAG-RESUME`) and click **Import**.

### 3.2 Configure Vercel Project Settings
1. **Framework Preset**: Select **Vite**.
2. **Root Directory**: Click **Edit** -> Select `frontend` folder -> Click **Continue**.
3. Expand **Build and Output Settings**:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.3 Set Vercel Environment Variable
Expand **Environment Variables** section:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://resume-rag-backend.onrender.com` (Pasted from Render in Phase 2)

### 3.4 Deploy Frontend
1. Click **Deploy**.
2. Vercel will build your React application (~1 minute).
3. Once complete, copy your **Live Vercel Frontend URL**.
   - *Example live URL*: `https://resume-rag-frontend.vercel.app`

---

## Phase 4: Close the Loop (CORS Security & Live Verification)

### 4.1 Update Backend CORS Security
1. Go back to your local code `backend/app/main.py`.
2. Update `allow_origins`:
   ```python
   allow_origins=[
       "https://resume-rag-frontend.vercel.app",  # Your real live Vercel URL
       "http://localhost:5173",
   ]
   ```
3. Commit and push to GitHub:
   ```bash
   git add backend/app/main.py
   git commit -m "Update CORS allow_origins with live Vercel domain"
   git push origin main
   ```
4. Render will automatically detect the push and redeploy your backend.

---

## Phase 5: End-to-End Live Verification Checklist

Open your live Vercel website URL (`https://resume-rag-frontend.vercel.app`) in your browser and test:

1. **Signup**: Create a new account with a real email address.
2. **Verify OTP**: Check your real email inbox for the 6-digit verification code sent via Gmail SMTP. Enter the code.
3. **Login**: Log in with your email and password.
4. **Resume Upload**: Upload a PDF resume. Verify the upload completes and parses text.
5. **RAG Chat**: Open the chat module and ask questions about the resume.
6. **ATS Feedback & Mock Interview**: Generate ATS scores and practice mock interview questions.
