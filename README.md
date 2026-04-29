# auto-job-cold-emailer

<!-- THE method for spray and pray. -->

An AI-powered automation tool that personalizes and sends cold emails to companies for job applications — eliminating the tedious manual work of cold outreach.

## Overview

This project automates the process of cold emailing for job hunting. It leverages a local AI model (via Ollama) to generate personalized email content for each target company, then sends the emails through your Gmail account using SMTP.

### Key Features

- **AI-Powered Personalization** — Uses a local LLM (Ollama) to generate unique, company-specific email content
- **Browser Automation** — Built-in Playwright-based browser agent to scrape company information from websites
- **Interactive Agent Loop** — Conversational CLI where you tell the agent what to do and it autonomously uses tools (navigate, extract text, click, send emails)
- **Duplicate Prevention** — Tracks sent emails in `sent_emails.json` to avoid spamming the same company
- **Dual Email Templates** — Both plain text and HTML email versions with professional formatting
- **Local AI** — No cloud API keys needed; runs entirely on your machine via Ollama

## Project Structure

```
auto-job-cold-emailer/
├── cold-email-agent.py        # Main interactive AI agent with browser tools
├── async_cold_email.py        # Standalone async cold email sender
├── main.py                    # Entry point stub
├── pyproject.toml             # Project dependencies (uv/pip)
├── secrets.env                # Email credentials (add your own)
├── sent_emails.json           # Tracks already-contacted emails
├── README.md                  # This file
├── ai-web-agent/              # Related browser agent scripts
│    ├── async_slim_browser_agent copy.py
│    └── slim_browser_agent.py
├── assets/                    # Profile images, logos, etc.
└── playwright/                # Playwright browser state & auth
     └── .auth/
         └── state.json         # Saved browser session state
```

## How It Works

1. **Configure** your Gmail credentials in `secrets.env`
2. **Run** the interactive agent (`cold-email-agent.py`) or the standalone email sender (`async_cold_email.py`)
3. **Tell the agent** what companies to target — it navigates to their websites, extracts text, generates personalized content, and sends emails
4. **Track** all sent emails in `sent_emails.json` to avoid duplicates

### Architecture

```
User (CLI)
     │
     ▼
WebAgent (ollama LLM)
     │
     ├── BrowserManager (Playwright)
     │        ├── navigate_to_url()
     │        ├── extract_text_from_page()
     │        └── click_button_with_text()
     │
     └── send_cold_email()
             ├── Personalizes email body
             ├── Checks sent_emails.json for duplicates
             └── Sends via aiosmtplib (Gmail SMTP)
```

## Installation

### Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** — Fast Python package installer and virtual environment manager
- **[Ollama](https://ollama.com)** — For running local AI models
- **Playwright browsers** — Installed via `playwright install`

### Setup

```bash
# Clone the repository
cd auto-job-cold-emailer

# Create and activate the virtual environment
uv venv

# Install dependencies
uv pip install -r pyproject.toml

# Install Playwright browsers
playwright install chromium
```

### Configure Credentials

1. Edit `secrets.env` with your Gmail credentials:

```env
USER_EMAIL=your-email@gmail.com
APP_PASSWORD=your-gmail-app-password
```

2. **Get a Gmail App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification
   - Go to App Passwords (search "App Passwords" in Google Account)
   - Generate a new app password for "Mail"
   - Paste it into `secrets.env` (remove spaces)

## Usage

### Interactive AI Agent

Launch the conversational agent that can browse websites, extract information, and send personalized emails:

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

The agent uses tool-calling to autonomously decide which actions to take — navigating pages, extracting text, clicking buttons, and sending emails.

### Custom Email Template

The email template in both scripts is fully customizable. Edit the `send_cold_email()` function in either script to change:

- Subject line
- Email body text
- HTML formatting
- Signature block
- Linked project references

## Dependencies

| Package                                                      | Purpose                      |
| ------------------------------------------------------------ | ---------------------------- |
| [aiofiles](https://github.com/python-poetry/aiofiles)        | Async file operations        |
| [aiosmtplib](https://github.com/aio-libs/aiosmtplib)         | Async SMTP email sending     |
| [ollama](https://github.com/ollama/ollama-python)            | Local AI model integration   |
| [playwright](https://github.com/microsoft/playwright-python) | Browser automation           |
| [python-dotenv](https://github.com/theskumar/python-dotenv)  | Environment variable loading |

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
CLICK = True   # Set to False to disable click_button_with_text tool
```

### Sent Email Tracking

Emails already sent are stored in `sent_emails.json`. The agent checks this before sending to prevent duplicate outreach.

## Security Notes

- **Never commit `secrets.env`** — It contains your email credentials
- Use a **Gmail App Password**, not your main password
- The `playwright/.auth/state.json` file contains browser session data — treat it as sensitive

## Troubleshooting

| Issue                                        | Solution                                                         |
| -------------------------------------------- | ---------------------------------------------------------------- |
| `FileNotFoundError: Saved context not found` | Run `playwright install chromium` and re-authenticate in browser |
| `Authentication failed` for SMTP             | Verify your Gmail App Password has no spaces                     |
| Model connection errors                      | Ensure Ollama is running (`ollama serve`)                        |
| Slow model responses                         | Switch to a smaller model like `qwen3.5:0.8b`                    |

## License

This project is provided as-is for personal use.
