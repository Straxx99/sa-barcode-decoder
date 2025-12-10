# PDF417 Barcode API - Deployment Guide

This guide covers deploying your Python PDF417 barcode decoding API to various cloud platforms.

## 📋 Prerequisites

- A GitHub account (for code hosting)
- Account on your chosen cloud platform
- Your API code ready in the `barcode-api` folder

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Easy & Free Tier)

**Pros:**
- Free tier available (500 hours/month)
- Automatic deployments from GitHub
- Very easy setup
- Built-in HTTPS

**Steps:**

1. **Prepare your repository**
   ```bash
   cd C:/Projects/barcode-api
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub repository**
   - Go to github.com and create a new repository
   - Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/barcode-api.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy to Railway**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `barcode-api` repository
   - Railway will auto-detect Python and deploy

4. **Configure Environment**
   - Railway will automatically use `requirements.txt`
   - Your API will be available at: `https://your-app.railway.app`

5. **Update your React app**
   In your React components, update the API URL:
   ```typescript
   const API_URL = 'https://your-app.railway.app';
   ```

---

### Option 2: Render (Free Tier Available)

**Pros:**
- Generous free tier
- Easy deployment
- Built-in HTTPS
- Good for production

**Steps:**

1. **Push code to GitHub** (same as Railway steps 1-2)

2. **Deploy to Render**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: barcode-api
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Add Gunicorn**
   Update `requirements.txt` to include:
   ```
   Flask==3.0.0
   flask-cors==4.0.0
   pdf417decoder==1.0.8
   opencv-python-headless==4.10.0.84
   Pillow>=11.0.0
   numpy>=2.0.0
   gunicorn==21.2.0
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy
   - Your API will be at: `https://barcode-api-xxxx.onrender.com`

**Note:** Free tier sleeps after 15 minutes of inactivity. First request may take 30-60 seconds to wake up.

---

### Option 3: Heroku (Reliable, Paid)

**Pros:**
- Very reliable
- Great documentation
- Easy to scale
- Professional hosting

**Cost:** ~$7/month for basic dyno

**Steps:**

1. **Install Heroku CLI**
   - Download from https://devcenter.heroku.com/articles/heroku-cli
   - Login: `heroku login`

2. **Prepare Procfile**
   Create `Procfile` in your barcode-api folder:
   ```
   web: gunicorn app:app
   ```

3. **Deploy**
   ```bash
   cd C:/Projects/barcode-api
   heroku create barcode-api-sa
   git push heroku main
   ```

4. **Your API will be at**: `https://barcode-api-sa.herokuapp.com`

---

### Option 4: AWS Lambda with API Gateway (Serverless)

**Pros:**
- Pay per use (very cheap for low traffic)
- Scalable
- No server management

**Complexity:** Medium

**Steps:**

1. **Install Zappa**
   ```bash
   pip install zappa
   ```

2. **Configure Zappa**
   Create `zappa_settings.json`:
   ```json
   {
       "production": {
           "app_function": "app.app",
           "aws_region": "us-east-1",
           "project_name": "barcode-api",
           "runtime": "python3.9",
           "s3_bucket": "barcode-api-deployments"
       }
   }
   ```

3. **Deploy**
   ```bash
   zappa deploy production
   ```

4. **Update on changes**
   ```bash
   zappa update production
   ```

---

## 🔧 Production Configuration

### Update Flask for Production

Modify `app.py` for production:

```python
import os

# ... existing imports ...

app = Flask(__name__)
CORS(app, origins=["https://your-react-app.com"])  # Restrict CORS in production

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### Environment Variables

For production deployments, set these environment variables:

- `PORT`: The port your app runs on (set by platform)
- `DEBUG`: Set to `False` in production
- `ALLOWED_ORIGINS`: Your React app URL for CORS

### CORS Configuration

In production, update CORS to only allow your app's domain:

```python
from flask_cors import CORS

# Development
# CORS(app)

# Production
CORS(app, origins=[
    "https://your-app.netlify.app",
    "https://your-app.vercel.app",
    "https://www.yourdomain.com"
])
```

---

## 📱 Update React App

### Update API URL

Create an environment variable in your React app:

**.env.development**
```
VITE_API_URL=http://localhost:5000
```

**.env.production**
```
VITE_API_URL=https://your-api.railway.app
```

### Use in Components

```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// In BarcodeScanner.tsx
<BarcodeScanner
  apiUrl={API_URL}
  onScanSuccess={handleScan}
  onClose={() => setShowScanner(false)}
/>
```

---

## 🧪 Testing Production API

Test your deployed API:

```bash
# Health check
curl https://your-api.railway.app/health

# Test decode (with a base64 image)
curl -X POST https://your-api.railway.app/decode \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,..."}'
```

Or use the HTML test page by updating the API URL in line 110:

```javascript
const API_URL = 'https://your-api.railway.app';
```

---

## 🔒 Security Best Practices

1. **Rate Limiting**
   Add rate limiting to prevent abuse:
   ```bash
   pip install flask-limiter
   ```

   ```python
   from flask_limiter import Limiter
   from flask_limiter.util import get_remote_address

   limiter = Limiter(
       app=app,
       key_func=get_remote_address,
       default_limits=["100 per hour"]
   )

   @app.route('/decode', methods=['POST'])
   @limiter.limit("10 per minute")
   def decode_barcode():
       # ... existing code ...
   ```

2. **API Keys** (Optional)
   For added security, require API keys:
   ```python
   API_KEY = os.environ.get('API_KEY', 'your-secret-key')

   @app.before_request
   def check_api_key():
       if request.path.startswith('/decode'):
           key = request.headers.get('X-API-Key')
           if key != API_KEY:
               return jsonify({'error': 'Invalid API key'}), 401
   ```

3. **HTTPS Only**
   All cloud platforms provide HTTPS automatically. Never use HTTP in production.

---

## 📊 Monitoring

### Railway
- Built-in logs and metrics in dashboard
- View at: https://railway.app/dashboard

### Render
- Logs available in dashboard
- Metrics for response times and errors

### Heroku
- Use Heroku logs: `heroku logs --tail`
- Add monitoring: Heroku Metrics or New Relic

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| **Railway** | 500 hours/month | $5/month | Development & MVP |
| **Render** | 750 hours/month | $7/month | Production |
| **Heroku** | None | $7/month | Enterprise |
| **AWS Lambda** | 1M requests/month | Pay per use | High scale |

---

## 🚨 Troubleshooting

### Issue: Module not found
**Solution:** Ensure all dependencies are in `requirements.txt`

### Issue: App crashes on startup
**Solution:** Check logs:
- Railway: Dashboard → Logs
- Render: Dashboard → Logs
- Heroku: `heroku logs --tail`

### Issue: CORS errors in browser
**Solution:** Update CORS configuration in `app.py`:
```python
CORS(app, origins=["https://your-react-app.com"])
```

### Issue: Slow cold starts (Render free tier)
**Solution:**
- Upgrade to paid tier ($7/month)
- Or implement a keep-alive ping every 10 minutes

### Issue: API timeout
**Solution:** Increase timeout in your React app:
```javascript
const response = await fetch(`${apiUrl}/decode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: base64Image }),
    timeout: 30000  // 30 seconds
});
```

---

## ✅ Recommended Setup (Production-Ready)

For a production South African warranty app:

1. **Deploy API to Render** ($7/month)
   - Reliable uptime
   - No cold starts
   - Good for SA users

2. **Deploy React App to Vercel or Netlify** (Free)
   - Automatic deployments from GitHub
   - Global CDN
   - HTTPS included

3. **Add monitoring**
   - Sentry for error tracking
   - Google Analytics for usage

4. **Estimated Monthly Cost**: $7 for API + $0 for frontend = **$7/month**

---

## 📞 Support

If you encounter issues:
1. Check the platform's status page
2. Review deployment logs
3. Test API locally first: `python app.py`
4. Verify all dependencies are installed

---

## 🎯 Next Steps

1. Choose your deployment platform (recommend Railway for testing, Render for production)
2. Push code to GitHub
3. Deploy using steps above
4. Update React app with production API URL
5. Test with real license disc images
6. Monitor performance and errors

Good luck with your deployment! 🚀
