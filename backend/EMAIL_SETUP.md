# 📧 Email Configuration Guide

This guide explains how to configure email for password reset functionality.

---

## 🎯 Why Email Configuration?

Email is used for:
- **Password reset links** - Send secure reset tokens to users
- **Account verification** (optional future feature)
- **Notifications** (optional future feature)

---

## 📮 Gmail Setup (Recommended)

### Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/security
2. Under "Signing in to Google", select **2-Step Verification**
3. Follow the prompts to enable it

### Step 2: Generate App Password

1. Go to App Passwords: https://myaccount.google.com/apppasswords
2. You might need to sign in again
3. Select **Mail** for the app
4. Select **Other (Custom name)** for the device
5. Enter: `StudyAI Backend`
6. Click **Generate**
7. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

### Step 3: Update .env File

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=youremail@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=youremail@gmail.com
EMAIL_FROM_NAME=AI Study Assistant
```

**Important**: Use the 16-character App Password, NOT your regular Gmail password!

---

## 📮 Other Email Providers

### Outlook / Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=youremail@outlook.com
SMTP_PASSWORD=your-outlook-password
EMAIL_FROM=youremail@outlook.com
EMAIL_FROM_NAME=AI Study Assistant
```

### Yahoo Mail

```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=youremail@yahoo.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=youremail@yahoo.com
EMAIL_FROM_NAME=AI Study Assistant
```

**Note**: Yahoo also requires App Password. Generate at: https://login.yahoo.com/account/security

### Custom SMTP Server

```env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=AI Study Assistant
```

---

## 🧪 Testing Email Configuration

### Test 1: Python Script

Create a test file `test_email.py`:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your email settings
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
EMAIL_FROM = "your-email@gmail.com"
EMAIL_TO = "your-email@gmail.com"  # Send to yourself for testing

def send_test_email():
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = "Test Email from AI Study Assistant"
        
        body = "If you receive this email, your SMTP configuration is working! 🎉"
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    send_test_email()
```

Run the test:
```powershell
python test_email.py
```

### Test 2: Via API

1. Start your backend server
2. Register a user
3. Use the forgot password endpoint:

```powershell
curl -X POST http://localhost:8000/api/v1/auth/forgot-password `
  -H "Content-Type: application/json" `
  -d '{"email": "your-email@gmail.com"}'
```

4. Check your email for the reset link

---

## 🔧 Troubleshooting

### Error: "Authentication failed"

**Solutions**:
1. ✅ Use App Password (not regular password) for Gmail/Yahoo
2. ✅ Check if 2-Step Verification is enabled
3. ✅ Regenerate App Password if needed
4. ✅ Check SMTP_USER matches the email account

### Error: "Connection refused"

**Solutions**:
1. ✅ Check SMTP_HOST is correct
2. ✅ Try port 465 instead of 587 (SSL vs TLS)
3. ✅ Check firewall/antivirus blocking port 587
4. ✅ Verify internet connection

### Error: "Sender address rejected"

**Solutions**:
1. ✅ EMAIL_FROM must match SMTP_USER for most providers
2. ✅ Verify email account is active
3. ✅ Check if SMTP service is enabled for your account

### Gmail: "Less secure app access"

**Solution**: 
- Gmail deprecated "less secure apps" in 2022
- **You MUST use App Password** (not the old method)
- Follow Step 2 above to generate App Password

---

## 🔐 Security Best Practices

### 1. Never Commit .env File
```
# Already in .gitignore
.env
```

### 2. Use Environment Variables in Production

For deployment platforms:

**Heroku**:
```bash
heroku config:set SMTP_USER=your-email@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password
```

**Render**:
- Go to Environment tab
- Add SMTP_USER, SMTP_PASSWORD as secret variables

**Railway**:
- Go to Variables tab
- Add each email variable

### 3. Rotate App Passwords Regularly

- Regenerate App Password every 6 months
- Revoke old App Passwords

### 4. Use Dedicated Email Account

Consider creating a separate Gmail account for your application:
- `studyai.noreply@gmail.com`
- Only for sending automated emails
- Not your personal email

---

## 📋 Complete .env Email Section

```env
# ============================================
# EMAIL CONFIGURATION (FOR PASSWORD RESET)
# ============================================
# GMAIL SETUP:
# 1. Enable 2-Step Verification: https://myaccount.google.com/security
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Copy the 16-character password below

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=AI Study Assistant
```

---

## ✅ Verification Checklist

- [ ] 2-Step Verification enabled (Gmail/Yahoo)
- [ ] App Password generated
- [ ] SMTP_USER is correct email address
- [ ] SMTP_PASSWORD is App Password (not regular password)
- [ ] EMAIL_FROM matches SMTP_USER
- [ ] Test email sent successfully
- [ ] .env file NOT committed to Git

---

## 🎉 All Set!

Once configured correctly, your application can:
- ✅ Send password reset emails
- ✅ Use professional "from" name
- ✅ Deliver emails reliably

---

## 📞 Need Help?

Common email providers documentation:
- **Gmail**: https://support.google.com/mail/answer/185833
- **Outlook**: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings
- **Yahoo**: https://help.yahoo.com/kb/SLN4075.html
