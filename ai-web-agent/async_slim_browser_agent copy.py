import asyncio
from datetime import datetime

from ollama import AsyncClient, ResponseError
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

BROWSER_STATE_PATH = "/Users/abishanarulselvan/CODING/auto-job-cold-emailer/playwright/.auth/state.json"
AVAILABLE_MODELS = {
    "qwen3.5": "qwen3.5:0.8b",
    "qwen3.6": "qwen3.6:35b-a3b-coding-nvfp4",
}
SELECTED_MODEL = AVAILABLE_MODELS.get("qwen3.6")

# Change CLICK to True to activate clicking functionality
CLICK = True


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
            instance.context = await instance.browser.new_context(storage_state=state_path)
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
                "content": "You are a web agent. You have access to functions which allows you to access the browser and navigate pages. Also, you are in an agent loop, so you are free to use whatever function you wish, and as many you like. Try to pass arguments into the url (when applicable), rather than clicking, to preserve resources and increase efficiencies by decreasing overhead.",
            },
        ]
        self.client = AsyncClient()
        self.click = click

        if self.click:
            self.tools = {
                "navigate_to_url": self.browser.navigate_to_url,
                "extract_text_from_page": self.browser.extract_text_from_page,
                "click_button_with_text": self.browser.click_button_with_text,
            }
        else:
            self.tools = {
                "navigate_to_url": self.browser.navigate_to_url,
                "extract_text_from_page": self.browser.extract_text_from_page,
            }

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
