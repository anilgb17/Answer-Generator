# 🚀 Getting Started with Answer Generator

Welcome! This guide will help you set up and run the Answer Generator in just a few minutes.

## 📋 Prerequisites

Before you begin, make sure you have:
- ✅ Docker and Docker Compose installed
- ✅ Python 3.11+ installed
- ✅ Git installed

## 🎯 Quick Start (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/anilgb17/Answer-Generator.git
cd Answer-Generator
```

### Step 2: Setup Environment

**Windows:**
```bash
setup_env.bat
```

**Linux/Mac:**
```bash
python setup_env.py
```

This will:
- Create your `backend/.env` file
- Generate secure encryption keys
- Prepare the file for your API keys

### Step 3: Add Your API Key

Open `backend/.env` and add at least ONE API key.

**Recommended: Gemini (FREE)**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy and paste into `.env`:
   ```bash
   GEMINI_API_KEY=your_key_here
   ```

### Step 4: Start the Application

**Windows:**
```bash
start-project.bat
```

**Linux/Mac:**
```bash
docker-compose up -d
```

### Step 5: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🎉 You're Ready!

You can now:
1. Upload questions (text, PDF, or images)
2. Select your preferred language
3. Generate comprehensive answers
4. Download as PDF

## 📚 Next Steps

- **[API Keys Guide](SETUP_API_KEYS.md)** - Detailed API setup instructions
- **[README](README.md)** - Full project documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to production

## 🆘 Need Help?

### Common Issues

**"No API key configured"**
- Make sure you added a key to `backend/.env`
- Check for typos
- Restart the application: `docker-compose restart`

**"Port already in use"**
- Stop other services using ports 3000, 8000, or 6379
- Or change ports in `docker-compose.yml`

**"Docker not found"**
- Install Docker Desktop from https://www.docker.com/products/docker-desktop

### Get Support

- 📖 Check the [documentation](README.md)
- 🐛 Report issues: https://github.com/anilgb17/Answer-Generator/issues
- 💬 Ask questions in GitHub Discussions

## 🔒 Security Note

Your `.env` file contains sensitive API keys and is automatically protected:
- ✅ Excluded from git (in `.gitignore`)
- ✅ Never committed to repository
- ✅ Safe to add your real keys

**Never share your `.env` file or commit it to version control!**

---

**Happy generating! 🎓✨**
