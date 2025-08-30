# Social Media Automation Tool

## Recent Updates - Account Upload Enhancement

### New Features:

1. **Enhanced Account Folder Upload** - Now supports uploading entire folders with multiple account files
2. **Multiple File Format Support** - Supports 3 different account file formats
3. **Automatic Table Updates** - Account table automatically updates when you upload account files
4. **Better Error Handling** - Improved validation and error messages

### Supported Account File Formats:

#### Format 1: Key-Value (Recommended)

```
username:john@email.com
password:mypass123
cookies:[{"name":"session","value":"abc123"}]
email:john@email.com
mailpass:emailpass123
phone:+1234567890
recoverymail:recovery@email.com
```

#### Format 2: Pipe Separated

```
username|password|cookies|email|mailpass|phone|recoverymail
```

#### Format 3: Comma Separated

```
username,password,cookies,email,mailpass,phone,recoverymail
```

### How to Use:

1. **Prepare Account Files**: Create individual `.txt` files for each account using one of the supported formats above
2. **Create Account Folder**: Put all account files in a single folder
3. **Upload**: Click the folder icon next to "account folder" and select your folder
4. **Verify**: Check that the account table populates with your account information
5. **Configure**: Set your automation settings (platform, threads, etc.)
6. **Run**: Click Start to begin automation

### Sample Files:

The application includes sample account files in the `uploads/accounts/` folder:

- `sample_account1.txt` - Key-value format
- `sample_account2.txt` - Pipe separated format
- `sample_account3.txt` - Comma separated format

### Installation:

```bash
pip install -r requirements.txt
python app.py
```

### Access:

Open your browser and go to `http://127.0.0.1:5000`

### Supported Platforms:

- Facebook
- Instagram
- TikTok

### Features:

- Multi-threaded automation
- Cookie-based login support
- Real-time progress tracking
- Success rate calculation
- Live logging
- Proxy support
- Headless browser option

## ✨ **Enhanced Category & Format System**

### **Category Dropdown - Automation Actions:**

- **Login** - Test account credentials and authentication
- **Comment** - Post comments on content/posts
- **Like** - Automatically like posts and content
- **Follow** - Follow target users/accounts
- **Unfollow** - Unfollow users (account cleanup)
- **Share** - Share/repost content
- **Message** - Send direct messages to users
- **Join Group** - Join Facebook groups/communities
- **Leave Group** - Leave groups (cleanup)
- **Scrape Data** - Extract user data, posts, comments

### **Format Dropdown - Authentication Method:**

- **Email** - Use email field for login
- **Username** - Use username field for login
- **Phone** - Use phone number for mobile login
- **Cookies** - Use saved cookies for authentication
- **Private Key** - Use password field for login
- **Recovery Email** - Use recovery email field

### **How They Work Together:**

```
Category: "Comment" + Format: "Cookies" =
→ Use cookie authentication to log in and post comments

Category: "Follow" + Format: "Email" =
→ Use email login to follow target users

Category: "Like" + Format: "Username" =
→ Use username login to like posts

Category: "Scrape Data" + Format: "Phone" =
→ Use phone login to scrape user information
```

### **Smart Authentication System:**

1. **Cookie Priority**: If format is "Cookies" and cookies exist, uses cookie authentication first
2. **Fallback Login**: If cookies fail, falls back to username/password login
3. **Format Selection**: Uses the selected format field as the login credential
4. **Auto-Detection**: If selected format is empty, automatically uses username or email

### **Example Usage:**

- Set **Category: "Comment"** and **Format: "Email"** to post comments using email login
- Set **Category: "Follow"** and **Format: "Cookies"** to follow users using saved cookies
- Set **Category: "Login"** and **Format: "Username"** to test username/password authentication

### **Logs Show Everything:**

- Which authentication method was used
- Which category action was performed
- Success/failure for each account
- Detailed progress and error messages
