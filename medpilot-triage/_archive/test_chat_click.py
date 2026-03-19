import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capture console logs
        page.on("console", lambda msg: print(f"Browser Console: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser Error: {err}"))
        
        print("Navigating to http://127.0.0.1:8000...")
        await page.goto("http://127.0.0.1:8000/")
        await page.wait_for_load_state("networkidle")
        
        print("Clicking chat button...")
        # Find the button using its onclick attribute
        button = await page.query_selector('button[onclick="toggleChat()"]')
        if button:
            print("Button found. Clicking...")
            await button.click()
            await page.wait_for_timeout(2000)
            
            chat_window = await page.query_selector('#chat-window')
            if chat_window:
                is_hidden = await chat_window.evaluate('el => el.classList.contains("hidden")')
                print(f"Chat window hidden? {is_hidden}")
            else:
                print("Chat window element not found!")
        else:
            print("Chat button not found!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
