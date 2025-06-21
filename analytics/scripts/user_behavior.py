import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import plotly.express as px


class UserAnalytics:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def get_goal_completion_rates(self, days: int = 30) -> pd.DataFrame:
        """Calculate goal completion rates by category and user segment"""
        query = f"""
        SELECT 
            u.fitness_level,
            g.category,
            COUNT(*) as total_goals,
            SUM(CASE WHEN g.is_completed THEN 1 ELSE 0 END) as completed_goals,
            AVG(CASE WHEN g.is_completed THEN 1.0 ELSE 0.0 END) as completion_rate
        FROM goals g
        JOIN users u ON g.user_id = u.id
        WHERE g.created_at >= NOW() - INTERVAL '{days} days'
        GROUP BY u.fitness_level, g.category
        """

        return pd.read_sql(query, self.engine)

    def get_community_engagement_metrics(self) -> pd.DataFrame:
        """Analyze community engagement patterns"""
        query = """
        SELECT 
            c.id as community_id,
            c.name,
            COUNT(DISTINCT cm.user_id) as active_members,
            COUNT(cm.id) as total_messages,
            AVG(ci.completed_today::int) as avg_completion_rate
        FROM communities c
        LEFT JOIN community_messages cm ON c.id = cm.community_id
        LEFT JOIN check_ins ci ON c.id = ci.community_id
        WHERE cm.created_at >= NOW() - INTERVAL '7 days'
        GROUP BY c.id, c.name
        """

        return pd.read_sql(query, self.engine)

    def generate_cohort_analysis(self) -> pd.DataFrame:
        """Weekly cohort retention analysis"""
        query = """
        WITH user_weeks AS (
            SELECT 
                user_id,
                DATE_TRUNC('week', created_at) as signup_week,
                DATE_TRUNC('week', created_at) as activity_week
            FROM users
            UNION
            SELECT 
                user_id,
                DATE_TRUNC('week', u.created_at) as signup_week,
                DATE_TRUNC('week', ci.created_at) as activity_week
            FROM check_ins ci
            JOIN users u ON ci.user_id = u.id
        )
        SELECT 
            signup_week,
            activity_week,
            COUNT(DISTINCT user_id) as active_users
        FROM user_weeks
        GROUP BY signup_week, activity_week
        ORDER BY signup_week, activity_week
        """

        df = pd.read_sql(query, self.engine)

        # Calculate retention percentages
        cohort_table = df.pivot(
            index="signup_week", columns="activity_week", values="active_users"
        )

        cohort_sizes = cohort_table.iloc[:, 0]
        retention_table = cohort_table.divide(cohort_sizes, axis=0)

        return retention_table


# Background task for daily analytics
@celery.task
def generate_daily_metrics():
    analytics = UserAnalytics(DATABASE_URL)

    # Calculate key metrics
    completion_rates = analytics.get_goal_completion_rates()
    engagement_metrics = analytics.get_community_engagement_metrics()

    # Store in Redis for dashboard
    redis_client.set(
        "daily_completion_rate", completion_rates["completion_rate"].mean()
    )
    redis_client.set("community_engagement", engagement_metrics.to_json())

    return "Metrics updated successfully"
