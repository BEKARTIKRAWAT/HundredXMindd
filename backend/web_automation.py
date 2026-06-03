import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
class WebAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        self.last_url = None
    def goto(self, url: str):
        response = self.session.get(url)
        response.raise_for_status()
        self.last_url = url
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        return {"title": title, "status": response.status_code}
    def get_text(self, selector: str):
        if not self.last_url:
            raise Exception("No page loaded. Call goto first.")
        response = self.session.get(self.last_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try CSS selector, then tag name, then class
        if selector.startswith(('.', '#')):
            elements = soup.select(selector)
        else:
            elements = soup.find_all(selector)
        texts = [el.get_text(strip=True) for el in elements]
        return {"texts": texts}
    def fill_form(self, form_data: dict, submit_button_selector: str = None):
        if not self.last_url:
            raise Exception("No page loaded.")
        # Simple POST submission with data
        response = self.session.post(self.last_url, data=form_data)
        response.raise_for_status()
        self.last_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')
        return {"status": response.status_code, "new_url": response.url}
    def screenshot(self, path: str = "screenshot.png"):
        # Not implemented with requests (use an external library if needed)
        return {"error": "Screenshot not available in requests mode. Use external tool."}
_web_auto = WebAutomation()
async def perform_action(action: str, params: dict):
    def sync_action():
        try:
            if action == "goto":
                return _web_auto.goto(params["url"])
            elif action == "get_text":
                return _web_auto.get_text(params["selector"])
            elif action == "fill_form":
                return _web_auto.fill_form(params["form_data"], params.get("submit_button_selector"))
            elif action == "screenshot":
                return _web_auto.screenshot(params.get("path", "screenshot.png"))
            else:
                return {"error": f"Unknown action '{action}'"}
        except Exception as e:
            return {"error": str(e)}
    import asyncio
    return await asyncio.to_thread(sync_action)
