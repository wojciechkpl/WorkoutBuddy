# Railway Deployment Guide for WorkoutBuddy AI v2.1

This guide covers deploying the AI-powered WorkoutBuddy FastAPI backend with analytics to Railway.

## ✨ Features Included

- 🤖 **AI-Powered Challenges**: GPT-4o-mini generates personalized workouts
- 🎯 **Smart Community Matching**: AI-driven compatibility analysis  
- 💪 **Automated Encouragement**: Personalized motivation messages
- 📊 **Real-time Analytics**: PostHog integration for user insights
- 🧪 **A/B Testing Framework**: Built-in experimentation platform
- 📈 **Cohort Analysis**: Track retention and goal completion rates

## Prerequisites

1. [Railway CLI](https://railway.app/cli) installed
2. Railway account created
3. OpenAI API account (for AI features)
4. PostHog account (for analytics - optional)
5. Git repository connected to Railway

## Quick Deploy

### Option 1: One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Option 2: Manual Deploy

1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Initialize project**
   ```bash
   railway init
   ```

3. **Add PostgreSQL database**
   ```bash
   railway add postgresql
   ```

4. **Deploy the application**
   ```bash
   railway up
   ```

## Configuration

### Required Environment Variables

Railway will automatically set these when you add PostgreSQL:
- `PGHOST` - Database host
- `PGPORT` - Database port (5432)
- `PGDATABASE` - Database name
- `PGUSER` - Database username
- `PGPASSWORD` - Database password

### AI & Analytics Configuration

**Essential variables:**
```bash
# Core application
railway variables set SECRET_KEY=your-super-secret-key-here
railway variables set LOG_LEVEL=INFO
railway variables set RAILWAY_ENVIRONMENT=production

# AI Features (OpenAI)
railway variables set OPENAI_API_KEY=sk-your-openai-api-key-here

# Analytics (PostHog - optional)
railway variables set POSTHOG_API_KEY=phc_your-posthog-project-api-key
railway variables set POSTHOG_HOST=https://app.posthog.com
```

### Getting API Keys

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up/login and navigate to API Keys
3. Create new secret key
4. Copy the key starting with `sk-`
5. **Cost**: ~$0.15 per 1K tokens (very affordable for GPT-4o-mini)

#### PostHog API Key (Optional)
1. Go to [PostHog](https://posthog.com/)
2. Sign up for free account (generous free tier)
3. Create new project
4. Find API key in Project Settings → API Keys
5. Copy the key starting with `phc_`

### Database Migration

After first deployment, run migrations:
```bash
railway run cd backend && python -m alembic upgrade head
```

## Testing the Deployment

### Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "users": 0,
  "active_experiments": 3,
  "ai_service": "operational",
  "analytics": "operational"
}
```

### AI Features Test
```bash
# Test AI challenge generation
curl -X POST "https://your-app.railway.app/challenges/generate?user_id=1&goal_type=cardio"

# Test AI encouragement
curl -X POST "https://your-app.railway.app/encouragement/1"
```

### Analytics Dashboard
```bash
# View cohort analysis
curl https://your-app.railway.app/analytics/cohorts

# View A/B testing experiments
curl https://your-app.railway.app/experiments
```

## Project Structure

The Railway deployment uses these files:

- `Procfile` - Defines how Railway should start the app
- `railway.json` - Railway-specific configuration
- `backend/requirements.txt` - Python dependencies (includes AI/ML libs)
- `backend/app/config.py` - Environment-aware configuration
- `backend/app/ai_services.py` - OpenAI integration
- `backend/app/analytics.py` - PostHog analytics
- `backend/app/ab_testing.py` - A/B testing framework

## Local Development

For local development with AI features:

```bash
# Set environment variables
export OPENAI_API_KEY=sk-your-key-here
export POSTHOG_API_KEY=phc_your-key-here

# Install dependencies
cd backend
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload
```

The app will automatically:
- Use AI features if OpenAI key is provided
- Fall back to template responses if no key
- Track analytics if PostHog key is provided
- Log locally if no analytics key

## Production URLs

After deployment, your API will be available at:

### Core Endpoints
- Health check: `https://your-app.railway.app/health`
- API docs: `https://your-app.railway.app/docs`
- Root endpoint: `https://your-app.railway.app/`

### AI-Powered Features
- AI Challenges: `POST /challenges/generate`
- AI Community Matching: `GET /communities/recommended/{user_id}`
- AI Encouragement: `POST /encouragement/{user_id}`

### Analytics & Insights  
- Cohort Analysis: `GET /analytics/cohorts`
- Event Metrics: `GET /analytics/events`
- A/B Test Results: `GET /experiments/{experiment_id}/results`

## A/B Testing Experiments

The platform comes with 3 pre-configured experiments:

1. **AI vs Template Challenges** (`ai_challenges_v1`)
   - Tests AI-generated vs template-based challenges
   - Target metric: challenge_completion_rate

2. **AI vs Basic Community Matching** (`community_matching_v1`)
   - Tests AI-powered vs simple goal-based matching
   - Target metric: community_connection_rate

3. **Encouragement Frequency** (`encouragement_frequency_v1`)
   - Tests daily vs 3-day vs weekly encouragement
   - Target metric: user_retention_7_day

## Cost Management

### OpenAI Costs
- **GPT-4o-mini**: ~$0.15 per 1K tokens
- **Typical challenge**: ~200 tokens = $0.03
- **Monthly estimate**: 1000 challenges = $30

### PostHog Costs
- **Free tier**: 1M events/month
- **Typical usage**: <100K events/month for small app
- **Cost**: Free for most use cases

### Railway Costs
- **Free tier**: $5/month credits
- **Typical usage**: $10-20/month for production app

## Monitoring & Analytics

### Application Health
- Use Railway dashboard for infrastructure metrics
- Health check endpoint: `/health`
- Application logs via Railway CLI: `railway logs`

### User Analytics
- PostHog dashboard for user behavior
- Real-time event tracking
- Cohort analysis for retention
- A/B test results for optimization

### AI Performance
- Challenge completion rates
- User engagement with AI vs template content
- Community matching success rates

## Frontend Integration

Update the Flutter API service URL in `frontend/lib/services/api_service.dart`:

```dart
final String baseUrl = kDebugMode == 'true' 
    ? 'http://127.0.0.1:8000'  // Local development
    : 'https://your-railway-backend-url.railway.app';  // Your actual Railway URL
```

The Flutter app includes test buttons for:
- AI challenge generation
- AI community matching  
- Personalized encouragement
- Analytics dashboard
- A/B testing results

## Troubleshooting

### Common Issues

1. **AI features not working**
   - Check `OPENAI_API_KEY` is set correctly
   - Verify API key has sufficient credits
   - Check logs for OpenAI API errors

2. **Analytics not tracking**
   - Verify `POSTHOG_API_KEY` is set
   - Check PostHog project settings
   - Ensure events are being sent (check logs)

3. **Database connection errors**
   - Ensure PostgreSQL service is added
   - Check environment variables are set correctly

4. **A/B testing not working**
   - Check experiment configuration
   - Verify user assignment is happening
   - Check conversion tracking

### Debug Commands

```bash
# Check environment variables
railway variables

# View recent logs
railway logs --lines 100

# Connect to database
railway connect postgresql

# Check AI service status
curl https://your-app.railway.app/ | jq '.ai_status'
```

## Security Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Secure OpenAI API key (never commit to code)
- [ ] Configure proper CORS origins
- [ ] Use environment variables for all sensitive data
- [ ] Monitor API usage and costs
- [ ] Enable Railway's built-in security features
- [ ] Regular security updates for dependencies

## Performance Optimization

### AI Features
- Use consistent hashing for A/B testing
- Cache common challenge templates
- Limit AI requests per user per day
- Monitor OpenAI API rate limits

### Analytics
- Batch events when possible
- Use async tracking to avoid blocking requests
- Set up alerts for unusual usage patterns

### Database
- Monitor query performance
- Set up connection pooling
- Regular database maintenance

## Support Resources

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PostHog Documentation](https://posthog.com/docs)
- [Railway Discord](https://discord.gg/railway)

## Success Metrics

Track these key metrics to measure platform success:

1. **Goal Completion Rate**: % of users who complete their fitness goals
2. **Community Engagement**: Connection rates and interaction frequency  
3. **AI Feature Adoption**: Usage of AI vs template features
4. **User Retention**: 7-day, 30-day retention rates
5. **Challenge Completion**: Success rate of daily challenges

Monitor these through the analytics dashboard and use A/B testing to continuously optimize the user experience. 