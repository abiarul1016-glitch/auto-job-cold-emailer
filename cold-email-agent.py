import asyncio
import os
from datetime import datetime
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv
from ollama import AsyncClient, ResponseError
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

load_dotenv("secrets.env")

BROWSER_STATE_PATH = (
    "/Users/abishanarulselvan/CODING/auto-job-cold-emailer/playwright/.auth/state.json"
)
AVAILABLE_MODELS = {
    "qwen3.5": "qwen3.5:0.8b",
    "qwen3.6": "qwen3.6:35b-a3b-coding-nvfp4",
}
SELECTED_MODEL = AVAILABLE_MODELS.get("qwen3.6")

# Change CLICK to True to activate clicking functionality
CLICK = False

# TODO: Add try and except logic
USER_EMAIL = os.getenv("USER_EMAIL")

# NOTE: User must get app password from google (gmail), to allow it assess to the email client
APP_PASSWORD = os.getenv("APP_PASSWORD")


class BrowserManager:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    state_path: str

    """Handles all Playwright interactions."""

    def __init__(self):
        self.playwright = None
        self.browser = None

    @classmethod
    async def create(cls, state_path=BROWSER_STATE_PATH):
        """Initialize the BrowserManager with a state file path."""

        instance = cls()

        instance.playwright = await async_playwright().start()
        instance.browser = await instance.playwright.chromium.launch(headless=False)
        try:
            instance.context = await instance.browser.new_context(
                storage_state=state_path
            )
        except FileNotFoundError:
            print("Saved context not found. Creating new context.")
            instance.context = await instance.browser.new_context()
        instance.page = await instance.context.new_page()
        instance.state_path = state_path
        return instance

    async def navigate_to_url(self, url: str):
        """
        Navigate to a given URL.

        Args:
            page: The Playwright page object. This is already passed in when it is called as a tool, so you don't need to worry about it when calling the function.
            url: The URL to navigate to. This you will need to pass in when calling the function as a tool.

        Returns:
            A success message if the url was successfully accessed.
        """
        try:
            await self.page.goto(url)
            return f"Successfully navigated to: {url}!"
        except Exception as e:
            return f"Failed to navigate to {url}, due to: {e}"

    async def extract_text_from_page(self):
        """
        Extracts all the visible text from the page body

        Returns:
            All the text from the current url.
        """
        text = await self.page.inner_text("body")
        return text

    async def click_button_with_text(self, text: str):
        """
        Click a button containing specific text.

        Args:
            text: The text of the button to click. This you will need to pass in when calling the function as a tool.

        Returns:
            A success message if the button was successfully clicked.
        """

        try:
            await self.page.get_by_text(text).first.click()
            return f"Clicked the button with text: {text}!"
        except Exception as e:
            return f"Failed to click the button with text: {text}, due to: {e}"

    async def close(self):
        await self.context.storage_state(path=self.state_path)
        await self.browser.close()
        await self.playwright.stop()


class WebAgent:
    """Handles the conversation loop and tool execution."""

    date = datetime.today()
    human_formatted_date = date.strftime("%B %d, %Y")

    def __init__(self, model, browser_manager: BrowserManager, click=False):
        self.model = model
        self.browser = browser_manager
        self.messages = [
            {
                "role": "system",
                "content": "You are a job application assistant. You have access to functions which allows you to access the browser, navigate pages, as well as send emails. Also, you are in an agent loop, so you are free to use whatever function you wish, and as many you like. Try to pass arguments into the url (when applicable), rather than clicking, to preserve resources and increase efficiencies by decreasing overhead.",
            },
        ]
        self.client = AsyncClient()
        self.click = click

        self.tools = {
            "navigate_to_url": self.browser.navigate_to_url,
            "extract_text_from_page": self.browser.extract_text_from_page,
            "send_cold_email": send_cold_email,
        }

        # Add clicking function, if clicking is enabled.
        if self.click:
            self.tools["click_button_with_text"] = self.browser.click_button_with_text

    async def run(self):
        while True:
            user_input = input("\nWhat should I do? (quit to exit): ")
            if user_input.lower() == "quit":
                break
            self.messages.append({"role": "user", "content": user_input})
            await self.process_cycle()

    async def process_cycle(self):
        while True:
            try:
                response = await self.client.chat(
                    model=self.model,
                    messages=self.messages,
                    tools=list(self.tools.values()),
                    think=False,
                )
            except ResponseError as e:
                print(f"Error: {e.error}")
                return

            self.messages.append(response.message)

            if not response.message.tool_calls:
                print(f"\nAgent: {response.message.content}")
                break

            for tool_call in response.message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_to_call = self.tools[function_name]
                    args = tool_call.function.arguments
                    result = await function_to_call(**args)
                    print(f"Called: {function_name}!")
                except KeyError:
                    result = f"Error: Unknown tool '{function_name}'"
                except Exception as e:
                    result = f"Error calling {function_name}: {e}"

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_name": function_name,
                        "content": str(result),
                    }
                )


# this can be factored into two functions: generate email, and send email
async def send_cold_email(send_to, company_name, generated_reason):
    """
    Send a personalized cold email to a company.

        Args:
            send_to: Recipient email address (str).
            company_name: Name of the company (str). Used to personalize subject and body.
            generated_reason: Personalized reason for applying (str). Injected into email body.

        Returns:
            str: Success or error message.
    """

    # For now reassign send_to, to my email for testing purposes. TODO: REMOVE IN PRODUCTION
    send_to = USER_EMAIL

    # Set up Email Details - TODO: Add profile image
    message = EmailMessage()
    message["From"] = USER_EMAIL
    message["To"] = send_to
    message["Subject"] = (
        f"12th grader / Python & Automation dev looking to build for {company_name}"
    )
    message.set_content(
        f"""To the team at {company_name},

Have you ever felt like a bird whose feet were chained, and force-fed baby food? That's how I have constantly felt at school, where the theoretical path isn't for me. I'd rather build real tools than read about them.

I'm a self-taught developer (CS50x/P) focused on automation and local AI. Recently, I built a slim browser agent using Playwright because traditional MCP servers were too slow for my local machine. You can see the repo here: https://github.com/abiarul1016-glitch/slim-browser-agent

I also have experience with:
Local AI: Working with Ollama for task automation.
Voice/Data: Building end-to-end automation pipelines (scraping, data analysis).
Personally, my most interesting automation: Skipper, an automated absence caller, which calls my school office in my parents' cloned voice—so I can skip school. You can check it out here: https://github.com/abiarul1016-glitch/Skipper

I'm looking to skip the traditional 4-year degree to put that energy into an organization building real products. I know hiring a high schooler is a non-traditional move, but I have the grit to learn whatever stack you use and the drive to deliver results immediately.

{generated_reason}

Do you have 10 minutes for a quick chat, or perhaps a small task/internship where I could prove my value?

Best of luck with any future endeavours,
Abishan Arulselvan

GitHub: https://github.com/abiarul1016-glitch
Linkedin: https://www.linkedin.com/in/abishan-arulselvan/

Abishan Arulselvan | STUDENT
abiarul1016@gmail.com

"""
    )

    # Gemini-Generated HTML version, for better formatting. NOTE: Perhaps remove uneccessary bolding
    html_content = f"""
    <html>
        <body style="font-family: 'Georgia', sans-serif; font-size: 14px; line-height: 1.5; color: #333;">
            <p>To the team at <strong>{company_name}</strong>,</p>
            
            <p>Have you ever felt like a bird whose feet were chained, and force-fed baby food? That's how I have constantly felt at school, where the theoretical path isn't for me. I'd rather build real tools than read about them.</p>

            <p>I'm a self-taught developer (CS50x/P) focused on automation and local AI. Recently, I built a slim browser agent using Playwright because traditional MCP servers were too slow for my local machine. You can see the repo here: <a href="https://github.com/abiarul1016-glitch/slim-browser-agent">https://github.com/abiarul1016-glitch/slim-browser-agent</a></p>
            
            <p>I also have experience with:</p>
            <ul>
                <li><strong>Local AI:</strong> Working with Ollama for task automation.</li>
                <li><strong>Voice/Data:</strong> Building end-to-end automation pipelines.</li>
                <li><strong>Skipper:</strong> An automated absence caller using cloned voices.</li>
            </ul>
            
            <p>Personally, my most interesting automation: Skipper, an automated absence caller, which calls my school office in my parents' cloned voice—so I can skip school. You can check it out here: <a href="https://github.com/abiarul1016-glitch/Skipper">https://github.com/abiarul1016-glitch/Skipper</a></p>

            <p>I'm looking to skip the traditional 4-year degree to put that energy into an organization building real products. I know hiring a high schooler is a non-traditional move, but I have the grit to learn whatever stack you use and the drive to deliver results immediately.</p>

            <p>{generated_reason}</p>

            <p>Do you have 10 minutes for a quick chat, or perhaps a small task/internship where I could prove my value?</p>

            <!-- EMAIL SIGNATURE -->
            <div style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px;">
                <strong style="color: #007bff;">Abishan Arulselvan</strong><br>
                <span style="font-size: 12px; color: #666;">Python & Automation Developer | Student</span><br>
                <a href="https://github.com/abiarul1016-glitch" style="font-size: 12px;">GitHub</a> | 
                <a href="https://www.linkedin.com/in/abishan-arulselvan/" style="font-size: 12px;">LinkedIn</a>
            </div>
        </body>
    </html>
    """
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=USER_EMAIL,
            password=APP_PASSWORD,
        )
        return f"Email successfully send to {company_name}: {send_to}"
    except Exception as e:
        return f"Email was not successfully send due to {e}"


async def check_if_already_sent():
    pass


async def main():
    print("This is a slim browser agent!")

    browser = await BrowserManager.create(state_path=BROWSER_STATE_PATH)
    # Change click to True to activate clicking functionality
    agent = WebAgent(model=SELECTED_MODEL, browser_manager=browser, click=CLICK)

    try:
        await agent.run()
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
