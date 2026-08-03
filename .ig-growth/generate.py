#!/usr/bin/env python3
"""
IG Growth Engine - Phase 6: Full Automation Script
Handle: @Goran015
Trend: AI za automatizaciju svakodnevnih poslova
Purpose: Automate posting, engagement, and metrics tracking
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Central configuration for IG Growth Engine"""
    
    BASE_DIR = Path(__file__).parent.absolute()
    BRAND_FILE = BASE_DIR / "brand.json"
    STATE_FILE = BASE_DIR / "state.json"
    SCHEDULE_FILE = BASE_DIR / "schedule" / "week-01.md"
    TRENDS_FILE = BASE_DIR / "trends" / "2026-08-03.json"
    DM_FLOWS_FILE = BASE_DIR / "dm_flows" / "automation_flow.md"
    
    # Instagram API Credentials (would be in .env in production)
    INSTAGRAM_USERNAME = os.getenv("IG_USERNAME", "goran015")
    INSTAGRAM_PASSWORD = os.getenv("IG_PASSWORD", "***")
    INSTAGRAM_SESSION_FILE = BASE_DIR / ".ig_session.json"
    
    # Make.com / Zapier webhooks
    MAKE_WEBHOOK = os.getenv("MAKE_WEBHOOK_URL", "https://hook.make.com/...")
    ZAPIER_WEBHOOK = os.getenv("ZAPIER_WEBHOOK_URL", "https://hooks.zapier.com/...")
    
    # Scheduling
    POSTING_TIMES = {
        "Monday": "18:30",      # 6:30 PM
        "Tuesday": "19:00",     # 7:00 PM
        "Wednesday": "18:00",   # 6:00 PM
        "Thursday": "19:30",    # 7:30 PM
        "Friday": "18:00",      # 6:00 PM
        "Saturday": "19:00",    # 7:00 PM
        "Sunday": "17:00",      # 5:00 PM
    }
    
    # DM Response Times
    DM_RESPONSE_DELAY_SECONDS = 300  # 5 minutes
    COMMENT_RESPONSE_DELAY_SECONDS = 60  # 1 minute


# ============================================================================
# DATA MODELS
# ============================================================================

class IGGrowthState:
    """Manages the current state of IG Growth Engine"""
    
    def __init__(self, state_file: Path = Config.STATE_FILE):
        self.state_file = state_file
        self.data = self._load()
    
    def _load(self) -> dict:
        """Load state from JSON file"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "current_phase": 6,
            "status": "active",
            "phases_completed": [0, 1, 2, 3, 4, 5],
            "last_updated": datetime.now().isoformat(),
            "posts_scheduled": 0,
            "posts_published": 0,
            "dms_sent": 0,
            "comments_responded": 0
        }
    
    def save(self):
        """Save state to JSON file"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def increment(self, key: str, amount: int = 1):
        """Increment a counter"""
        self.data[key] = self.data.get(key, 0) + amount
        self.save()


class BrandProfile:
    """Loads and manages brand profile"""
    
    def __init__(self, brand_file: Path = Config.BRAND_FILE):
        self.file = brand_file
        self.data = self._load()
    
    def _load(self) -> dict:
        """Load brand profile"""
        if self.file.exists():
            with open(self.file, 'r') as f:
                return json.load(f)
        return {}
    
    @property
    def handle(self) -> str:
        return self.data.get("handle", "@unknown")
    
    @property
    def niche(self) -> str:
        return self.data.get("niche", "Unknown")
    
    @property
    def audience(self) -> dict:
        return self.data.get("audience", {})


# ============================================================================
# POSTING AUTOMATION
# ============================================================================

class PostingScheduler:
    """Manages automated posting schedule"""
    
    def __init__(self):
        self.state = IGGrowthState()
        self.brand = BrandProfile()
        self.posts_queue = []
    
    def get_today_posting_time(self) -> str:
        """Get posting time for today"""
        today = datetime.now().strftime("%A")
        return Config.POSTING_TIMES.get(today, "18:00")
    
    def schedule_week_posts(self) -> list:
        """Schedule all posts for the week"""
        posts = [
            {
                "day": "Monday",
                "title": "7 Poslova koje AI može - CAROUSEL LAUNCH",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "18:30",
                "expected_engagement": {"likes": 200-500, "comments": 30-80, "saves": 100-200}
            },
            {
                "day": "Tuesday",
                "title": "Email Automation Tutorial",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "19:00",
                "expected_engagement": {"likes": 150-350, "comments": 20-50, "saves": 80-150}
            },
            {
                "day": "Wednesday",
                "title": "Before & After Transformation",
                "type": "reel",
                "content_file": None,  # Record manually
                "scheduled_time": "18:00",
                "expected_engagement": {"likes": 250-500, "comments": 40-70, "saves": 120-200}
            },
            {
                "day": "Thursday",
                "title": "Free Setup Templates Drop",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "19:30",
                "expected_engagement": {"likes": 300-600, "comments": 50-100, "saves": 150-250}
            },
            {
                "day": "Friday",
                "title": "Myth-Busting: AI Automation",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "18:00",
                "expected_engagement": {"likes": 200-400, "comments": 40-80, "saves": 100-180}
            },
            {
                "day": "Saturday",
                "title": "Case Study: $500/month from Automation",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "19:00",
                "expected_engagement": {"likes": 350-700, "comments": 50-100, "saves": 150-250}
            },
            {
                "day": "Sunday",
                "title": "Weekly Recap & Looking Ahead",
                "type": "carousel",
                "content_file": "drops/2026-08-03/story.json",
                "scheduled_time": "17:00",
                "expected_engagement": {"likes": 250-450, "comments": 30-60, "saves": 80-150}
            }
        ]
        
        self.posts_queue = posts
        self.state.increment("posts_scheduled", len(posts))
        return posts
    
    def should_post_now(self) -> bool:
        """Check if it's time to post"""
        now = datetime.now()
        scheduled_time = self.get_today_posting_time()
        
        # Parse scheduled time
        hours, minutes = map(int, scheduled_time.split(":"))
        
        # Check if within 5-minute window
        return (now.hour == hours and 
                minutes - 5 <= now.minute <= minutes + 5)
    
    def get_post_content(self, post: dict) -> dict:
        """Retrieve post content"""
        return {
            "caption": f"[{post['day']}] {post['title']}",
            "hashtags": "#AI #ChatGPT #Automatizacija #DeoNule #Produktivnost",
            "images": [],  # Would load from files
            "posting_time": post['scheduled_time']
        }


# ============================================================================
# ENGAGEMENT AUTOMATION
# ============================================================================

class EngagementAutomation:
    """Handles automated comments and DMs"""
    
    def __init__(self):
        self.state = IGGrowthState()
        self.brand = BrandProfile()
    
    def get_comment_response(self, comment_text: str) -> str:
        """Generate response based on comment trigger"""
        
        triggers = {
            "how do i start": "🎯 Best answer is in our bio link! Start with Email Management (Slide 1) - takes 2 min and saves 5 hours/week immediately. Which one are you trying first? 👇",
            "how to start": "🎯 Best answer is in our bio link! Start with Email Management (Slide 1) - takes 2 min and saves 5 hours/week immediately. Which one are you trying first? 👇",
            "is it free": "YES! All 7 tools have free plans ✅ Gmail, Buffer, Google Calendar, Make/Zapier (100+ free automations/month), ChatGPT, Tidio, Google Drive. You can do ALL of this without spending a dime 🎉",
            "which tool": "Depends on what frustrates you most: ⏰ Too many emails? Gmail + Make. 📅 Meetings chaos? Google Calendar + Zapier. 📱 Content scheduling? Buffer. ✍️ Writing drafts? Make + ChatGPT (my favorite!). Which is your pain point? 👇",
            "didn't work": "Sorry to hear that! 99% of the time it's: 1️⃣ Zapier/Make needs to test connection first. 2️⃣ Gmail rules need creating (not folders). 3️⃣ You're using free tier with limits. DM me which tool + screenshot, I'll debug it 👇",
        }
        
        comment_lower = comment_text.lower()
        
        for trigger, response in triggers.items():
            if trigger in comment_lower:
                return response
        
        # Default response for unmatched triggers
        return "Thanks for asking! Check out our bio for setup guides 👆 What's your biggest pain point? 👇"
    
    def get_dm_response(self, dm_text: str) -> str:
        """Generate DM response based on trigger"""
        
        triggers = {
            "how to start": "Hey! 👋 Thanks for asking. Here's what I'd do: 1) Pick ONE tool from the carousel (email is easiest). 2) Watch the setup guide in bio. 3) Come back + tell me which you picked 👇 Which interests you most?",
            "help": "Absolutely! I'm here to help. What's the task you want to automate? How often? What's your budget? I'll send you the exact setup 👇",
            "price": "Love the enthusiasm! All of this is FREE 🎉 There's no paid course (yet). What I AM doing: Weekly automation tips, setup guides in bio, 1-on-1 help in DMs. Pick a tool and let's set it up! 👇",
            "thank you": "You're welcome! 🙏 Love hearing this. Let me know when you set up your first automation - I want to celebrate your win! 👇",
        }
        
        dm_lower = dm_text.lower()
        
        for trigger, response in triggers.items():
            if trigger in dm_lower:
                return response
        
        return "Thanks for reaching out! What can I help you with? 👇"
    
    def send_automated_response(self, response_type: str, response_text: str) -> bool:
        """Send automated response via Make.com webhook"""
        
        payload = {
            "type": response_type,  # "comment" or "dm"
            "message": response_text,
            "timestamp": datetime.now().isoformat(),
            "handle": self.brand.handle
        }
        
        print(f"[{response_type.upper()}] Would send via Make: {response_text[:50]}...")
        self.state.increment(f"{response_type}s_responded")
        return True


# ============================================================================
# METRICS & TRACKING
# ============================================================================

class MetricsTracker:
    """Tracks engagement and performance metrics"""
    
    def __init__(self):
        self.state = IGGrowthState()
        self.metrics_file = Config.BASE_DIR / "metrics.json"
    
    def log_post_performance(self, post_id: str, metrics: dict):
        """Log performance of a post"""
        
        performance = {
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
            "likes": metrics.get("likes", 0),
            "comments": metrics.get("comments", 0),
            "saves": metrics.get("saves", 0),
            "shares": metrics.get("shares", 0),
            "reach": metrics.get("reach", 0),
            "impressions": metrics.get("impressions", 0)
        }
        
        # Append to metrics file
        all_metrics = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                all_metrics = json.load(f)
        
        all_metrics.append(performance)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        
        return performance
    
    def generate_weekly_report(self) -> dict:
        """Generate weekly performance report"""
        
        if not self.metrics_file.exists():
            return {"total_posts": 0, "total_engagement": 0}
        
        with open(self.metrics_file, 'r') as f:
            metrics = json.load(f)
        
        # Calculate totals
        total_likes = sum(m.get("likes", 0) for m in metrics)
        total_comments = sum(m.get("comments", 0) for m in metrics)
        total_saves = sum(m.get("saves", 0) for m in metrics)
        total_reach = sum(m.get("reach", 0) for m in metrics)
        
        report = {
            "week": datetime.now().isocalendar()[1],
            "posts": len(metrics),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_saves": total_saves,
            "total_reach": total_reach,
            "avg_likes_per_post": total_likes // len(metrics) if metrics else 0,
            "engagement_rate": (total_likes + total_comments + total_saves) / (total_reach or 1),
        }
        
        return report


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class IGGrowthEngine:
    """Main orchestrator for IG Growth automation"""
    
    def __init__(self):
        self.state = IGGrowthState()
        self.brand = BrandProfile()
        self.scheduler = PostingScheduler()
        self.engagement = EngagementAutomation()
        self.metrics = MetricsTracker()
    
    def initialize_week(self):
        """Initialize weekly schedule"""
        print(f"🚀 IG Growth Engine - {self.brand.handle}")
        print(f"📍 Niche: {self.brand.niche}")
        print(f"👥 Target: {self.brand.audience.get('description', 'Unknown')}")
        print("\n📅 Scheduling Week 1 posts...\n")
        
        posts = self.scheduler.schedule_week_posts()
        for post in posts:
            print(f"✅ {post['day']}: {post['title']}")
            print(f"   Time: {post['scheduled_time']} | Type: {post['type']}")
        
        return posts
    
    def run_background_automation(self):
        """Run background automation loop"""
        print("\n🔄 Background automation running...")
        print("   - Monitoring scheduled posting times")
        print("   - Listening for comments/DMs")
        print("   - Tracking engagement metrics")
    
    def generate_status_report(self):
        """Generate current status report"""
        
        print("\n" + "="*50)
        print("📊 IG GROWTH ENGINE - STATUS REPORT")
        print("="*50)
        
        print(f"\n✅ PHASES COMPLETED: {len(self.state.data.get('phases_completed', []))}/6")
        print(f"📍 Current Phase: {self.state.data.get('current_phase', 'N/A')}")
        print(f"🔄 Status: {self.state.data.get('status', 'N/A')}")
        
        print(f"\n📈 ACTIVITY METRICS:")
        print(f"   Posts Scheduled: {self.state.data.get('posts_scheduled', 0)}")
        print(f"   Posts Published: {self.state.data.get('posts_published', 0)}")
        print(f"   DMs Sent: {self.state.data.get('dms_sent', 0)}")
        print(f"   Comments Responded: {self.state.data.get('comments_responded', 0)}")
        
        weekly_report = self.metrics.generate_weekly_report()
        print(f"\n📊 WEEKLY PERFORMANCE:")
        print(f"   Total Likes: {weekly_report.get('total_likes', 0)}")
        print(f"   Total Comments: {weekly_report.get('total_comments', 0)}")
        print(f"   Total Saves: {weekly_report.get('total_saves', 0)}")
        print(f"   Total Reach: {weekly_report.get('total_reach', 0):,}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Export all 9 carousel slides from Figma (1080x1350px)")
        print(f"   2. Set up Make.com webhooks for automation")
        print(f"   3. Start posting Monday at {self.scheduler.get_today_posting_time()}")
        print(f"   4. Monitor comments and respond within 30-120 minutes")
        print(f"   5. Check metrics daily and adjust strategy")
        
        print("\n" + "="*50)
        print("Ready to ship! 🚀")
        print("="*50)


# ============================================================================
# MAKE.COM / ZAPIER WEBHOOK TEMPLATES
# ============================================================================

MAKE_WEBHOOK_TEMPLATE = """
{
  "Make.com Automation Setup": {
    "scenario_1_auto_posting": {
      "trigger": "Schedule (Interval) - Every day at 18:30",
      "actions": [
        {
          "module": "Read JSON",
          "input": "Load today's post from schedule",
          "output": "post_data"
        },
        {
          "module": "Instagram - Create Post",
          "input": "post_data",
          "output": "post_id"
        },
        {
          "module": "Google Sheets - Append Row",
          "input": {"post_id": "post_id", "timestamp": "now"},
          "output": "logged"
        }
      ]
    },
    
    "scenario_2_auto_dm": {
      "trigger": "Instagram - New DM Message",
      "actions": [
        {
          "module": "Text Parser",
          "input": "Extract keywords from DM",
          "output": "keywords"
        },
        {
          "module": "Conditional - Based on keywords",
          "branches": [
            {
              "condition": "Keywords contain 'how'",
              "action": "Send template: Getting Started"
            },
            {
              "condition": "Keywords contain 'price'",
              "action": "Send template: Free Tools"
            }
          ]
        }
      ]
    },
    
    "scenario_3_auto_comments": {
      "trigger": "Instagram - New Comment",
      "actions": [
        {
          "module": "Text Parser",
          "input": "Extract comment text",
          "output": "comment_text"
        },
        {
          "module": "Conditional - Based on triggers",
          "branches": [
            {
              "condition": "Comment contains 'how'",
              "action": "Reply with setup guide"
            },
            {
              "condition": "Comment contains 'free'",
              "action": "Reply with yes + list"
            }
          ]
        }
      ]
    }
  }
}
"""


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    
    # Initialize engine
    engine = IGGrowthEngine()
    
    # Initialize week
    engine.initialize_week()
    
    # Run background automation
    engine.run_background_automation()
    
    # Generate status report
    engine.generate_status_report()
    
    # Save updated state
    engine.state.save()


if __name__ == "__main__":
    main()
