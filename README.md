# Job Applier Bot

This project automates the process of applying to jobs on LinkedIn, retrieving OTP codes from Gmail when prompted for login verification.

---

## Demo
[Demo](https://photos.app.goo.gl/bqUgFW34bbf9paT5A)

---

## Prerequisites

* Python 3.10+
* A Google Cloud Project with the Gmail API enabled
* LinkedIn account credentials
* A Gmail account connected to LinkedIn (for OTP retrieval)

---

## Setup Instructions

### 1. Enable Gmail API on Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services > Library**.
4. Search for **Gmail API** and enable it.

---

### 2. Create OAuth Client ID Credentials

1. In the Google Cloud Console, go to **APIs & Services > Credentials**.
2. Click **Create Credentials** → **OAuth client ID**.
3. Choose **Desktop application** as the application type.
4. Download the credentials file. Save it as **`credentials.json`** in the root of this project.

---

### 3. Add Test User to OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**.
2. Set the app type to **External** (if not already configured).
3. Under **Test users**, add the Gmail address that will be used to log in to LinkedIn.
4. Save the configuration.
5. Run the file gmail_service.py using the command `uv run gmail_service.py` and authenticate once with the gmail account.

---

### 4. Environment Variables

Create a `.env` file in the project root with the following content:

```bash
GEMINI_API_KEY=your_gemini_api_key
USER_EMAIL=your_linkedin_email@gmail.com
USER_PASSWORD=your_linkedin_password
```

* `USER_EMAIL`: The Gmail address used for LinkedIn login.
* `USER_PASSWORD`: The password for your LinkedIn account.

---

### 5. Install Dependencies

Run the following command to install all required libraries in one go:

```bash
uv pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv pydantic browser-use
```

---

### 6. Running the Bot

```bash
uv run test.py
```

On the first run, a browser window will open asking you to authenticate your Gmail account. Once authenticated, a `token.json` file will be created and reused for future runs.

---
