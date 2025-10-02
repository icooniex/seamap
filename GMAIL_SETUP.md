## Gmail SMTP Setup Instructions

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled

### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Other (Custom name)" as device
4. Enter "SeaMap Django" as the custom name
5. Click "Generate"
6. Copy the 16-character app password (e.g., "abcd efgh ijkl mnop")

### Step 3: Set Environment Variables
Create a .env file in your project root with:
```
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
```

### Step 4: Test Email Configuration
Run the test command to verify email settings work correctly.