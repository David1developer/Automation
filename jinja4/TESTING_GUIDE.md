# Sample Test Accounts

## 📋 Account Testing Guide

The following sample accounts have been created to test the social media automation tool:

### 🔐 **Sample Accounts Created:**

#### 1. **test_user1.txt** (Key-Value Format)

- **Username:** testuser1@gmail.com
- **Password:** testpass123
- **Platform:** Instagram (has Instagram cookies)
- **Format:** Key-value pairs (recommended format)

#### 2. **social_bot2.txt** (Key-Value Format)

- **Username:** socialbot2@outlook.com
- **Password:** botpass456
- **Platform:** Facebook (has Facebook cookies)
- **Format:** Key-value pairs

#### 3. **auto_user3.txt** (Pipe-Separated Format)

- **Username:** autouser3@yahoo.com
- **Password:** autopass789
- **Platform:** TikTok (has TikTok cookies)
- **Format:** Pipe-separated (|)

#### 4. **demo_user4.txt** (Comma-Separated Format)

- **Username:** demouser4@protonmail.com
- **Password:** demopass321
- **Platform:** Any (no cookies)
- **Format:** Comma-separated

#### 5. **marketing_bot.txt** (Key-Value Format)

- **Username:** marketingbot@business.com
- **Password:** marketing2024
- **Platform:** Facebook (business account)
- **Format:** Key-value pairs

#### 6. **influencer_account.txt** (Key-Value Format)

- **Username:** influencer123@gmail.com
- **Password:** influence2024
- **Platform:** Instagram (influencer account)
- **Format:** Key-value pairs

### 📝 **Additional Test Files:**

#### **sample_comments.txt**

Contains 10 sample comments for testing comment automation:

- "Great post! 👍"
- "Love this content! 💖"
- "Amazing work! 🔥"
- And more...

#### **sample_proxies.txt**

Contains 5 sample proxy addresses for testing proxy functionality.

### 🧪 **How to Test:**

#### **Basic Login Test:**

1. Select **Category:** "Login"
2. Select **Format:** "Email" or "Username"
3. Select **Platform:** Any (Facebook, Instagram, TikTok)
4. Click **Start** to test login functionality

#### **Follow Test:**

1. Select **Category:** "Follow Users"
2. Select **Format:** "Cookies" (for faster auth)
3. **Input Format:** "testuser, demouser, sampleuser"
4. Click **Start** to test follow functionality

#### **Comment Test:**

1. Select **Category:** "Comment"
2. Select **Format:** "Email"
3. **Input Format:** "This is a test comment! 🔥"
4. Click **Start** to test comment functionality

#### **Cookie Authentication Test:**

1. Select **Category:** "Login"
2. Select **Format:** "Cookies"
3. Click **Start** to test cookie-based authentication

### 🔄 **Testing Different Formats:**

#### **Test Email Authentication:**

- Use accounts: test_user1, social_bot2, marketing_bot
- Format: "Email"

#### **Test Username Authentication:**

- Use any account
- Format: "Username"

#### **Test Cookie Authentication:**

- Use accounts with cookies: test_user1, social_bot2, auto_user3, marketing_bot, influencer_account
- Format: "Cookies"

#### **Test Phone Authentication:**

- Use any account (all have phone numbers)
- Format: "Phone"

### 📊 **Expected Results:**

- **Login Category:** Should show "Login test completed successfully"
- **Follow Category:** Should show "Follow action completed: X/Y successful"
- **Comment Category:** Should show "Successfully posted comment"
- **Other Categories:** Should show simulated success messages

### 🧹 **Clear Table Test (UPDATED):**

#### **🧹 Clear Uploads Button (Yellow):**

- Deletes only uploaded account files
- **Preserves all sample files** (test_user1.txt, social_bot2.txt, etc.)
- Good for testing upload functionality
- Sample files remain for continuous testing

#### **🗑️ Clear All Button (Red):**

- Deletes ALL account files including samples
- Requires confirmation dialog
- Use with caution - will remove sample files
- Complete reset of account table

#### **Testing Clear Functionality:**

1. Upload some test files
2. Click "🧹 Clear Uploads" - only uploaded files deleted
3. Sample files remain in table
4. Click "🗑️ Clear All" - everything deleted (with confirmation)

### 📈 **Monitor Progress:**

- Check the **Runtime Log** for detailed progress
- Watch **Success Rate** percentage
- Monitor **Progress** counter (X/Y)

### ⚠️ **Note:**

These are test accounts with fake credentials. The automation will simulate actions but won't perform real social media interactions since the credentials are not for actual social media accounts.

### 🎯 **Testing Workflow:**

1. **Upload Test:** The accounts are already uploaded
2. **Authentication Test:** Try different format types
3. **Action Test:** Try different categories
4. **Clear Test:** Test the clear table functionality
5. **Reload Test:** Refresh page to see persistence
