from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import csv
import time
from bs4 import BeautifulSoup

# Configuration
CAT_ID      = 59
TOTAL_PAGES = 376
BASE_URL    = f"https://www.yiddish24.com/cat/{CAT_ID}"
TEXT_DIR    = "yiddish24_texts"
AUDIO_DIR   = "yiddish24_audio"
CSV_FILE    = "yiddish24_index.csv"

# Headers for downloading audio
dl_headers = {
    "User-Agent":     "Mozilla/5.0 (X11; Linux x86_64)",
    "Referer":        BASE_URL,
    "Accept":         "audio/*;q=0.9,*/*;q=0.5",
    "Range":          "bytes=0-",
    "Accept-Encoding":"identity",
}

# Prepare output directories
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# Setup Selenium in headless mode
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get(BASE_URL)

# Initialize CSV and HTTP session for audio
with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvf:
    writer = csv.writer(csvf)
    writer.writerow(["page", "id", "date", "title", "text_file", "audio_file"])

    http = requests.Session()
    http.headers.update({"User-Agent": dl_headers["User-Agent"]})

    # Loop through each page
    for page in range(1, TOTAL_PAGES + 1):
        print(f"\n📄 Processing page {page}/{TOTAL_PAGES}")
        # Wait for entries to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".yiddish-player-details.darkred"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        entries = soup.select("div.yiddish-player-details.darkred")
        print(f"  🔍 Found {len(entries)} entries")

        for entry in entries:
            panel = entry.select_one("div.playing-panel")
            if not panel:
                continue
            eid = panel.get("data-id")
            url = panel.get("data-song-url")
            if not eid or not url:
                continue

            title = entry.select_one("h1").get_text(strip=True)
            date  = entry.select_one("span.date").get_text(strip=True)
            text  = entry.select_one("p").get_text(" ", strip=True)

            # Save text file
            txt_file = f"entry_{eid}.txt"
            txt_path = os.path.join(TEXT_DIR, txt_file)
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(f"{title}\n{date}\n\n{text}")
            print(f"  📝 {txt_file}")

            # Download audio
            safe = "".join(c for c in title if c.isalnum() or c in " _-")[:50].strip()
            aud_file = f"{eid}_{safe}.mp3"
            aud_path = os.path.join(AUDIO_DIR, aud_file)
            if not os.path.exists(aud_path):
                resp = http.get(url, headers=dl_headers, stream=True)
                if resp.status_code in (200, 206) and "audio" in resp.headers.get("Content-Type", ""):
                    with open(aud_path, "wb") as af:
                        for chunk in resp.iter_content(8192):
                            af.write(chunk)
                    print(f"  ✅ {aud_file}")
                else:
                    print(f"  ⚠️ Audio failed ({resp.status_code}) for ID {eid}")

            # Write CSV row
            writer.writerow([page, eid, date, title, txt_file, aud_path])

        # Click the "Next" arrow
        if page < TOTAL_PAGES:
            # Remove any popups
            driver.execute_script(
                "document.querySelectorAll('#modalMain, .popup-box, .popup-backdrop, #popup-title, .popup-heading').forEach(el=>el.remove());"
            )
            # Locate and click the next page button by class
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next_icon > a"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", next_btn)
            time.sleep(1)

# Clean up
driver.quit()
print("\n🎉 Done! All pages processed.")
print(f"Texts in: {TEXT_DIR}")
print(f"Audio in: {AUDIO_DIR}")
print(f"Index CSV: {CSV_FILE}")
