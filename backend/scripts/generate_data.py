"""
Phase 0 — Synthetic Data Generation
Generates 6 CSVs and 5 PDFs with deterministic seed(42).
Uses the exact movie titles required for the 6 demo questions.
"""

import csv
import random
import os
from datetime import date, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).parent.parent / "data"
CSV_DIR = BASE_DIR / "csv"
PDF_DIR = BASE_DIR / "pdfs"

TITLES = [
    "Stellar Run", "Dark Orbit", "Last Kingdom", "Echo Chamber",
    "Crimson Tide 2", "Void Protocol", "Laughter Factory",
    "Stand-Up Universe", "Comedy Central", "Romance in Rain",
]

GENRES = {
    "Stellar Run": "Sci-Fi", "Dark Orbit": "Sci-Fi",
    "Last Kingdom": "Action", "Echo Chamber": "Thriller",
    "Crimson Tide 2": "Action", "Void Protocol": "Thriller",
    "Laughter Factory": "Comedy", "Stand-Up Universe": "Comedy",
    "Comedy Central": "Comedy", "Romance in Rain": "Romance",
}

DIRECTORS = [
    "James Nolan", "Sarah Chen", "Marcus Webb", "Aisha Patel",
    "Viktor Reis", "Lena Kim", "Robert Zhao", "Diana Cruz",
    "Thomas Berg", "Priya Sharma",
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "San Francisco", "Seattle", "Denver", "Miami", "Boston",
]

DEVICES = ["Mobile", "Desktop", "Smart TV", "Tablet"]
TIERS = ["Free", "Basic", "Premium", "Enterprise"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
CHANNELS = ["Social Media", "Search Ads", "Email", "Display", "Influencer", "TV"]
SENTIMENTS = ["positive", "neutral", "negative"]
MONTHS = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12",
           "2025-01", "2025-02", "2025-03", "2025-04"]


def write_csv(filename, headers, rows):
    path = CSV_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [CSV] {filename}: {len(rows)} rows")


def generate_movies():
    rows = []
    for i, title in enumerate(TITLES, 1):
        rows.append({
            "movie_id": i,
            "title": title,
            "genre": GENRES[title],
            "release_year": random.choice([2023, 2024, 2025]),
            "director": DIRECTORS[i - 1],
            "runtime_min": random.randint(88, 165),
            "rating": round(random.uniform(5.5, 9.5), 1),
            "budget_usd": round(random.uniform(5_000_000, 80_000_000), 2),
            "revenue_usd": round(random.uniform(8_000_000, 250_000_000), 2),
        })
    write_csv("movies.csv", list(rows[0].keys()), rows)
    return rows


def generate_viewers(n=5000):
    rows = []
    for i in range(1, n + 1):
        joined = date(2022, 1, 1) + timedelta(days=random.randint(0, 1000))
        rows.append({
            "viewer_id": i,
            "name": fake.name(),
            "age_group": random.choice(AGE_GROUPS),
            "city": random.choice(CITIES),
            "subscription_tier": random.choice(TIERS),
            "joined_date": joined.isoformat(),
        })
    write_csv("viewers.csv", list(rows[0].keys()), rows)
    return rows


def generate_watch_activity(viewers, movies, n=5000):
    rows = []
    for i in range(1, n + 1):
        movie = random.choice(movies)
        runtime = movie["runtime_min"]
        dur = random.randint(5, runtime)
        rows.append({
            "activity_id": i,
            "viewer_id": random.choice(viewers)["viewer_id"],
            "movie_id": movie["movie_id"],
            "watch_date": (date(2024, 6, 1) + timedelta(days=random.randint(0, 300))).isoformat(),
            "watch_duration_min": dur,
            "completion_pct": round(min(dur / runtime * 100, 100), 1),
            "device": random.choice(DEVICES),
        })
    write_csv("watch_activity.csv", list(rows[0].keys()), rows)
    return rows


def generate_reviews(viewers, movies, n=5000):
    positive_phrases = [
        "Absolutely loved this film! The storytelling was phenomenal.",
        "Great performances and stunning visuals throughout.",
        "A must-watch for fans of the genre. Highly recommended.",
        "Exceeded my expectations in every way possible.",
        "Brilliant direction and an engaging plot from start to finish.",
    ]
    neutral_phrases = [
        "It was okay, nothing too special but watchable.",
        "Average movie with some interesting moments here and there.",
        "Not bad, but could have been better with tighter editing.",
        "Decent entertainment for a weekend, nothing groundbreaking.",
        "Some good parts, some slow parts. Mixed feelings overall.",
    ]
    negative_phrases = [
        "Disappointed with the plot. Very predictable and boring.",
        "The pacing was terrible and the acting felt forced throughout.",
        "Would not recommend. Wasted potential on a promising premise.",
        "Below average. The script needed a lot more work.",
        "Not worth the hype. Overly long and lacking substance.",
    ]
    rows = []
    for i in range(1, n + 1):
        sentiment = random.choices(SENTIMENTS, weights=[50, 30, 20])[0]
        if sentiment == "positive":
            text = random.choice(positive_phrases)
            rating = round(random.uniform(7.0, 10.0), 1)
        elif sentiment == "neutral":
            text = random.choice(neutral_phrases)
            rating = round(random.uniform(5.0, 7.0), 1)
        else:
            text = random.choice(negative_phrases)
            rating = round(random.uniform(1.0, 5.0), 1)
        rows.append({
            "review_id": i,
            "viewer_id": random.choice(viewers)["viewer_id"],
            "movie_id": random.choice(movies)["movie_id"],
            "rating": rating,
            "sentiment": sentiment,
            "review_date": (date(2024, 6, 1) + timedelta(days=random.randint(0, 300))).isoformat(),
            "review_text": text,
        })
    write_csv("reviews.csv", list(rows[0].keys()), rows)
    return rows


def generate_marketing_spend(movies, n=5000):
    rows = []
    for i in range(1, n + 1):
        spend = round(random.uniform(1000, 100000), 2)
        impressions = random.randint(10000, 5000000)
        clicks = int(impressions * random.uniform(0.005, 0.05))
        conversions = int(clicks * random.uniform(0.02, 0.15))
        rows.append({
            "campaign_id": i,
            "movie_id": random.choice(movies)["movie_id"],
            "channel": random.choice(CHANNELS),
            "spend_usd": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "campaign_month": random.choice(MONTHS),
        })
    write_csv("marketing_spend.csv", list(rows[0].keys()), rows)
    return rows


def generate_regional_performance(movies, n=5000):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "region_id": i,
            "city": random.choice(CITIES),
            "movie_id": random.choice(movies)["movie_id"],
            "views": random.randint(100, 500000),
            "engagement_score": round(random.uniform(1.0, 10.0), 2),
            "revenue_usd": round(random.uniform(500, 2000000), 2),
            "month": random.choice(MONTHS),
        })
    write_csv("regional_performance.csv", list(rows[0].keys()), rows)
    return rows


# ─── PDF Generation ───

PDF_CONTENT = {
    "quarterly_executive_report_q1_2025.pdf": """Quarterly Executive Report — Q1 2025

StreamCo Confidential | Prepared by the Analytics Division

Executive Summary:
Q1 2025 has been a landmark quarter for StreamCo. Total platform revenue reached $487 million, representing a 23% year-over-year increase. Our subscriber base grew to 14.2 million active users, driven primarily by the successful launches of Stellar Run and Dark Orbit in the Sci-Fi category.

Revenue Breakdown by Genre:
The Sci-Fi genre dominated Q1 revenue, contributing $156 million (32% of total). Action titles followed closely at $112 million (23%), while Comedy generated $78 million (16%). Romance and Thriller genres contributed $72 million and $69 million respectively. This marks the first quarter where Sci-Fi surpassed Action as the top revenue genre, a shift driven by the massive success of Stellar Run.

Top Performing Titles:
Stellar Run emerged as the breakout hit of the quarter, generating $89 million in revenue against a $45 million budget — a 97% return on investment. Dark Orbit performed strongly at $67 million revenue. Last Kingdom continued its steady performance with $52 million. Echo Chamber surprised analysts with $41 million despite a modest marketing budget.

Viewer Engagement Metrics:
Average watch time per session increased to 47 minutes, up from 42 minutes in Q4 2024. Completion rates improved across all genres, with Sci-Fi leading at 78% average completion. The Premium tier showed the highest engagement with 62 minutes average session length. Mobile viewing continued to grow, now representing 43% of all watch sessions.

Geographic Performance:
New York and Los Angeles remain our strongest markets, contributing 34% of total revenue. However, emerging markets like Denver and Phoenix showed 45% growth quarter-over-quarter. Seattle demonstrated particularly strong engagement scores, averaging 8.2 out of 10 across all titles.

Strategic Outlook:
Based on Q1 performance, we are increasing our Sci-Fi content investment by 30% for the remainder of 2025. The comedy genre requires strategic reassessment — while audience size remains large, per-viewer revenue trails other genres by 22%. We recommend targeted comedy content that appeals to Premium subscribers specifically.

Key Risks:
Market saturation in major metropolitan areas may slow growth. Increasing content production costs (up 15% YoY) require careful budget management. Competition from rival platforms intensified in Q1 with three new entrants in the streaming space.""",

    "campaign_performance_summary.pdf": """Campaign Performance Summary — StreamCo Marketing Division

Prepared for: Senior Leadership Team
Report Period: July 2024 — March 2025

Overview:
This report summarizes marketing campaign performance across all channels for the past three quarters. Total marketing spend reached $12.4 million across 847 campaigns promoting our content library. Overall return on ad spend (ROAS) was 4.7x, exceeding our target of 4.0x.

Channel Performance Analysis:
Social Media campaigns delivered the highest ROAS at 6.2x, driven by viral moments from Stellar Run trailers on TikTok and Instagram Reels. Total social spend was $3.1 million generating $19.2 million in attributed revenue. Search Ads maintained consistent performance with 5.1x ROAS on $2.8 million spend. Email marketing proved most cost-efficient at 8.3x ROAS, though with limited scale at $1.2 million spend. Display advertising underperformed at 2.1x ROAS, and we recommend reducing display allocation by 25%. Influencer partnerships showed promising results at 4.8x ROAS for Sci-Fi titles specifically. TV advertising, while expensive at $2.4 million, drove significant brand awareness measured through search volume lifts of 340%.

CPM Trends:
Cost per thousand impressions (CPM) increased 12% year-over-year across digital channels. Social media CPM rose from $6.20 to $7.40, reflecting increased competition. Search CPM remained relatively stable at $3.80. Email CPM decreased slightly to $1.10 due to improved list hygiene and segmentation.

Best-Performing Creatives:
Short-form video content (15-30 seconds) outperformed static images by 3.2x in click-through rate. Behind-the-scenes content generated 45% higher engagement than traditional trailers. User-generated content campaigns achieved 2.8x higher conversion rates than branded content. Personalized recommendations in email campaigns improved click rates by 67%.

Title-Specific Campaign Results:
Stellar Run received the largest marketing investment at $2.1 million, generating an exceptional 7.1x ROAS. Dark Orbit campaigns focused on sci-fi enthusiast audiences achieved 5.8x ROAS. Comedy titles (Laughter Factory, Stand-Up Universe, Comedy Central) collectively received $1.8 million in marketing spend but delivered only 3.2x ROAS. Romance in Rain performed well with targeted campaigns on female-skewing platforms.

Recommendations:
Increase social media allocation by 20% for Q2 2025. Reduce display advertising budget and reallocate to influencer partnerships. Implement A/B testing framework for all email campaigns. Develop genre-specific creative strategies rather than one-size-fits-all approaches. Comedy marketing requires fundamental repositioning — current messaging does not resonate with target demographics.""",

    "content_roadmap_2025.pdf": """Content Roadmap 2025 — StreamCo Studios

Classification: Internal Use Only
Version: 3.2 | Last Updated: March 2025

Strategic Vision:
StreamCo's 2025 content strategy focuses on three pillars: expanding our Sci-Fi franchise universe, revitalizing our Comedy slate, and establishing a premium Thriller brand. Total production budget for 2025 is $340 million across 28 planned titles, representing a 25% increase from 2024.

Upcoming Titles — Q2 2025:
Stellar Run 2: Sequel to our biggest hit, with a $65 million budget. Pre-production is complete, principal photography begins April 2025. Target release: October 2025. Early audience testing shows 92% interest among viewers who watched the original.
Nebula's Edge: Original sci-fi thriller hybrid, budget $42 million. Currently in post-production with a July 2025 release target. Features breakthrough visual effects technology.
City of Shadows: Action-thriller crossover, $38 million budget. Release planned for August 2025.

Genre Strategy:
Sci-Fi: Our strongest performing genre. We are building a shared universe connecting Stellar Run, Dark Orbit, and Void Protocol. This franchise approach mirrors successful strategies in theatrical releases. Budget allocation: $95 million (28% of total).
Action: Maintain current output of 4-5 titles per year. Focus on mid-budget ($25-35M) titles with proven directors. Budget allocation: $75 million (22%).
Thriller: Underserved genre with high per-viewer revenue. Increasing slate from 3 to 5 titles. Budget allocation: $60 million (18%).
Comedy: Requires strategic overhaul. Current comedy titles show lower completion rates and revenue per viewer compared to other genres. New approach: invest in fewer, higher-quality comedy specials rather than full-length features. Partnering with established comedy talent for exclusive content. Budget allocation: $55 million (16%).
Romance: Steady performer with loyal audience base. Exploring limited series format for romance content. Budget allocation: $40 million (12%).

Production Pipeline:
Currently in active production: 8 titles. In post-production: 4 titles. In development (script/pre-production): 12 titles. Greenlit, awaiting scheduling: 4 titles.

Technology Investments:
Virtual production stages: $12 million investment in LED volume stages. AI-assisted post-production: $5 million pilot program for VFX acceleration. Cloud rendering: Partnership with major cloud provider for distributed rendering.

Distribution Strategy:
Day-and-date release on StreamCo platform for all original titles. Select theatrical windows (2-4 weeks) for tentpole releases. International licensing agreements for 15 additional territories in 2025.""",

    "platform_policy_guidelines.pdf": """StreamCo Platform Policy Guidelines

Document Owner: Legal & Compliance Division
Effective Date: January 1, 2025
Review Cycle: Quarterly

Content Moderation Policies:
All content uploaded to the StreamCo platform must comply with our content standards. Automated screening uses a three-tier system: AI pre-screening flags potentially problematic content, human moderators review flagged items within 24 hours, and a senior review board handles escalated cases. Content ratings (G, PG, PG-13, R) must be accurately assigned before publication.

Data Handling and Privacy:
StreamCo is committed to protecting user privacy in compliance with GDPR, CCPA, and applicable regulations. Personal Identifiable Information (PII) including names, email addresses, viewing history, and payment information must be encrypted at rest using AES-256 and in transit using TLS 1.3. PII must never be included in analytics reports, marketing materials, or shared with third parties without explicit user consent. All internal analytics systems must implement PII scrubbing before data processing. Viewer data retention policy: active account data retained indefinitely, deleted account data purged within 30 days, viewing analytics anonymized after 24 months.

Compliance Requirements:
All employees handling user data must complete annual privacy training. Data access is restricted on a need-to-know basis with role-based access controls. All API endpoints handling user data must implement authentication and authorization. Regular security audits conducted quarterly by external auditors. Incident response plan must be activated within 1 hour of any data breach detection.

Content Licensing and Rights Management:
All content must have verified licensing agreements before platform publication. Digital rights management (DRM) applied to all premium content. Geographic content restrictions enforced based on licensing territories. Content removal requests processed within 48 hours. Creator revenue sharing follows standard 70/30 split for original content.

Advertising and Monetization:
Advertisements must comply with FTC guidelines for disclosure. No targeted advertising to users under 18. Ad frequency capped at 2 minutes per 30 minutes of content for Basic tier. Premium and Enterprise tiers are ad-free. Sponsored content must be clearly labeled. Data used for ad targeting must be anonymized and aggregated.

Accessibility Standards:
All original content must include closed captions within 48 hours of release. Audio descriptions required for all tentpole releases. Platform UI must meet WCAG 2.1 AA standards. Subtitle support for minimum 12 languages on all original content.

Security Protocols:
Multi-factor authentication available for all user accounts and mandatory for employees. API rate limiting enforced on all public endpoints: 100 requests per minute for authenticated users, 20 for unauthenticated. All database queries must use parameterized statements — raw SQL construction is prohibited. Secrets and API keys must never be committed to version control. Regular penetration testing conducted quarterly.""",

    "audience_behavior_report.pdf": """Audience Behavior Analysis Report

Prepared by: StreamCo Data Science Team
Analysis Period: Q3 2024 — Q1 2025
Sample Size: 14.2 million active subscribers

Watch Pattern Analysis:
Peak viewing hours remain consistent at 7 PM — 11 PM local time across all markets, with 67% of daily watch time concentrated in this window. Weekend viewing is 34% higher than weekday averages. Tuesday has emerged as the weakest viewing day, while Friday shows the strongest engagement. Average daily viewing time per user is 1.8 hours, up from 1.6 hours in the previous analysis period.

Binge Behavior:
Binge viewing (defined as watching 3+ episodes or 2+ movies in a single session) occurs in 28% of all sessions. Binge sessions are most common among the 25-34 age group (36% binge rate) and least common among 55+ viewers (14% binge rate). Sci-Fi and Thriller genres have the highest binge rates at 35% and 31% respectively. Comedy content shows a notably lower binge rate of 18%, suggesting episodic rather than serialized consumption patterns. Premium subscribers binge 42% more frequently than Basic tier users.

Device Preferences:
Smart TV has overtaken Mobile as the primary viewing device, representing 38% of total watch time (up from 31%). Mobile remains strong at 32%, particularly for short-form content and commute viewing. Desktop viewing continues to decline, now at 15%. Tablet viewing holds steady at 15%. Multi-device viewing (starting on one device, continuing on another) increased 56% and now accounts for 12% of all sessions. The average viewer uses 2.3 different devices per month.

Genre Consumption by Demographics:
18-24 age group: Sci-Fi (32%), Action (28%), Comedy (22%), other (18%). 25-34 age group: Thriller (29%), Sci-Fi (26%), Action (21%), Romance (14%), Comedy (10%). 35-44 age group: Action (27%), Thriller (24%), Drama (20%), Comedy (15%), other (14%). 45-54 age group: Thriller (30%), Action (22%), Romance (20%), Comedy (18%), other (10%). 55+ age group: Romance (28%), Thriller (24%), Comedy (22%), Action (16%), other (10%).

Subscription Tier Behavior:
Free tier users average 45 minutes daily viewing with 52% completion rates. Basic tier users watch 1.4 hours daily with 64% completion rates. Premium tier users are most engaged at 2.3 hours daily with 78% completion rates. Enterprise tier users show similar patterns to Premium but with higher multi-device usage.

Content Discovery:
Algorithmic recommendations drive 45% of content starts. Browse and search account for 30%. Social media referrals account for 15%. Email recommendations account for 10%. Users who engage with recommendations watch 40% more content monthly.

Churn Indicators:
Declining weekly watch time (below 30 minutes) predicts churn with 73% accuracy. Users who do not watch any content for 14 consecutive days have a 62% probability of churning within 60 days. Low completion rates (below 40%) across multiple titles indicate content dissatisfaction. Price sensitivity is highest among Basic tier users in the 18-24 age group.

Retention Drivers:
Exclusive original content is the primary retention driver, cited by 58% of retained subscribers. Multi-profile support increases household retention by 34%. Personalized recommendations improve retention by 23%. Early access to new releases motivates 41% of Premium upgrades.""",
}


def generate_pdfs():
    """Generate 5 PDF documents with 600-900 words of realistic narrative text."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    for filename, content in PDF_CONTENT.items():
        path = PDF_DIR / filename
        doc = SimpleDocTemplate(str(path), pagesize=letter,
                                topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"],
                                     fontSize=16, alignment=TA_CENTER, spaceAfter=20)
        body_style = ParagraphStyle("CustomBody", parent=styles["Normal"],
                                    fontSize=11, leading=15, alignment=TA_LEFT, spaceAfter=8)
        heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"],
                                       fontSize=13, spaceAfter=10, spaceBefore=14)
        story = []
        lines = content.strip().split("\n")
        title = lines[0].strip()
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))

        for line in lines[1:]:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
            elif line.endswith(":") and len(line.split()) <= 8:
                story.append(Paragraph(line, heading_style))
            else:
                # Escape XML special characters
                line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(line, body_style))

        doc.build(story)
        print(f"  [PDF] {filename}")


def main():
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)

    print("Generating synthetic data (seed=42)...")
    movies = generate_movies()
    viewers = generate_viewers(5000)
    generate_watch_activity(viewers, movies, 5000)
    generate_reviews(viewers, movies, 5000)
    generate_marketing_spend(movies, 5000)
    generate_regional_performance(movies, 5000)

    print("\nGenerating PDF documents...")
    generate_pdfs()

    print("\n✓ All data generated successfully.")


if __name__ == "__main__":
    main()
