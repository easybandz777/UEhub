# 🔍 Sentry Error Tracking Setup Guide

This guide will help you set up Sentry error tracking for both the frontend (Next.js) and backend (FastAPI) of UE Hub.

## 📋 Prerequisites

1. Create a free Sentry account at [sentry.io](image.pngdis properly ??
https://sentry.io)
2. Create a new organization (or use existing)
3. Create two projects: one for frontend, one for backend

## 🚀 Step 1: Create Sentry Projects

### Frontend Project (Next.js)
1. Go to Sentry Dashboard → Projects → Create Project
2. Select **Next.js** as the platform
3. Name it `ue-hub-frontend`
4. Copy the DSN (looks like `https://xxx@xxx.ingest.sentry.io/xxx`)

### Backend Project (FastAPI)
1. Create another project
2. Select **FastAPI** or **Python** as the platform
3. Name it `ue-hub-backend`
4. Copy the DSN

## 🔧 Step 2: Configure Environment Variables

### For Vercel (Frontend)
Add these environment variables in your Vercel dashboard:

```bash
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
SENTRY_ORG=your-sentry-org-name
SENTRY_PROJECT=ue-hub-frontend
```

### For Fly.io (Backend)
Set these secrets for your Fly.io app:

```bash
flyctl secrets set SENTRY_DSN="https://your-backend-dsn@sentry.io/project-id" -a uehub
flyctl secrets set SENTRY_ORG="your-sentry-org-name" -a uehub
flyctl secrets set SENTRY_PROJECT="ue-hub-backend" -a uehub
```

### For Local Development
Copy the example files and fill in your values:

```bash
# Frontend
cp frontend/env.example frontend/.env.local

# Backend
cp backend/env.example backend/.env
```

## 📊 Step 3: What You Get

### Frontend Monitoring
- **JavaScript Errors**: Unhandled exceptions and promise rejections
- **Performance Monitoring**: Page load times, API call durations
- **User Sessions**: Replay sessions with errors
- **Custom Events**: Track user actions and business metrics

### Backend Monitoring
- **API Errors**: FastAPI exceptions and HTTP errors
- **Database Issues**: SQLAlchemy query problems
- **Performance**: Slow API endpoints and database queries
- **Background Jobs**: RQ worker failures

## 🎯 Step 4: Testing the Setup

### Test Frontend Error Tracking
Add this to any page to test:

```javascript
// In a React component
const testSentryError = () => {
  throw new Error("Test Sentry Frontend Error!");
};

// In a button click handler
<button onClick={testSentryError}>Test Sentry</button>
```

### Test Backend Error Tracking
Add this to any FastAPI endpoint:

```python
@app.get("/test-sentry")
async def test_sentry():
    raise Exception("Test Sentry Backend Error!")
```

## 📈 Step 5: Advanced Configuration

### Source Maps (Frontend)
For better error tracking, enable source map uploads:

1. Get a Sentry Auth Token from your Sentry settings
2. Add to Vercel environment variables:
   ```
   SENTRY_AUTH_TOKEN=your-auth-token
   ```

### Custom Context (Backend)
Use the helper functions in your code:

```python
from app.core.sentry import set_user, set_context, capture_exception

# Set user context
set_user(user_id="123", email="user@example.com")

# Add custom context
set_context("business_context", {
    "inventory_item_id": "item-123",
    "training_module": "osha-safety"
})

# Capture exceptions with context
try:
    # Your code here
    pass
except Exception as e:
    capture_exception(e)
```

## 🔍 Step 6: Monitoring Best Practices

### What to Monitor
- **Critical User Flows**: Login, inventory updates, training completion
- **API Performance**: Slow database queries, external API calls
- **Business Metrics**: Failed training submissions, inventory discrepancies

### Alert Setup
1. Go to Sentry → Alerts → Create Alert
2. Set up alerts for:
   - High error rates (>5 errors/minute)
   - New error types
   - Performance degradation

### Dashboard Setup
Create custom dashboards for:
- Error rates by module (auth, inventory, training)
- Performance metrics by endpoint
- User impact analysis

## 🚨 Troubleshooting

### Common Issues

**Frontend errors not appearing:**
- Check that `NEXT_PUBLIC_SENTRY_DSN` is set correctly
- Verify the DSN format includes `https://`
- Check browser console for Sentry initialization errors

**Backend errors not appearing:**
- Verify `SENTRY_DSN` environment variable is set
- Check application logs for Sentry initialization messages
- Ensure the DSN corresponds to the backend project

**Source maps not working:**
- Verify `SENTRY_AUTH_TOKEN` is set
- Check that the Sentry organization and project names match
- Review build logs for source map upload errors

## 📚 Additional Resources

- [Sentry Next.js Documentation](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Sentry FastAPI Documentation](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Sentry Alerts Guide](https://docs.sentry.io/product/alerts/)

## 🎉 You're All Set!

Once configured, Sentry will automatically:
- Capture and report errors from both frontend and backend
- Monitor performance and identify slow operations
- Provide detailed stack traces and user context
- Send alerts when issues occur

Your UE Hub application now has enterprise-grade error tracking and monitoring! 🚀
