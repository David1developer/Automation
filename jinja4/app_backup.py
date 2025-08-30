from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from werkzeug.utils import secure_filename
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
import os
import json

app = Flask(__name__)
app.secret_key = 'secret'
log_lines = []
automation_running = False
success_count = 0
total_runs = 0
current_progress = 0
total_accounts = 0
proxies_count = 0
comments_count = 0

UPLOAD_FOLDER = 'uploads'
ACCOUNTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'accounts')
PROXIES_FOLDER = os.path.join(UPLOAD_FOLDER, 'proxies')
COMMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'comments')

os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(PROXIES_FOLDER, exist_ok=True)
os.makedirs(COMMENTS_FOLDER, exist_ok=True)

PLATFORM_URLS = {
    "facebook": "https://facebook.com",
    "instagram": "https://instagram.com",
    "tiktok": "https://tiktok.com"
}

def log(msg):
    log_lines.append(msg)
    print(msg)

def clear_table_data():
    """Clear all account files from the accounts folder"""
    try:
        for filename in os.listdir(ACCOUNTS_FOLDER):
            file_path = os.path.join(ACCOUNTS_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        log("Account table data cleared")
        return True
    except Exception as e:
        log(f"Error clearing table data: {e}")
        return False

def parse_account_file_to_table(filepath):
    """Parse account file and extract account information."""
    data = {
        'no': 0,
        'username': '',
        'privatekey': '',
        'cookies': '',
        'email': '',
        'passmail': '',
        'phone': '',
        'recoverymail': '',
        'filename': os.path.basename(filepath)
    }
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            lines = content.splitlines()
            if not content:
                return data
            if any(':' in line for line in lines):
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('username:'):
                        data['username'] = line.split(':', 1)[1].strip()
                    elif line.startswith('password:'):
                        data['privatekey'] = line.split(':', 1)[1].strip()
                    elif line.startswith('cookies:'):
                        data['cookies'] = line.split(':', 1)[1].strip()
                    elif line.startswith('email:'):
                        data['email'] = line.split(':', 1)[1].strip()
                    elif line.startswith('mailpass:') or line.startswith('passmail:'):
                        data['passmail'] = line.split(':', 1)[1].strip()
                    elif line.startswith('phone:'):
                        data['phone'] = line.split(':', 1)[1].strip()
                    elif line.startswith('recoverymail:') or line.startswith('recovery:'):
                        data['recoverymail'] = line.split(':', 1)[1].strip()
            elif '|' in content:
                first_line = lines[0].strip()
                parts = first_line.split('|')
                if len(parts) >= 2:
                    data['username'] = parts[0].strip()
                    data['privatekey'] = parts[1].strip()
                    data['cookies'] = parts[2].strip() if len(parts) > 2 else ''
                    data['email'] = parts[3].strip() if len(parts) > 3 else ''
                    data['passmail'] = parts[4].strip() if len(parts) > 4 else ''
                    data['phone'] = parts[5].strip() if len(parts) > 5 else ''
                    data['recoverymail'] = parts[6].strip() if len(parts) > 6 else ''
            elif ',' in content:
                first_line = lines[0].strip()
                parts = first_line.split(',')
                if len(parts) >= 2:
                    data['username'] = parts[0].strip()
                    data['privatekey'] = parts[1].strip()
                    data['cookies'] = parts[2].strip() if len(parts) > 2 else ''
                    data['email'] = parts[3].strip() if len(parts) > 3 else ''
                    data['passmail'] = parts[4].strip() if len(parts) > 4 else ''
                    data['phone'] = parts[5].strip() if len(parts) > 5 else ''
                    data['recoverymail'] = parts[6].strip() if len(parts) > 6 else ''
            else:
                if len(lines) >= 1:
                    data['username'] = lines[0].strip()
                if len(lines) >= 2:
                    data['privatekey'] = lines[1].strip()
        return data
    except Exception:
        return data

@app.route('/')
def index():
    accounts_table = []
    account_files = os.listdir(ACCOUNTS_FOLDER)
    count = 1
    for filename in account_files:
        full_path = os.path.join(ACCOUNTS_FOLDER, filename)
        parsed = parse_account_file_to_table(full_path)
        if parsed['username'] and parsed['privatekey']:
            parsed['no'] = count
            accounts_table.append(parsed)
            count += 1
    return render_template('index.html', accounts_table=accounts_table)

@app.route('/clear_table', methods=['POST'])
def clear_table():
    """Clear the accounts table in the browser (do not delete files)"""
    return jsonify({'status': 'cleared', 'accounts': []})

if __name__ == "__main__":
    app.run(debug=True)
