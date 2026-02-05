# 🔐 API Keys Setup Guide

Your `.env` file has been secured with new keys. Follow these steps to get your API keys:

## ✅ Security Keys Updated
- ✅ New SECRET_KEY generated
- ✅ New ENCRYPTION_KEY generated
- ✅ Old Gemini API key removed

## 📝 Next Steps

### 1. Get a NEW Gemini API Key (FREE - Recommended)
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the new key
5. **IMPORTANT**: Delete your old key from the console for security

### 2. Update Your .env File
Open `backend/.env` and add your new Gemini API key:
```bash
GEMINI_API_KEY=your_new_gemini_key_here
```

### 3. Optional: Get Other API Keys

#### Perplexity (FREE tier available)
- URL: https://www.perplexity.ai/settings/api
- Free tier: 5 requests/day
- Add to: `PERPLEXITY_API_KEY=`

#### OpenAI (PAID)
- URL: https://platform.openai.com/api-keys
- Requires payment method
- Add to: `OPENAI_API_KEY=`

#### Anthropic Claude (PAID)
- URL: https://console.anthropic.com/
- Requires payment method
- Add to: `ANTHROPIC_API_KEY=`

## 🚀 Start Your Application

After adding at least one API key (Gemini recommended):

```bash
# Start the application
docker-compose up -d

# Or use the batch file
start-project.bat
```

## 🔒 Security Best Practices

1. ✅ Never commit `.env` file to git (already protected)
2. ✅ Never share your API keys publicly
3. ✅ Rotate keys regularly
4. ✅ Delete old/compromised keys immediately
5. ✅ Use different keys for development and production

## ⚠️ Important Notes

- Your `.env` file is protected by `.gitignore` and won't be pushed to GitHub
- The old Gemini key should be deleted from Google's console
- At least one AI provider API key is required for the app to work
- Gemini is recommended as it's FREE and has good performance

## 🆘 Need Help?

If you encounter issues:
1. Check that your API key is valid
2. Ensure no extra spaces in the `.env` file
3. Restart the application after updating keys
4. Check logs: `docker-compose logs backend`

---
**Status**: 🔴 API keys needed - Add at least one API key to start using the application
