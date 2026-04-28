from datetime import datetime

from ollama import ResponseError, chat
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

BROWSER_STATE_PATH = "playwright/.auth/state.json"
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

    def __init__(self, state_path=BROWSER_STATE_PATH):
        """Initialize the BrowserManager with a state file path."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        try:
            self.context = self.browser.new_context(storage_state=state_path)
        except FileNotFoundError:
            print("Saved context not found. Creating new context.")
            self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.state_path = state_path

    def navigate_to_url(self, url: str):
        """
        Navigate to a given URL.

        Args:
            page: The Playwright page object. This is already passed in when it is called as a tool, so you don't need to worry about it when calling the function.
            url: The URL to navigate to. This you will need to pass in when calling the function as a tool.

        Returns:
            A success message if the url was successfully accessed.
        """
        try:
            self.page.goto(url)
            return f"Successfully navigated to: {url}!"
        except Exception as e:
            return f"Failed to navigate to {url}, due to: {e}"

    def extract_text_from_page(self):
        """
        Extracts all the visible text from the page body

        Returns:
            All the text from the current url.
        """
        text = self.page.inner_text("body")
        return text

    def click_button_with_text(self, text: str):
        """
        Click a button containing specific text.

        Args:
            text: The text of the button to click. This you will need to pass in when calling the function as a tool.

        Returns:
            A success message if the button was successfully clicked.
        """

        try:
            self.page.get_by_text(text).first.click()
            return f"Clicked the button with text: {text}!"
        except Exception as e:
            return f"Failed to click the button with text: {text}, due to: {e}"

    def close(self):
        # TODO: make saving to state.json more dynamic, perhaps use pathlib?
        self.context.storage_state(path=BROWSER_STATE_PATH)
        self.browser.close()
        self.playwright.stop()


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

    def run(self):
        while True:
            user_input = input("\nWhat should I do? (quit to exit): ")
            if user_input.lower() == "quit":
                break
            self.messages.append({"role": "user", "content": user_input})
            self.process_cycle()

    def process_cycle(self):
        while True:
            try:
                response = chat(
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
                    result = function_to_call(**args)
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


def main():
    print("This is a slim browser agent!")

    browser = BrowserManager(state_path=BROWSER_STATE_PATH)
    # Change click to True to activate clicking functionality
    agent = WebAgent(model=SELECTED_MODEL, browser_manager=browser, click=CLICK)

    try:
        agent.run()
    finally:
        browser.close()


if __name__ == "__main__":
    main()
