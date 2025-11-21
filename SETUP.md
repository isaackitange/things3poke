# Things 3 Email MCP Server for Poke

**Works 24/7 from any server - your laptop can be off! 🎉**

## How It Works

Email is like sending a letter to Things' mailbox. The server writes the letter (email), mails it, and Things picks it up automatically.

```
You text Poke → MCP server sends email → Things inbox receives task
```

## Quick Setup (3 Steps)

### Step 1: Get Gmail App Password

1. Create or use a Gmail account
2. Go to Google Account → Security → 2-Step Verification (enable it)
3. Go to Security → App passwords
4. Generate new app password for "Mail"
5. Save the 16-character password (looks like: `abcd efgh ijkl mnop`)

### Step 2: Deploy to Replit (Easiest)

1. Go to [replit.com](https://replit.com)
2. Create new Python repl
3. Upload `things-email-mcp-server.py`
4. Add these **Secrets** (in left sidebar):
   - `SMTP_USER` = your Gmail address
   - `SMTP_PASSWORD` = the 16-char app password from Step 1
5. Click Run

Replit will give you a URL like: `https://your-repl-name.username.repl.co`

### Step 3: Connect to Poke

1. Go to [poke.com](https://poke.com) web app
2. Click Integrations
3. Click "Custom Connection"
4. Select "MCP URL"
5. Paste your Replit URL
6. Save

## Test It!

Text Poke:
- "Add a task to Things: Buy milk"
- "Add 'Write report' to Things under Work heading"
- "Add a task 'Plan vacation' with checklist: book flight, reserve hotel, plan itinerary"

## What Poke Can Do

**1. Simple tasks**
```
"Add task to Things: Call dentist"
```

**2. Tasks with notes**
```
"Add to Things: Meeting prep
Notes: Review slides, print handouts"
```

**3. Tasks under headings** (Projects/Areas)
```
"Add 'Buy groceries' to Things under Personal"
```

**4. Tasks with checklists**
```
"Add project to Things: Weekend cleanup
Checklist: vacuum, dishes, laundry"
```

## Alternative Hosting Options

### Railway
1. Create account at railway.app
2. New Project → Deploy from GitHub
3. Add environment variables
4. Use generated URL

### Heroku
```bash
heroku create your-app-name
heroku config:set SMTP_USER=your@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password
git push heroku main
```

### Your Own Server
```bash
export SMTP_USER=your@gmail.com
export SMTP_PASSWORD=your-app-password
python3 things-email-mcp-server.py
```

## Email Format Reference

Things reads emails like this:

**Subject line** = Task title
**Body** = Notes

**Special formats:**
- `Heading: Task` in subject = adds to that heading
- Lines starting with `-` = checklist items

## Troubleshooting

**"SMTP not configured"**
- Make sure you added SMTP_USER and SMTP_PASSWORD secrets

**"Authentication failed"**
- Use app password, not regular Gmail password
- Enable 2-Step Verification first

**"Poke can't connect to server"**
- Check your server URL is public and starts with `https://`
- Make sure server is running

**Tasks not appearing in Things**
- Check your Things Cloud email is correct: `add-to-things-wqfcr1hf2k2vp3su8h4z2@things.email`
- Make sure Things Cloud sync is enabled in Things settings

## Privacy Note

Your Gmail credentials are stored as environment variables on your hosting service. The server only uses them to send emails to Things. Choose a trusted hosting provider (like Replit, Railway, or Heroku).

## Why This Is Better Than URL Schemes

✅ Works 24/7 (laptop can be off)
✅ Works from anywhere
✅ Officially supported by Things
✅ No risk of data corruption
✅ Simple setup

## Advanced: Using Other Email Services

Don't want to use Gmail? Update these environment variables:

**Outlook/Hotmail:**
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**ProtonMail:** Use ProtonMail Bridge

**SendGrid/Mailgun:** Configure their SMTP settings
