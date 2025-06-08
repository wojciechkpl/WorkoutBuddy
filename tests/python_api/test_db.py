#!/usr/bin/env python3

import sys
import os

# Add the ml_backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml_backend"))

from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!", result.fetchone())
except Exception as e:
    print("❌ Database connection failed:", str(e))
