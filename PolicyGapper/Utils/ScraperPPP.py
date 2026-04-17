import os
import requests
from weasyprint import HTML
import sys
import json
import tempfile
from playwright.sync_api import sync_playwright
from google_play_scraper import app


def save_pdf_robust(url, output_file):
    extension_path = os.path.join(os.path.dirname(__file__), "ISDCAC")

    with tempfile.TemporaryDirectory() as user_data_dir:
        with sync_playwright() as p:

            args = [
                f"--disable-extensions-except={extension_path}",
                f"--load-extension={extension_path}",
                "--headless=new",
            ]

            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=args,
            )

            page = context.pages[0] if context.pages else context.new_page()

            page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})

            print(f"Navigazione verso: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            print("Attendo 7 secondi l'azione di I-Still-Dont-Care-About-Cookies...")
            page.wait_for_timeout(7000)

            page.evaluate(
                """() => {
                const selectors = [
                    "[id*='cookie']", "[class*='cookie']",
                    "[id*='consent']", "[class*='consent']",
                    "[id*='gdpr']", "[class*='gdpr']",
                    ".vzKQHb", ".K2OSr",
                    "[role='alertdialog']", "[role='dialog'][aria-label*='cookie']",
                    ".banner", ".overlay", ".modal-backdrop"
                ];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(e => {
                        if(e && e.style) {
                            const text = e.innerText ? e.innerText.toUpperCase() : "";
                            if (e.tagName === 'BUTTON' || e.getAttribute('role') === 'button') {
                                if (text.includes("OK") || text.includes("ACCEPT") || text.includes("AGREE") || text.includes("DENY") || text.includes("REJECT")) {
                                    e.click();
                                    return;
                                }
                            }
                            e.style.display = 'none';
                            e.style.opacity = '0';
                            e.style.pointerEvents = 'none';
                        }
                    });
                });
            }"""
            )
            page.wait_for_timeout(2000)

            page.pdf(path=output_file, format="A4", print_background=True)
            context.close()
            print(f"PDF generato con successo: {output_file}")



with open("UrlPrivacyPolicy.txt", "r", encoding="utf-8") as f:
    privacy_policy_url = f.read().strip()

packageName = sys.argv[1]

result = app(packageName, lang="en", country="us")

output_dir = "./app_data"
os.makedirs(output_dir, exist_ok=True)
ppp_dir = "/app/PPP"
os.makedirs(ppp_dir, exist_ok=True)

filename = os.path.join(output_dir, f"{packageName}.json")
json_str = json.dumps(result, indent=4, ensure_ascii=False)

with open(filename, "w", encoding="utf-8") as file:
    file.write(f"{json_str}")

print("App Data Saved")

# Chiamata alla nuova funzione robusta
save_pdf_robust(privacy_policy_url, os.path.join(ppp_dir, f"{packageName}.pdf"))
