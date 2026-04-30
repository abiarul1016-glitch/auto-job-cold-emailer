# auto-job-cold-emailer

**THE method for spray and pray.**

<!-- **automated cold emailing, minus the tedium.** -->

---

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![Ollama](https://img.shields.io/badge/Ollama-fff?style=for-the-badge&logo=ollama&logoColor=000)](#)
[![Qwen](https://custom-icon-badges.demolab.com/badge/Qwen-605CEC?style=for-the-badge&logo=qwen&logoColor=fff)](#)
[![Playwright](https://custom-icon-badges.demolab.com/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=fff)](#)
[![aiosmtplib](https://img.shields.io/badge/aiosmtplib-fff?style=for-the-badge&logo=smtp&logoColor=00527B)](#)

---

## What is it?

Job hunting means cold emailing dozens — sometimes hundreds — of companies. The process is repetitive, tedious, and time-consuming: research each company, write a personalized pitch, craft a subject line, and hit send. Rinse and repeat.

**auto-job-cold-emailer** automates all of that.

Define your target companies, and the agent handles the rest: navigating to their websites, extracting relevant information, generating personalized email content via a local LLM, and sending tailored outreach emails through your Gmail account — all in a single interactive session.

## Features

- **Interactive AI Agent** — Conversational CLI where you tell the agent what to do, and it autonomously uses tools to navigate pages, extract text, click buttons, and send emails
- **Local LLM Personalization** — Runs on-device AI models (Qwen via Ollama) to generate unique, company-specific email content tailored to each target
- **Browser Automation** — Built-in Playwright-based browser agent to scrape company information from websites and extract relevant details
- **Duplicate Prevention** — Tracks sent emails in `sent_emails.json` to avoid spamming the same company across multiple outreach runs
- **Dual Email Templates** — Both plain text and HTML email versions with professional formatting and a branded signature block
- **Configurable Model Selection** — Switch between different Ollama models (e.g., `qwen3.5:0.8b` for speed, `qwen3.6:35b-a3b-coding-nvfp4` for quality)
- **Click Actions** — Optional browser clicking functionality to interact with buttons and elements on web pages

## How it works

**auto-job-cold-emailer** operates as an interactive, multi-stage pipeline, moving from data extraction to live email delivery with minimal human intervention.

1. **Agent Initialization** — The system launches an interactive CLI loop powered by a local LLM (Qwen via Ollama). The agent is equipped with browser tools and an email-sending tool.
2. **User Input** — You type commands into the CLI. The agent parses your request and decides which tools to use.
3. **Browser Automation** — The agent uses Playwright to navigate to URLs, extract visible text from pages, and optionally click buttons.
4. **Email Generation & Sending** — When you request a cold email, the agent generates personalized content using the LLM, checks `sent_emails.json` for duplicates, and sends the email via `aiosmtplib` (Gmail SMTP).
5. **State Persistence** — Browser authentication state is saved to `playwright/.auth/state.json` for session reuse. Sent emails are logged to `sent_emails.json`.

### Flow Diagram

```
User (CLI)
          │
          ▼
WebAgent (ollama LLM)
          │
          ├──► BrowserManager (Playwright)
          │            ├── navigate_to_url()
          │            ├── extract_text_from_page()
          │            └── click_button_with_text()
          │
          └──► send_cold_email()
                  ├── Personalizes email body
                  ├── Checks sent_emails.json for duplicates
                  └── Sends via aiosmtplib (Gmail SMTP)
```

## Tech stack

**auto-job-cold-emailer** is a local-first, Python-driven automation tool.

| Layer                  | Technology    | Purpose                                            |
| :--------------------- | :------------ | :------------------------------------------------- |
| **Core Language**      | Python 3.12+  | Orchestration, data handling, and async execution  |
| **Local AI/LLM**       | Ollama (Qwen) | Generates personalized email content and reasoning |
| **Browser Automation** | Playwright    | Navigates pages, extracts text, clicks buttons     |
| **Email Sending**      | aiosmtplib    | Async SMTP email delivery via Gmail                |
| **Environment**        | python-dotenv | Manages credentials and configuration              |

## Running locally

### Prerequisites

- **Python 3.12+**
- **Ollama** — Install from [ollama.com](https://ollama.com) and pull a model (e.g., `qwen3.5` or `qwen3.6:35b-a3b-coding-nvfp4`):
  ```bash
  ollama pull qwen3.5
  ```
- **Gmail Account** — With 2-Step Verification enabled (for App Password generation)

### Setup

1. **Install Dependencies:**

   ```bash
   uv pip install -r pyproject.toml
   ```

2. **Install Playwright Browsers:**

   ```bash
   playwright install chromium
   ```

3. **Configure Environment Variables:**
   Edit `secrets.env` with your Gmail credentials:

   ```env
   USER_EMAIL=your-email@gmail.com
   APP_PASSWORD=your-gmail-app-password
   ```

   > **Get a Gmail App Password:**
   >
   > 1. Go to [Google Account Security](https://myaccount.google.com/security)
   > 2. Enable 2-Step Verification
   > 3. Search "App Passwords" in Google Account settings
   > 4. Generate a new app password for "Mail"
   > 5. Paste it into `secrets.env`

4. **Configure Browser State (Optional):**
   If you have an existing Playwright authentication state, place it at `playwright/.auth/state.json`. Otherwise, the agent will create a fresh browser context on first run.

5. **Run the Agent:**

   ```bash
   uv run cold-email-agent.py
   ```

   You'll be prompted with:

   ```
   What should I do? (quit to exit):
   ```

   Example interactions:

   ```
   What should I do? (quit to exit): Go to google.com and tell me what you see
   What should I do? (quit to exit): Send a cold email to careers@google.com
   What should I do? (quit to exit): quit
   ```

## Configuration

### Model Selection

Edit `AVAILABLE_MODELS` in `cold-email-agent.py` to choose your Ollama model:

```python
AVAILABLE_MODELS = {
         "qwen3.5": "qwen3.5:0.8b",
         "qwen3.6": "qwen3.6:35b-a3b-coding-nvfp4",
}
SELECTED_MODEL = AVAILABLE_MODELS.get("qwen3.6")
```

### Click Actions

Enable/disable browser clicking functionality:

```python
CLICK = True     # Set to False to disable click_button_with_text tool
```

### Sent Email Tracking

Emails already sent are stored in `sent_emails.json`. The agent checks this before sending to prevent duplicate outreach.

## Notes

- **Browser state** is saved to `playwright/.auth/state.json`. Keep this file secure as it contains authentication cookies.
- **Sent emails** are tracked in `sent_emails.json`. The agent checks this file before sending to avoid spamming the same company.
- The script runs in **headed mode** (`headless=False`) by default so you can monitor browser activity visually. Set `headless=True` in `cold-email-agent.py` for unattended runs.
- **Never commit `secrets.env`** — It contains your email credentials. Add it to `.gitignore`.
- Use a **Gmail App Password**, not your main password, for SMTP authentication.

## What's next

- [ ] Add support for multiple email templates (e.g., internship, full-time, freelance)
- [ ] Integrate with job boards (LinkedIn, Indeed) to auto-discover target companies
- [ ] Add email reply tracking and response categorization
- [ ] Support for additional SMTP providers (Outlook, Yahoo, custom domains)
- [ ] Dashboard for monitoring outreach history and response rates
- [ ] Scheduled runs via cron or systemd timer

---

<div align="center">

Cold emails, warm results. 💌

_Built for those who'd rather code than write cover letters._

</div>
