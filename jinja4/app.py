from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
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

def clear_table_data():
    """Clear uploaded account files from the accounts folder, but preserve sample files"""
    try:
        # List of sample files to preserve
        sample_files = {
            'test_user1.txt',
            'social_bot2.txt', 
            'auto_user3.txt',
            'demo_user4.txt',
            'marketing_bot.txt',
            'influencer_account.txt',
            'multi_user_account.txt'
        }
        
        deleted_count = 0
        for filename in os.listdir(ACCOUNTS_FOLDER):
            file_path = os.path.join(ACCOUNTS_FOLDER, filename)
            if os.path.isfile(file_path):
                # Only delete files that are NOT in the sample files list
                if filename not in sample_files:
                    os.remove(file_path)
                    deleted_count += 1
                    log(f"Deleted uploaded file: {filename}")
                else:
                    log(f"Preserved sample file: {filename}")
        
        if deleted_count > 0:
            log(f"Account table cleared: {deleted_count} uploaded files deleted, sample files preserved")
        else:
            log("No uploaded files to clear, sample files preserved")
        return True
    except Exception as e:
        log(f"Error clearing table data: {e}")
        return False

app = Flask(__name__)
import os
import json
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

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

def parse_account_file_to_table(filepath):
    """
    Parse account file and extract account information.
    Supports multiple formats:
    1. Key-value format: username:value, password:value, etc.
    2. Pipe-separated format: username|password|cookies|email|mailpass|phone|recovery
    3. Comma-separated format: username,password,cookies,email,mailpass,phone,recovery
    """
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
            # Key-value format
            if any(':' in line for line in lines):
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key == 'username':
                        data['username'] = value
                    elif key == 'password' or key == 'privatekey':
                        data['privatekey'] = value
                    elif key == 'cookies':
                        data['cookies'] = value
                    elif key == 'email':
                        data['email'] = value
                    elif key == 'mailpass' or key == 'passmail':
                        data['passmail'] = value
                    elif key == 'phone':
                        data['phone'] = value
                    elif key == 'recoverymail' or key == 'recovery':
                        data['recoverymail'] = value
            # Pipe-separated format
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
            # Comma-separated format
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
            # Plain text fallback
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
    global total_accounts, proxies_count, comments_count
    
    # Check if clear parameter is passed in URL (e.g., /?clear=true)
    if request.args.get('clear') == 'true':
        clear_table_data()
        flash('Account table cleared on page load!', 'info')
    
    # Uncomment the line below if you want to automatically clear table data on every page reload
    # clear_table_data()
    
    def is_valid_account_file(filepath):
        """Check if account file contains valid username AND password/privatekey"""
        try:
            full_path = os.path.join(ACCOUNTS_FOLDER, filepath)
            parsed_data = parse_account_file_to_table(full_path)
            has_username = parsed_data['username'] and parsed_data['username'].strip()
            has_password = parsed_data['privatekey'] and parsed_data['privatekey'].strip()
            return bool(has_username and has_password)
        except Exception:
            return False

    account_files = os.listdir(ACCOUNTS_FOLDER)
    total_accounts = sum(1 for f in account_files if is_valid_account_file(f))
    proxies_count = len(os.listdir(PROXIES_FOLDER))
    comments_count = len(os.listdir(COMMENTS_FOLDER))
    # If no valid account folder, set cards to N/A or 0
    if total_accounts == 0:
        stats = {
            'accounts': 0,
            'proxies': 0,
            'comments': 0,
            'success_rate': 'N/A',
            'progress': 'N/A',
            'status': 'Idle',
            'total_accounts': 0,
            'proxies_count': 0,
            'comments_count': 0
        }
    else:
        stats = {
            'accounts': total_accounts,
            'proxies': proxies_count,
            'comments': comments_count,
            'success_rate': calculate_success_rate(),
            'progress': f"{current_progress} / {total_accounts}",
            'status': 'Running' if automation_running else 'Idle',
            'total_accounts': total_accounts,
            'proxies_count': proxies_count,
            'comments_count': comments_count
        }

    account_files = os.listdir(ACCOUNTS_FOLDER)
    accounts_table = []
    count = 1
    for filename in account_files:
        full_path = os.path.join(ACCOUNTS_FOLDER, filename)
        parsed = parse_account_file_to_table(full_path)
        # Debug log for each file
        log(f"File: {filename} | Username: {parsed['username']} | Privatekey: {parsed['privatekey']}")
        # Only add valid accounts to the table with proper numbering
        if parsed['username'] and parsed['privatekey']:
            parsed['no'] = count
            parsed['filename'] = filename
            accounts_table.append(parsed)
            count += 1

    return render_template('index.html', stats=stats, log_content='\n'.join(log_lines), accounts_table=accounts_table)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded = False

    # Handle account folder upload (multiple files)
    account_files = request.files.getlist('account_folder')
    if account_files and account_files[0].filename:
        uploaded_count = 0
        for file in account_files:
            if file.filename:
                filename = secure_filename(file.filename)
                # Ensure unique filename
                original_filename = filename
                counter = 1
                while os.path.exists(os.path.join(ACCOUNTS_FOLDER, filename)):
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    counter += 1
                file.save(os.path.join(ACCOUNTS_FOLDER, filename))
                uploaded_count += 1
                log(f"Account file uploaded: {filename}")

        uploaded = True
        log(f"Account folder uploaded with {uploaded_count} files")

    # Handle individual file uploads
    file_map = {
        'proxies_file': PROXIES_FOLDER,
        'comments_file': COMMENTS_FOLDER
    }
    
    for field, folder in file_map.items():
        file = request.files.get(field)
        if file and file.filename:
            filename = secure_filename(file.filename)
            
            # Check if file already exists and add a number suffix if needed
            original_filename = filename
            counter = 1
            while os.path.exists(os.path.join(folder, filename)):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                counter += 1
                
            file.save(os.path.join(folder, filename))
            uploaded = True
            log(f"{field.replace('_', ' ').title()} uploaded: {filename}")
    
    # Handle single account file upload
    single_file = request.files.get('single_account_file')
    if single_file and single_file.filename:
        filename = secure_filename(single_file.filename)
        original_filename = filename
        counter = 1
        while os.path.exists(os.path.join(ACCOUNTS_FOLDER, filename)):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        single_file.save(os.path.join(ACCOUNTS_FOLDER, filename))
        uploaded = True
        log(f"Single account file uploaded: {filename}")
    
    if uploaded:
        flash('Files uploaded successfully! New accounts added to table.', 'success')
        log("File upload completed successfully")
    else:
        flash('No files were uploaded!', 'warning')
        log("No files were selected for upload")
    
    return redirect(url_for('index'))

@app.route('/start', methods=['POST'])
def start():
    global automation_running, current_progress, success_count, total_runs
    if automation_running:
        # Return flashed message in JSON for AJAX
        message = "Automation is already running."
        flash(message, "warning")
        return jsonify({'status': 'already running', 'logs': log_lines, 'flash': {'message': message, 'category': 'warning'}})
    # Count valid accounts before starting
    def is_valid_account_file(filepath):
        try:
            full_path = os.path.join(ACCOUNTS_FOLDER, filepath)
            parsed_data = parse_account_file_to_table(full_path)
            has_username = parsed_data['username'] and parsed_data['username'].strip()
            has_password = parsed_data['privatekey'] and parsed_data['privatekey'].strip()
            log(f"Checked file: {filepath} | Username: {parsed_data['username']} | Password: {parsed_data['privatekey']}")
            return bool(has_username and has_password)
        except Exception:
            return False

    account_files = os.listdir(ACCOUNTS_FOLDER)
    valid_accounts = [f for f in account_files if is_valid_account_file(f)]
    log(f"Valid accounts found: {valid_accounts}")
    if not valid_accounts:
        message = "File or folder not selected. Please choose an account file or folder before starting automation."
        flash(message, "warning")
        log("Account folder not selected. Automation not started.")
        return jsonify({'status': 'no_accounts', 'logs': log_lines, 'flash': {'message': message, 'category': 'warning'}})

    automation_running = True
    success_count = 0
    total_runs = 0
    current_progress = 0
    settings = request.get_json()
    message = "Automation started"
    flash(message, "info")
    thread = threading.Thread(target=run_automation, args=(settings,))
    thread.start()
    return jsonify({'status': 'started', 'logs': log_lines, 'flash': {'message': message, 'category': 'info'}})

@app.route('/stop', methods=['POST'])
def stop():
    global automation_running
    automation_running = False
    flash("Automation stopped", "warning")
    log("Automation manually stopped.")
    return ('', 204)

@app.route('/log')
def get_log():
    global total_accounts, proxies_count, comments_count
    total_accounts = len(os.listdir(ACCOUNTS_FOLDER))
    proxies_count = len(os.listdir(PROXIES_FOLDER))
    comments_count = len(os.listdir(COMMENTS_FOLDER))
    return jsonify({
        'logs': log_lines,
        'success_rate': calculate_success_rate(),
        'status': 'Running' if automation_running else 'Idle',
        'current_progress': current_progress,
        'total_accounts': total_accounts,
        'proxies': proxies_count,
        'comments': comments_count
    })

@app.route('/clear_log', methods=['POST'])
def clear_log():
    global log_lines
    log_lines = []  # Clear the log_lines array permanently
    return jsonify({'status': 'cleared'})

@app.route('/clear_table', methods=['POST'])
def clear_table():
    """Clear the accounts table in the browser (do not delete files)"""
    # Do not delete any files, just return an empty accounts list
    return jsonify({'status': 'cleared', 'accounts': []})

@app.route('/clear_all_accounts', methods=['POST'])
def clear_all_accounts():
    """Clear ALL account files including sample files"""
    try:
        deleted_count = 0
        for filename in os.listdir(ACCOUNTS_FOLDER):
            file_path = os.path.join(ACCOUNTS_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
        log(f"All account files cleared: {deleted_count} files deleted")
        flash('All account files cleared including samples!', 'warning')
        return jsonify({'status': 'cleared', 'message': f'All {deleted_count} account files cleared'})
    except Exception as e:
        log(f"Error clearing all account files: {e}")
        flash('Error clearing all account files!', 'error')
        return jsonify({'status': 'error', 'message': 'Failed to clear all account files'})

@app.route('/get_accounts')
def get_accounts():
    """Get current accounts table data for dynamic updates"""
    def is_valid_account_file(filepath):
        try:
            full_path = os.path.join(ACCOUNTS_FOLDER, filepath)
            parsed_data = parse_account_file_to_table(full_path)
            has_username = parsed_data['username'] and parsed_data['username'].strip()
            has_password = parsed_data['privatekey'] and parsed_data['privatekey'].strip()
            return bool(has_username and has_password)
        except Exception:
            return False

    account_files = os.listdir(ACCOUNTS_FOLDER)
    accounts_table = []
    count = 1
    for filename in account_files:
        full_path = os.path.join(ACCOUNTS_FOLDER, filename)
        parsed = parse_account_file_to_table(full_path)
        if parsed['username'] and parsed['privatekey']:
            parsed['no'] = count
            parsed['filename'] = filename  # Add filename for table link
            accounts_table.append(parsed)
            count += 1

    return jsonify({'accounts': accounts_table})

@app.route('/get_stats')
def get_stats():
    """Get current stats for dynamic updates"""
    def is_valid_account_file(filepath):
        try:
            full_path = os.path.join(ACCOUNTS_FOLDER, filepath)
            parsed_data = parse_account_file_to_table(full_path)
            has_username = parsed_data['username'] and parsed_data['username'].strip()
            has_password = parsed_data['privatekey'] and parsed_data['privatekey'].strip()
            return bool(has_username and has_password)
        except Exception:
            return False

    account_files = os.listdir(ACCOUNTS_FOLDER)
    total_accounts = sum(1 for f in account_files if is_valid_account_file(f))
    proxies_count = len(os.listdir(PROXIES_FOLDER))
    comments_count = len(os.listdir(COMMENTS_FOLDER))
    
    return jsonify({
        'accounts': total_accounts,
        'proxies': proxies_count,
        'comments': comments_count
    })

def calculate_success_rate():
    if total_runs == 0:
        return 0
    return int((success_count / total_runs) * 100)

def run_automation(settings):
    global automation_running, current_progress, total_runs, success_count, total_accounts
    platform = settings.get('platform', 'facebook')
    category = settings.get('category', 'login')
    format_type = settings.get('format', 'email')
    format_input = settings.get('formatInput', '').strip()
    headless = settings.get('headless', True)
    use_proxies = settings.get('use_proxies', False)
    mention = settings.get('mention', '').strip()
    accounts = os.listdir(ACCOUNTS_FOLDER)
    total_accounts = len(accounts) if accounts else 1
    if not accounts:
        accounts = ['dummy']
    
    log(f"Starting automation with Category: {category}, Format: {format_type}, Platform: {platform}")
    if format_input:
        log(f"Input Format Target: {format_input}")
    
    try:
        for idx, account in enumerate(accounts, 1):
            if not automation_running:
                log("Automation stopped by user.")
                break

            log(f"Processing account {idx}/{total_accounts}: {account}")
            log(f"Action: {category} on {platform} using {format_type} authentication")
            
            # Read credentials from file using the new parser
            account_path = os.path.join(ACCOUNTS_FOLDER, account)
            account_data = parse_account_file_to_table(account_path)
            
            # Determine authentication method based on format
            auth_credential = get_auth_credential(account_data, format_type)
            if not auth_credential:
                log(f"Skipping {account}: No valid {format_type} credential found")
                total_runs += 1
                current_progress = idx
                continue

            # Set up Chrome
            options = Options()
            if headless:
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            try:
                # Perform authentication and action based on category
                success = perform_automation_action(driver, platform, category, account_data, format_type, mention, format_input)
                if success:
                    success_count += 1
                    log(f"✅ {category} completed successfully for {auth_credential}")
                else:
                    log(f"❌ {category} failed for {auth_credential}")
                    
            except Exception as e:
                log(f"Error during {category} automation for {account}: {e}")
            finally:
                driver.quit()

            current_progress = idx
            total_runs += 1
            log(f"Progress: {current_progress}/{total_accounts} | Success rate: {calculate_success_rate()}%")
            time.sleep(2)  # Small delay between accounts

        automation_running = False
        log(f"🎉 Automation completed! Final success rate: {calculate_success_rate()}%")
    except Exception as e:
        log(f"Fatal error: {e}")
        automation_running = False

@app.route('/save_log', methods=['POST'])
def save_log():
    try:
        with open('log.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_lines))
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

def get_auth_credential(account_data, format_type):
    """Get the appropriate authentication credential based on format type"""
    format_mapping = {
        'email': account_data.get('email', ''),
        'username': account_data.get('username', ''),
        'phone': account_data.get('phone', ''),
        'cookies': account_data.get('cookies', ''),
        'privatekey': account_data.get('privatekey', ''),
        'recoveryemail': account_data.get('recoverymail', ''),
        'recoverymail': account_data.get('recoverymail', '')
    }
    
    credential = format_mapping.get(format_type, '')
    if format_type in ['email', 'username', 'phone'] and credential:
        return credential
    elif format_type == 'cookies' and credential and credential != '[]':
        return credential
    elif format_type in ['privatekey'] and credential:
        return credential
    
    # Fallback: if requested format not available, try username or email
    return account_data.get('username', '') or account_data.get('email', '')

def perform_automation_action(driver, platform, category, account_data, format_type, mention, format_input=""):
    """Perform the automation action based on category"""
    try:
        # Get authentication credentials
        username = account_data.get('username', '')
        email = account_data.get('email', '')
        password = account_data.get('privatekey', '')
        cookies_raw = account_data.get('cookies', '')
        
        # Choose login credential based on format
        login_credential = get_auth_credential(account_data, format_type)
        if not login_credential:
            log(f"No valid {format_type} credential found")
            return False
            
        # Navigate to platform
        url = PLATFORM_URLS.get(platform, "https://facebook.com")
        driver.get(url)
        log(f"Navigated to {platform}")
        
        # Attempt authentication
        auth_success = authenticate_user(driver, platform, login_credential, password, cookies_raw, format_type)
        if not auth_success:
            log(f"Authentication failed for {login_credential}")
            return False
            
        log(f"✅ Authentication successful for {login_credential}")
        
        # Perform the category-specific action
        target = format_input if format_input else mention  # Use format_input if provided, otherwise use mention
        if category == 'login':
            log("Login test completed successfully")
            return True
        elif category == 'comment':
            return perform_comment_action(driver, platform, target)
        elif category == 'like':
            return perform_like_action(driver, platform, target)
        elif category == 'follow':
            return perform_follow_action(driver, platform, target)
        elif category == 'unfollow':
            return perform_unfollow_action(driver, platform, target)
        elif category == 'share':
            return perform_share_action(driver, platform, target)
        elif category == 'message':
            return perform_message_action(driver, platform, target)
        elif category == 'join-group':
            return perform_join_group_action(driver, platform, target)
        elif category == 'leave-group':
            return perform_leave_group_action(driver, platform, target)
        elif category == 'scrape-data':
            return perform_scrape_action(driver, platform, target)
        else:
            log(f"Unknown category: {category}")
            return False
            
    except Exception as e:
        log(f"Error in perform_automation_action: {e}")
        return False

def authenticate_user(driver, platform, login_credential, password, cookies_raw, format_type):
    """Handle user authentication based on platform and format"""
    try:
        # Try cookie authentication first if available
        if format_type == 'cookies' and cookies_raw and cookies_raw != '[]':
            try:
                cookies = json.loads(cookies_raw)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
                time.sleep(3)
                
                # Check if login was successful (no login form visible)
                if platform == "facebook" and "login" not in driver.current_url.lower():
                    log("Cookie authentication successful")
                    return True
                elif platform == "instagram" and "accounts" not in driver.current_url.lower():
                    log("Cookie authentication successful")
                    return True
                elif platform == "tiktok" and "login" not in driver.current_url.lower():
                    log("Cookie authentication successful")
                    return True
            except Exception as e:
                log(f"Cookie authentication failed: {e}")
        
        # Fallback to username/password authentication
        if platform == "facebook":
            return login_facebook(driver, login_credential, password)
        elif platform == "instagram":
            return login_instagram(driver, login_credential, password)
        elif platform == "tiktok":
            return login_tiktok(driver, login_credential, password)
        else:
            log(f"Unsupported platform: {platform}")
            return False
            
    except Exception as e:
        log(f"Authentication error: {e}")
        return False

def login_facebook(driver, credential, password):
    """Handle Facebook login"""
    try:
        driver.get("https://www.facebook.com/login")
        time.sleep(3)
        
        email_input = driver.find_element(By.ID, "email")
        pass_input = driver.find_element(By.ID, "pass")
        
        email_input.send_keys(credential)
        pass_input.send_keys(password)
        pass_input.submit()
        time.sleep(5)
        
        if "login" not in driver.current_url.lower():
            return True
        return False
    except Exception as e:
        log(f"Facebook login error: {e}")
        return False

def login_instagram(driver, credential, password):
    """Handle Instagram login"""
    try:
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)
        
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        
        username_input.send_keys(credential)
        password_input.send_keys(password)
        password_input.submit()
        time.sleep(5)
        
        if "login" not in driver.current_url.lower() and "challenge" not in driver.current_url.lower():
            return True
        return False
    except Exception as e:
        log(f"Instagram login error: {e}")
        return False

def login_tiktok(driver, credential, password):
    """Handle TikTok login"""
    try:
        driver.get("https://www.tiktok.com/login/phone-or-email/email")
        time.sleep(5)
        
        email_input = driver.find_element(By.NAME, "email")
        pass_input = driver.find_element(By.NAME, "password")
        
        email_input.send_keys(credential)
        pass_input.send_keys(password)
        pass_input.submit()
        time.sleep(5)
        
        if "login" not in driver.current_url.lower() and "verify" not in driver.current_url.lower():
            return True
        return False
    except Exception as e:
        log(f"TikTok login error: {e}")
        return False

# Action-specific functions
def perform_comment_action(driver, platform, target):
    """Perform commenting action"""
    log(f"Performing comment action on {platform}")
    if not target:
        log("No target or comment specified")
        return False
        
    # Parse target - could be post URL or comment text
    if target.startswith('http'):
        # Target is a post URL
        post_url = target
        comment_text = "Great post! 👍"  # Default comment
    else:
        # Target is comment text, need to find posts to comment on
        comment_text = target
        post_url = None
        
    try:
        if platform == "instagram":
            if post_url:
                # Navigate to specific post
                driver.get(post_url)
                time.sleep(3)
            else:
                # Navigate to home feed and comment on first post
                driver.get("https://www.instagram.com/")
                time.sleep(3)
                
            # Find comment input field
            comment_inputs = driver.find_elements(By.XPATH, "//textarea[@placeholder='Add a comment...']")
            if comment_inputs:
                comment_inputs[0].send_keys(comment_text)
                # Find and click post button
                post_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Post')]")
                if post_buttons:
                    post_buttons[0].click()
                    log(f"✅ Successfully posted comment: '{comment_text}'")
                    return True
                    
        elif platform == "facebook":
            if post_url:
                driver.get(post_url)
            else:
                driver.get("https://www.facebook.com/")
            time.sleep(3)
            # Add Facebook-specific comment logic here
            log(f"✅ Facebook comment simulated: '{comment_text}'")
            return True
            
        elif platform == "tiktok":
            if post_url:
                driver.get(post_url)
            else:
                driver.get("https://www.tiktok.com/foryou")
            time.sleep(3)
            # Add TikTok-specific comment logic here
            log(f"✅ TikTok comment simulated: '{comment_text}'")
            return True
            
    except Exception as e:
        log(f"❌ Error posting comment: {e}")
        return False

def perform_like_action(driver, platform, mention):
    """Perform like action"""
    log(f"Performing like action on {platform}")
    if mention:
        log(f"Target posts: {mention}")
    # Add specific liking logic here
    time.sleep(2)
    log("Like action simulated")
    return True

def perform_follow_action(driver, platform, target):
    """Perform follow action"""
    log(f"Performing follow action on {platform}")
    if not target:
        log("No target users specified")
        return False
        
    # Parse target users (comma-separated)
    users_to_follow = [user.strip() for user in target.split(',') if user.strip()]
    log(f"Target users: {users_to_follow}")
    
    success_count = 0
    for user in users_to_follow:
        try:
            if platform == "instagram":
                # Navigate to user's profile
                profile_url = f"https://www.instagram.com/{user}/"
                driver.get(profile_url)
                time.sleep(3)
                
                # Find and click follow button
                follow_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Follow')]")
                if follow_buttons:
                    follow_buttons[0].click()
                    log(f"✅ Successfully followed @{user}")
                    success_count += 1
                    time.sleep(2)  # Delay between follows
                else:
                    log(f"❌ Follow button not found for @{user}")
                    
            elif platform == "facebook":
                # Facebook follow logic
                profile_url = f"https://www.facebook.com/{user}"
                driver.get(profile_url)
                time.sleep(3)
                # Add Facebook-specific follow logic here
                log(f"✅ Facebook follow simulated for {user}")
                success_count += 1
                
            elif platform == "tiktok":
                # TikTok follow logic
                profile_url = f"https://www.tiktok.com/@{user}"
                driver.get(profile_url)
                time.sleep(3)
                # Add TikTok-specific follow logic here
                log(f"✅ TikTok follow simulated for {user}")
                success_count += 1
                
        except Exception as e:
            log(f"❌ Error following @{user}: {e}")
            
    log(f"Follow action completed: {success_count}/{len(users_to_follow)} successful")
    return success_count > 0

def perform_unfollow_action(driver, platform, mention):
    """Perform unfollow action"""
    log(f"Performing unfollow action on {platform}")
    # Add specific unfollowing logic here
    time.sleep(2)
    log("Unfollow action simulated")
    return True

def perform_share_action(driver, platform, mention):
    """Perform share action"""
    log(f"Performing share action on {platform}")
    if mention:
        log(f"Target content: {mention}")
    # Add specific sharing logic here
    time.sleep(2)
    log("Share action simulated")
    return True

def perform_message_action(driver, platform, mention):
    """Perform message action"""
    log(f"Performing message action on {platform}")
    if mention:
        log(f"Target users/Message: {mention}")
    # Add specific messaging logic here
    time.sleep(2)
    log("Message action simulated")
    return True

def perform_join_group_action(driver, platform, mention):
    """Perform join group action"""
    log(f"Performing join group action on {platform}")
    if mention:
        log(f"Target groups: {mention}")
    # Add specific group joining logic here
    time.sleep(2)
    log("Join group action simulated")
    return True

def perform_leave_group_action(driver, platform, mention):
    """Perform leave group action"""
    log(f"Performing leave group action on {platform}")
    # Add specific group leaving logic here
    time.sleep(2)
    log("Leave group action simulated")
    return True

def perform_scrape_action(driver, platform, mention):
    """Perform data scraping action"""
    log(f"Performing data scraping on {platform}")
    if mention:
        log(f"Scrape target: {mention}")
    # Add specific scraping logic here
    time.sleep(2)
    log("Data scraping simulated")
    return True

@app.route('/delete_all_files', methods=['POST'])
def delete_all_files():
    """Delete all files in accounts, proxies, and comments folders"""
    folders = [ACCOUNTS_FOLDER, PROXIES_FOLDER, COMMENTS_FOLDER]
    deleted_files = 0
    for folder in folders:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_files += 1
                log(f"Deleted file: {file_path}")
    flash(f"All files deleted from accounts, proxies, and comments folders! ({deleted_files} files)", "success")
    return jsonify({'status': 'deleted', 'count': deleted_files})

@app.route('/delete_accounts_folder', methods=['POST'])
def delete_accounts_folder():
    """Delete all files in the uploads/accounts folder"""
    deleted_count = 0
    for filename in os.listdir(ACCOUNTS_FOLDER):
        file_path = os.path.join(ACCOUNTS_FOLDER, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            deleted_count += 1
            log(f"Deleted account file: {filename}")
    flash(f"All account files deleted from accounts folder! ({deleted_count} files)", "success")
    return jsonify({'status': 'deleted', 'count': deleted_count})

@app.route('/accounts/<filename>')
def download_account_file(filename):
    """Serve account file for download/view"""
    return send_from_directory(ACCOUNTS_FOLDER, filename)

if __name__  == "__main__":
    app.run(debug=True)