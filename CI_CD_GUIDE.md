# CI/CD with Jenkins on Windows (Docker Desktop) — Step-by-Step Guide

**Your setup:** Windows + Docker Desktop + existing `jenkins` container (currently stopped)  
**Jenkins port:** `http://localhost:8082`  
**Problem found:** Container exited due to volume permission error → fixed in this guide

---

## What This Pipeline Does

```
You push code to GitHub
        ↓
Jenkins (Docker container on your PC) detects it via webhook or poll
        ↓
Stage 1 → Run pytest (backend tests, no real DB/LLM needed)
Stage 2 → npm run build (frontend)
Stage 3 → docker build backend image
Stage 4 → docker build frontend image
Stage 5 → docker push both images to Docker Hub
Stage 6 → SSH/deploy using docker-compose.prod.yml
```

---

## PART 1 — Fix and Start Jenkins

### Step 1.1 — Start Docker Desktop

Open **Docker Desktop** from Start Menu or system tray.  
Wait until the whale icon in the taskbar stops animating (takes ~30 seconds).

### Step 1.2 — Fix the Permission Problem and Restart Jenkins

Your existing container hit a volume permissions error. Run this in **PowerShell** (as normal user — Docker Desktop handles permissions):

```powershell
# Remove the broken container (keeps the jenkins_home volume — your data is safe)
docker rm jenkins

# Re-create it with the correct user flag that fixes the permission issue
docker run -d `
  --name jenkins `
  --restart=on-failure `
  -p 8082:8080 `
  -p 50000:50000 `
  -u root `
  -v jenkins_home:/var/jenkins_home `
  -v //var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts-jdk21
```

> **What changed:**  
> `-u root` — runs Jenkins as root inside the container, fixing the volume permission error.  
> `-v //var/run/docker.sock:/var/run/docker.sock` — lets Jenkins build Docker images using your host's Docker engine.

### Step 1.3 — Verify Jenkins is Running

```powershell
docker ps --filter "name=jenkins"
```

You should see `STATUS: Up`. Then open: **http://localhost:8082**

### Step 1.4 — Get the Initial Admin Password

```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy the printed password, paste it into the browser when Jenkins asks for it.

> If Jenkins was already set up before, you won't see this screen — just log in with your existing credentials.

### Step 1.5 — Complete the Setup Wizard

1. Click **"Install suggested plugins"** and wait
2. Create your admin user
3. Keep the URL as `http://localhost:8082`
4. Click **"Start using Jenkins"**

---

## PART 2 — Install Required Plugins

Go to **Manage Jenkins → Plugins → Available plugins**

Search and install each of these:

| Plugin | Why needed |
|--------|-----------|
| **Docker Pipeline** | `withDockerRegistry()` step in Jenkinsfile |
| **SSH Agent** | `sshagent()` step for deploying to server |
| **Pipeline** | Usually pre-installed |
| **Git** | Usually pre-installed |
| **JUnit** | Shows test results as charts |
| **Credentials Binding** | `credentials()` in Jenkinsfile |
| **Blue Ocean** | *(optional)* Better pipeline UI |

After installing, click **Restart Jenkins** when no jobs are running.

---

## PART 3 — Install Docker CLI Inside Jenkins Container

Jenkins needs to run `docker build` and `docker push`. We already mounted the Docker socket in Step 1.2 — now install the Docker CLI tools inside the container:

```powershell
# Open a shell inside the Jenkins container
docker exec -it jenkins bash

# Inside the container, run:
apt-get update
apt-get install -y docker.io
exit
```

Verify it works:

```powershell
docker exec jenkins docker version
```

You should see both Client and Server version info.

---

## PART 4 — Install Python and Node.js Inside Jenkins Container

The pipeline runs pytest and npm build — these tools must be inside the container:

```powershell
docker exec -it jenkins bash
```

Inside the container:

```bash
# Python 3.11
apt-get install -y python3.11 python3.11-venv python3-pip

# Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Verify
python3.11 --version
node --version
npm --version
exit
```

---

## PART 5 — Add Credentials in Jenkins

Go to **Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credential**

You need to add **5 credentials**. The IDs must match exactly what the Jenkinsfile expects:

---

### Credential 1 — Docker Hub Username

- Kind: **Secret text**
- ID: `DOCKER_HUB_USER`
- Secret: your Docker Hub username (e.g. `johndoe`)
- Description: Docker Hub username

---

### Credential 2 — Docker Hub Login

- Kind: **Username with password**
- ID: `dockerhub-credentials`
- Username: your Docker Hub username
- Password: your Docker Hub password (or an Access Token — recommended)

> To create a Docker Hub Access Token: hub.docker.com → Account Settings → Security → New Access Token

---

### Credential 3 — Deploy Host Address

- Kind: **Secret text**
- ID: `DEPLOY_HOST`
- Secret: `ubuntu@YOUR_SERVER_IP`  (e.g. `ubuntu@1.2.3.4`)
- Description: Production server SSH address

> If you are deploying locally for now, you can skip this and the deploy stage won't run on non-main branches anyway.

---

### Credential 4 — SSH Private Key for Deployment

- Kind: **SSH Username with private key**
- ID: `deploy-ssh-key`
- Username: `ubuntu`
- Private Key → Enter directly → paste contents of your SSH private key

> To generate a key pair if you don't have one:
> ```powershell
> ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\deploy_key
> # Then add deploy_key.pub to your server's ~/.ssh/authorized_keys
> ```

---

### Credential 5 — Backend .env File

- Kind: **Secret file**
- ID: `backend-env-file`
- File: click **Choose File** → upload your `backend/.env` file

> This is your real production .env with MySQL password, SECRET_KEY, SMTP settings etc.

---

## PART 6 — Push Your Code to GitHub

Jenkins needs to pull the code from somewhere. Push to GitHub if you haven't already:

```powershell
cd d:\RAG-RESUME

# If no remote set yet:
git remote add origin https://github.com/YOUR_USERNAME/RAG-RESUME.git

# Stage and commit everything
git add Jenkinsfile docker-compose.prod.yml CI_CD_GUIDE.md
git add frontend/Dockerfile frontend/nginx.conf frontend/.dockerignore
git add backend/pytest.ini backend/tests/ci.env

git commit -m "ci: add Jenkins pipeline and Docker production setup"
git push -u origin main
```

---

## PART 7 — Create the Jenkins Pipeline Job

1. Click **"New Item"** on the Jenkins dashboard
2. Enter name: `rag-resume-pipeline`
3. Select **"Pipeline"** → click **OK**
4. Under **"Build Triggers"** check:
   - **"Poll SCM"** and enter `H/5 * * * *` *(checks every 5 minutes)*
   - OR set up a webhook (see Part 8)
5. Under **"Pipeline"** section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/YOUR_USERNAME/RAG-RESUME.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. Click **Save**

---

## PART 8 — Set Up GitHub Webhook (Optional but Recommended)

This makes Jenkins build instantly when you push, instead of polling every 5 minutes.

**Problem:** Jenkins is on your local PC, not a public server. GitHub can't reach `localhost:8082`.  
**Solution:** Use **ngrok** to create a temporary public URL.

```powershell
# Install ngrok (if not installed)
winget install ngrok

# In a new PowerShell window, expose Jenkins
ngrok http 8082
```

ngrok will show a URL like `https://abc123.ngrok.io`. Use that for the webhook:

1. GitHub repo → **Settings → Webhooks → Add webhook**
2. Payload URL: `https://abc123.ngrok.io/github-webhook/`
3. Content type: `application/json`
4. Event: **Just the push event**
5. Click **Add webhook**

In Jenkins job settings → **Build Triggers** → check **"GitHub hook trigger for GITScm polling"**

> ngrok URL changes every restart on the free plan. For permanent local CI, skip the webhook and use Poll SCM instead.

---

## PART 9 — Run Your First Build

1. Go to the `rag-resume-pipeline` job
2. Click **"Build Now"**
3. Click the build number (e.g. `#1`) → **"Console Output"**

**What you'll see:**

```
[Stage: Checkout]
Cloning repository...

[Stage: Backend: Install & Test]
Creating virtual environment...
Installing requirements...
PASSED tests/test_text_utils.py
PASSED tests/test_chunking_service.py
... (72 tests)

[Stage: Frontend: Install & Build]
npm ci...
vite build...
dist/ created

[Stage: Docker: Build Images]   ← only on main branch
Building backend image...
Building frontend image...

[Stage: Docker: Push Images]
Pushing to Docker Hub...

[Stage: Deploy to Server]
SSH deploy...
```

---

## PART 10 — Verify the Build Worked

```powershell
# Check images appeared on Docker Hub (after build+push stage)
# Just go to: https://hub.docker.com/r/YOUR_USERNAME/rag-resume-backend

# Check test results in Jenkins
# Go to: http://localhost:8082 → rag-resume-pipeline → latest build → Test Results
```

---

## How the Pipeline Decides What to Run

| Branch | Tests | Docker Build | Docker Push | Deploy |
|--------|-------|-------------|-------------|--------|
| `feature/anything` | ✅ Yes | ❌ No | ❌ No | ❌ No |
| `develop` | ✅ Yes | ❌ No | ❌ No | ❌ No |
| `main` | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

So during development, pushing to feature branches only runs tests — no Docker noise.

---

## Troubleshooting

### Jenkins container won't start
```powershell
docker logs jenkins 2>&1 | Select-Object -Last 20
```
Most common cause: Docker Desktop not fully started yet. Wait 30 seconds and retry.

### "Got permission denied... docker.sock"
```powershell
docker exec -it jenkins bash
chmod 666 /var/run/docker.sock
exit
```

### "python3.11: command not found" in pipeline
Jenkins can't find Python. Either the install step in Part 4 wasn't done, or it installed as `python3`:
```powershell
docker exec jenkins which python3
docker exec jenkins python3 --version
```
If it's `python3` not `python3.11`, update the Jenkinsfile `python -m venv` line to `python3 -m venv`.

### Tests fail with "ModuleNotFoundError"
The backend venv install failed. Check the Console Output for the `pip install` step.

### Docker Hub push fails with auth error
Re-check Credential 2 (`dockerhub-credentials`) — username and password must be exact.

### ngrok URL expired (webhook stopped working)
Switch to **Poll SCM** in the job config or restart ngrok and update the webhook URL.

---

## Files Reference

```
RAG-RESUME/
├── Jenkinsfile                  ← Pipeline: 6 stages
├── docker-compose.prod.yml      ← Production: mysql + backend + frontend
├── CI_CD_GUIDE.md               ← This guide
│
├── frontend/
│   ├── Dockerfile               ← Node 20 build → Nginx 1.25 serve
│   ├── nginx.conf               ← SPA routing + /api proxy to backend
│   └── .dockerignore
│
└── backend/
    ├── pytest.ini               ← pytest config
    └── tests/
        └── ci.env               ← safe env vars for CI (no real DB/LLM)
```
