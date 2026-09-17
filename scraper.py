import io
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import paramiko # THIS IS THE NEW SECURE UPLOAD LIBRARY!

all_notifications = []

def add_to_list(title, board_name, region, date_str, link, is_new=False):
    if not title or title.strip() == "":
        return
        
    all_notifications.append({
        "id": f"notif_{len(all_notifications)}",
        "title": " ".join(title.split()),
        "boardName": board_name,
        "region": region,
        "dateStr": date_str,
        "year": "2026",
        "link": link,
        "isNew": is_new
    })

# ==========================================
# 1. SCRAPE FBISE
# ==========================================
def scrape_fbise():
    url = "https://www.fbise.edu.pk/newsupdatenotification.php"
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_tab = soup.find('div', id='news_update')
    if news_tab:
        rows = news_tab.find_all('tr')
        count = 0
        for row in rows:
            if count >= 6: break
            if row.find('th') or row.find('td', class_='sub-title'): continue
            link_tag = row.find('a')
            if link_tag:
                raw_link = link_tag.get('href', '')
                full_link = f"https://www.fbise.edu.pk/{raw_link}" if not raw_link.startswith('http') else raw_link
                is_new = bool(row.find('img', src=lambda s: s and 'newflash' in s.lower()))
                title_text = link_tag.text.strip()
                if "form" in title_text.lower() and "admission" not in title_text.lower(): continue
                today_date = datetime.today().strftime("%d %b")
                add_to_list(title_text, "FEDERAL BOARD", "federal", today_date, full_link, is_new)
                count += 1

# ==========================================
# 2. SCRAPE BISE LAHORE
# ==========================================
def scrape_lahore():
    url = "https://www.biselahore.com/notifications"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    notices = soup.find_all('a', class_='group flex items-center')[:6] 
    for i, notice in enumerate(notices):
        raw_link = notice.get('href', '')
        full_link = f"https://www.biselahore.com{raw_link}" if raw_link.startswith('/') else raw_link
        title_span = notice.find('span', class_='flex-1')
        title_text = title_span.text.strip() if title_span else "Notification"
        today_date = datetime.today().strftime("%d %b") 
        add_to_list(title_text, "BISE LAHORE", "punjab", today_date, full_link, is_new=(i < 2))

# ==========================================
# 3. SCRAPE BBISE QUETTA
# ==========================================
def scrape_quetta():
    url = "https://bbise.edu.pk/Notifications"
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    notices = soup.find_all('article', class_='notice-card')[:6] 
    for notice in notices:
        title_tag = notice.find('h2')
        title_text = title_tag.text.strip() if title_tag else "Board Notification"
        link_tag = notice.find('a', class_='btn-icon-link')
        if link_tag:
            raw_link = link_tag.get('href', '')
            full_link = f"https://bbise.edu.pk{raw_link}" if raw_link.startswith('/') else raw_link
            meta_div = notice.find('div', class_='notice-meta')
            date_str = meta_div.find('span').text.strip()[:6] if meta_div else datetime.today().strftime("%d %b")
            is_new = bool(notice.find('span', class_='new-badge'))
            add_to_list(title_text, "BBISE QUETTA", "balochistan", date_str, full_link, is_new)

# ==========================================
# 4. SCRAPE BSEK KARACHI
# ==========================================
def scrape_karachi():
    url = "https://bsek.edu.pk/#/news"
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    notices = soup.find_all('div', role='button')[:6] 
    for i, notice in enumerate(notices):
        title_tag = notice.find('h3')
        if not title_tag: continue
        title_text = title_tag.text.strip()
        full_link = "https://bsek.edu.pk/#/news"
        date_span = notice.find('span', class_='text-xs font-black text-gray-400')
        if date_span:
            d_text = date_span.text.replace(',', '').split()
            date_str = f"{d_text[1]} {d_text[0]}" if len(d_text) >= 2 else datetime.today().strftime("%d %b")
        else:
            date_str = datetime.today().strftime("%d %b")
        add_to_list(title_text, "BSEK KARACHI", "sindh", date_str, full_link, is_new=(i < 2))

# ==========================================
# 5. SCRAPE BISE PESHAWAR
# ==========================================
def scrape_peshawar():
    url = "https://www.bisep.edu.pk/page-10007.html"
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')
    count = 0
    for row in rows:
        if count >= 6: break
        link_tag = row.find('a')
        if link_tag and link_tag.text.strip():
            raw_link = link_tag.get('href', '')
            if raw_link.startswith('#'): continue
            full_link = f"https://www.bisep.edu.pk/{raw_link}" if not raw_link.startswith('http') else raw_link
            is_new = bool(row.find('img', src=lambda s: s and 'new1.gif' in s.lower()))
            today_date = datetime.today().strftime("%d %b")
            add_to_list(link_tag.text, "BISE PESHAWAR", "kpk", today_date, full_link, is_new)
            count += 1

# ==========================================
# EXECUTE ALL SCRAPERS SAFELY
# ==========================================
try: scrape_fbise(); print("✅ FBISE Scraped") 
except Exception as e: print("❌ FBISE Failed:", e)

try: scrape_lahore(); print("✅ Lahore Scraped") 
except Exception as e: print("❌ Lahore Failed:", e)

try: scrape_quetta(); print("✅ Quetta Scraped") 
except Exception as e: print("❌ Quetta Failed:", e)

try: scrape_karachi(); print("✅ Karachi Scraped") 
except Exception as e: print("❌ Karachi Failed:", e)

try: scrape_peshawar(); print("✅ Peshawar Scraped") 
except Exception as e: print("❌ Peshawar Failed:", e)

# ==========================================
# UZAIR
# ==========================================

import os

# Create the folder if it doesn't exist
os.makedirs('output', exist_ok=True)

# Make sure you are saving the file INSIDE the folder like this:
with open('output/notifications.json', 'w') as f:
    # your save logic here...

# ==========================================
# SAVE & SECURE SFTP UPLOAD TO PANTHEON
# ==========================================
with open('notifications-data.json', 'w', encoding='utf-8') as f:
    json.dump(all_notifications, f, ensure_ascii=False, indent=4)
print(f"\nTotal Notifications Scraped: {len(all_notifications)}")

try:
    host = os.environ.get('FTP_HOST')
    port = 2222
    username = os.environ.get('FTP_USER')
    private_key_str = os.environ.get('SSH_PRIVATE_KEY')
    
    # Load the private key
    key = paramiko.RSAKey.from_private_key(io.StringIO(private_key_str))
    
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    sftp.chdir('files') 
    sftp.put('notifications-data.json', 'notifications-data.json')
    
    sftp.close()
    transport.close()
    print("🚀 SUCCESS: JSON uploaded to WordPress via SFTP with SSH Key!")
except Exception as e:
    print(f"⚠️ SFTP Upload Failed: {e}")
