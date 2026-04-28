import asyncio
import os
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv

load_dotenv("secrets.env")

# TODO: Add try and except logic
USER_EMAIL = os.getenv("USER_EMAIL")

# NOTE: User must get app password from google (gmail), to allow it assess to the email client
APP_PASSWORD = os.getenv("APP_PASSWORD")


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

Personally, my most interesting automation is Skipper: an automated absence caller, which calls my school office in my parents' cloned voice—so I can skip school. You can check it out here: https://github.com/abiarul1016-glitch/Skipper

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

    # HTML version, for better formatting
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
                <li><strong>Web Scraping:</strong> Created a Hackathon Scraper so I don't miss out on free food! <a href="https://github.com/abiarul1016-glitch/hackathon_scraper">GitHub</a></li>
                <li><strong>rental suite:</strong> An automated listing poster, using Playwright, Python asyncio, and text-generation via Ollama <a href="https://github.com/abiarul1016-glitch/rental-suite">GitHub</a></li>
            </ul>
            
            <p>Personally, my most interesting automation is Skipper: an automated absence caller, which calls my school office in my parents' cloned voice—so I can skip school. You can check it out here: <a href="https://github.com/abiarul1016-glitch/Skipper">https://github.com/abiarul1016-glitch/Skipper</a></p>

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


async def main():
    response = await send_cold_email(
        "dinoarul1129@gmail.com", "Apple", "Hey there, this is testing."
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
