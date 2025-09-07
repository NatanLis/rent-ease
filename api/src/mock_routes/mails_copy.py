from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel

__all__ = ["mails"]


class Avatar(BaseModel):
    src: str


class MailSender(BaseModel):
    name: str
    email: str
    avatar: Optional[Avatar] = None


class Mail(BaseModel):
    id: int
    from_: MailSender
    subject: str
    body: str
    date: str
    unread: Optional[bool] = False


def sub_date(dt: datetime, **kwargs) -> str:
    return (dt - timedelta(**kwargs)).isoformat()


now = datetime.now()

mails: List[Mail] = [
    Mail(
        id=1,
        from_=MailSender(
            name="Alex Smith", email="alex.smith@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=1")
        ),
        subject="Meeting Schedule: Q1 Marketing Strategy Review",
        body="""Dear Team,

I hope this email finds you well. Just a quick reminder about our Q1 Marketing Strategy meeting scheduled for tomorrow at 10
AM EST in Conference Room A.

Agenda:
- Q4 Performance Review
- New Campaign Proposals
- Budget Allocation for Q2
- Team Resource Planning

Please come prepared with your department updates. I've attached the preliminary deck for your review.

Best regards,
Alex Smith
Senior Marketing Director
Tel: (555) 123-4567""",
        date=now.isoformat(),
    ),
    Mail(
        id=2,
        unread=True,
        from_=MailSender(
            name="Jordan Brown", email="jordan.brown@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=2")
        ),
        subject="RE: Project Phoenix - Sprint 3 Update",
        body="""Hi team,

Quick update on Sprint 3 deliverables:

✅ User authentication module completed
🏗️ Payment integration at 80%
⏳ API documentation pending review

Key metrics:
- Code coverage: 94%
- Sprint velocity: 45 points
- Bug resolution rate: 98%

Please review the attached report for detailed analysis. Let's discuss any blockers in tomorrow's stand-up.

Regards,
Jordan

--
Jordan Brown
Lead Developer | Tech Solutions
Mobile: +1 (555) 234-5678""",
        date=sub_date(now, minutes=7),
    ),
    Mail(
        id=3,
        unread=True,
        from_=MailSender(
            name="Taylor Green", email="taylor.green@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=3")
        ),
        subject="Lunch Plans",
        body="""Hi there!

I was wondering if you'd like to grab lunch this Friday? There's this amazing new Mexican restaurant downtown called "La Casa"
that I've been wanting to try. They're known for their authentic tacos and house-made guacamole.

Would 12:30 PM work for you? It would be great to catch up and discuss the upcoming team building event while we're there.

Let me know what you think!

Best,
Taylor""",
        date=sub_date(now, hours=3),
    ),
    Mail(
        id=4,
        from_=MailSender(
            name="Morgan White", email="morgan.white@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=4")
        ),
        subject="New Proposal: Project Horizon",
        body="""Hi team,

I've just uploaded the comprehensive proposal for Project Horizon to our shared drive. The document includes:

• Detailed project objectives and success metrics
• Resource allocation and team structure
• Timeline with key milestones
• Budget breakdown
• Risk assessment and mitigation strategies

I'm particularly excited about our innovative approach to the user engagement component, which could set a new standard for
our industry.

Could you please review and provide feedback by EOD Friday? I'd like to present this to the steering committee next week.

Thanks in advance,

Morgan White
Senior Project Manager
Tel: (555) 234-5678""",
        date=sub_date(now, days=1),
    ),
    Mail(
        id=5,
        from_=MailSender(name="Casey Gray", email="casey.gray@example.com"),
        subject="Updated: San Francisco Conference Trip Itinerary",
        body="""Dear [Name],

Please find your confirmed travel itinerary below:

FLIGHT DETAILS:
Outbound: AA 1234
Date: March 15, 2024
DEP: JFK 09:30 AM
ARR: SFO 12:45 PM

HOTEL:
Marriott San Francisco
Check-in: March 15
Check-out: March 18
Confirmation #: MR123456

SCHEDULE:
March 15 - Evening: Welcome Reception (6 PM)
March 16 - Conference Day 1 (9 AM - 5 PM)
March 17 - Conference Day 2 (9 AM - 4 PM)

Please let me know if you need any modifications.

Best regards,
Casey Gray
Travel Coordinator
Office: (555) 345-6789""",
        date=sub_date(now, days=1),
    ),
    Mail(
        id=6,
        from_=MailSender(name="Jamie Johnson", email="jamie.johnson@example.com"),
        subject="Q1 2024 Financial Performance Review",
        body="""Dear Leadership Team,

Please find attached our Q1 2024 financial analysis report. Key highlights:

PERFORMANCE METRICS:
• Revenue: $12.4M (+15% YoY)
• Operating Expenses: $8.2M (-3% vs. budget)
• Net Profit Margin: 18.5% (+2.5% vs. Q4 2023)

AREAS OF OPTIMIZATION:
1. Cloud infrastructure costs (+22% over budget)
2. Marketing spend efficiency (-8% ROI vs. target)
3. Office operational costs (+5% vs. forecast)

I've scheduled a detailed review for Thursday at 2 PM EST. Calendar invite to follow.

Best regards,
Jamie Johnson
Chief Financial Officer
Ext: 4567""",
        date=sub_date(now, days=2),
    ),
    Mail(
        id=7,
        from_=MailSender(
            name="Riley Davis", email="riley.davis@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=7")
        ),
        subject="[Mandatory] New DevOps Tools Training Session",
        body="""Hello Development Team,

This is a reminder about next week's mandatory training session on our updated DevOps toolkit.

📅 Date: Tuesday, March 19
⏰ Time: 10:00 AM - 12:30 PM EST
📍 Location: Virtual (Zoom link below)

We'll be covering:
• GitLab CI/CD pipeline improvements
• Docker container optimization
• Kubernetes cluster management
• New monitoring tools integration

Prerequisites:
1. Install Docker Desktop 4.25
2. Update VS Code to latest version
3. Complete pre-training survey (link attached)

Zoom Link: https://zoom.us/j/123456789
Password: DevOps2024

--
Riley Davis
DevOps Lead
Technical Operations
M: (555) 777-8888""",
        date=sub_date(now, days=2),
    ),
    Mail(
        id=8,
        unread=True,
        from_=MailSender(
            name="Kelly Wilson", email="kelly.wilson@example.com", avatar=Avatar(src="https://i.pravatar.cc/128?u=8")
        ),
        subject="🎉 Happy Birthday!",
        body="""Dear [Name],

On behalf of the entire team, wishing you a fantastic birthday! 🎂

We've organized a small celebration in the break room at 3 PM today. Cake and refreshments will be served!

Your dedication and positive energy make our workplace better every day. Here's to another great year ahead!

Best wishes,
Kelly & The HR Team

P.S. Don't forget to check your email for a special birthday surprise from the company! 🎁

--
Kelly Wilson
HR Director
Human Resources Department
Tel: (555) 999-0000""",
        date=sub_date(now, days=2),
    ),
    Mail(
        id=9,
        from_=MailSender(name="Drew Moore", email="drew.moore@example.com"),
        subject="Website Redesign Feedback Request - Phase 2",
        body="""Hi there,

We're entering Phase 2 of our website redesign project and would value your input on the latest iterations.

New Features Implementation:
1. Dynamic product catalog
2. Enhanced search functionality
3. Personalized user dashboard
4. Mobile-responsive navigation

Review Links:
• Staging Environment: https://staging.example.com
• Design Specs: [Figma Link]
• User Flow Documentation: [Confluence Link]

Please provide feedback by EOD Friday. Key areas to focus on:
- User experience
- Navigation flow
- Content hierarchy
- Mobile responsiveness

Your insights will be crucial for our final implementation decisions.

Thanks in advance,
Drew Moore
UX Design Lead
Product Design Team""",
        date=sub_date(now, days=5),
    ),
    Mail(
        id=10,
        from_=MailSender(name="Jordan Taylor", email="jordan.taylor@example.com"),
        subject="Corporate Wellness Program - Membership Renewal",
        body="""Dear Valued Member,

Your corporate wellness program membership is due for renewal on April 1st, 2024.

NEW AMENITIES:
✨ Expanded yoga studio
🏋️ State-of-the-art cardio equipment
🧘 Meditation room
👥 Additional group fitness classes

RENEWAL BENEFITS:
• 15% early bird discount
• 3 complimentary personal training sessions
• Free wellness assessment
• Access to new mobile app

To schedule a tour or discuss renewal options, please book a time here: [Booking Link]

Stay healthy!

Best regards,
Jordan Taylor
Corporate Wellness Coordinator
Downtown Fitness Center
Tel: (555) 123-7890""",
        date=sub_date(now, days=5),
    ),
    Mail(
        id=11,
        unread=True,
        from_=MailSender(name="Morgan Anderson", email="morgan.anderson@example.com"),
        subject="Important: Updates to Your Corporate Insurance Policy",
        body="""Dear [Employee Name],

This email contains important information about changes to your corporate insurance coverage effective April 1, 2024.

KEY UPDATES:
1. Health Insurance
   • Reduced co-pay for specialist visits ($35 → $25)
   • Extended telehealth coverage
   • New mental health benefits

2. Dental Coverage
   • Increased annual maximum ($1,500 → $2,000)
   • Added orthodontic coverage for dependents

3. Vision Benefits
   • Enhanced frame allowance
   • New LASIK discount program

Please review the attached documentation carefully and complete the acknowledgment form by March 25th.

Questions? Join our virtual info session:
📅 March 20th, 2024
⏰ 11:00 AM EST
🔗 [Teams Link]

Regards,
Morgan Anderson
Benefits Coordinator
HR Department""",
        date=sub_date(now, days=12),
    ),
    Mail(
        id=12,
        from_=MailSender(name="Casey Thomas", email="casey.thomas@example.com"),
        subject='📚 March Book Club Meeting: "The Great Gatsby"',
        body="""Hello Book Lovers!

I hope you're enjoying F. Scott Fitzgerald's masterpiece! Our next meeting details:

📅 Thursday, March 21st
⏰ 5:30 PM - 7:00 PM
📍 Main Conference Room (or Zoom)

Discussion Topics:
1. Symbolism of the green light
2. The American Dream theme
3. Character development
4. Social commentary

Please bring your suggestions for April's book selection!

Refreshments will be provided 🍪

RSVP by replying to this email.

Happy reading!
Casey

--
Casey Thomas
Book Club Coordinator
Internal Culture Committee""",
        date=sub_date(now, days=30),
    ),
    Mail(
        id=13,
        from_=MailSender(name="Jamie Jackson", email="jamie.jackson@example.com"),
        subject="🍳 Company Cookbook Project - Recipe Submission Reminder",
        body="""Dear Colleagues,

Final call for our company cookbook project submissions!

Guidelines for Recipe Submission:
1. Include ingredients list with measurements
2. Step-by-step instructions
3. Cooking time and servings
4. Photo of the finished dish (optional)
5. Any cultural or personal significance

Submission Deadline: March 22nd, 2024

We already have some amazing entries:
• Sarah's Famous Chili
• Mike's Mediterranean Pasta
• Lisa's Vegan Brownies
• Tom's Family Paella

All proceeds from cookbook sales will support our local food bank.

Submit here: [Form Link]

Cooking together,
Jamie Jackson
Community Engagement Committee
Ext. 5432""",
        date=sub_date(now, days=30),
    ),
    Mail(
        id=14,
        from_=MailSender(name="Riley White", email="riley.white@example.com"),
        subject="🧘‍♀️ Updated Corporate Wellness Schedule - Spring 2024",
        body="""Dear Wellness Program Participants,

Our Spring 2024 wellness schedule is now available!

NEW CLASSES:
Monday:
• 7:30 AM - Morning Flow Yoga
• 12:15 PM - HIIT Express
• 5:30 PM - Meditation Basics

Wednesday:
• 8:00 AM - Power Vinyasa
• 12:00 PM - Desk Stretching
• 4:30 PM - Mindfulness Workshop

Friday:
• 7:45 AM - Gentle Yoga
• 12:30 PM - Stress Management
• 4:45 PM - Weekend Wind-Down

All classes available in-person and via Zoom.
Download our app to reserve your spot!

Namaste,
Riley White
Corporate Wellness Instructor
Wellness & Benefits Team""",
        date=sub_date(now, days=30),
    ),
    Mail(
        id=15,
        from_=MailSender(name="Kelly Harris", email="kelly.harris@example.com"),
        subject='📚 Book Launch Event: "Digital Transformation in the Modern Age"',
        body="""Dear [Name],

You're cordially invited to the launch of my new book, "Digital Transformation in the Modern Age: A Leadership Guide"

EVENT DETAILS:
📅 Date: April 15th, 2024
⏰ Time: 6:00 PM - 8:30 PM EST
📍 Grand Hotel Downtown
   123 Business Ave.

AGENDA:
6:00 PM - Welcome Reception
6:30 PM - Keynote Presentation
7:15 PM - Q&A Session
7:45 PM - Book Signing
8:00 PM - Networking

Light refreshments will be served.
Each attendee will receive a signed copy of the book.

RSVP by April 1st: [Event Link]

Looking forward to sharing this milestone with you!

Best regards,
Kelly Harris
Digital Strategy Consultant
Author, "Digital Transformation in the Modern Age""",
        date=sub_date(now, days=30),
    ),
    Mail(
        id=16,
        from_=MailSender(name="Drew Martin", email="drew.martin@example.com"),
        subject="🚀 TechCon 2024: Early Bird Registration Now Open",
        body="""Dear Tech Enthusiasts,

Registration is now open for TechCon 2024: "Innovation at Scale"

CONFERENCE HIGHLIGHTS:
📅 May 15-17, 2024
📍 Tech Convention Center

KEYNOTE SPEAKERS:
• Sarah Johnson - CEO, Future Tech Inc.
• Dr. Michael Chang - AI Research Director
• Lisa Rodriguez - Cybersecurity Expert

TRACKS:
1. AI/ML Innovation
2. Cloud Architecture
3. DevSecOps
4. Digital Transformation
5. Emerging Technologies

EARLY BIRD PRICING (ends April 1):
Full Conference Pass: $899 (reg. $1,199)
Team Discount (5+): 15% off

Register here: [Registration Link]

Best regards,
Drew Martin
Conference Director
TechCon 2024""",
        date=sub_date(now, days=34),
    ),
    Mail(
        id=17,
        from_=MailSender(name="Alex Thompson", email="alex.thompson@example.com"),
        subject="🎨 Modern Perspectives: Contemporary Art Exhibition",
        body="""Hi there,

Hope you're well! I wanted to personally invite you to an extraordinary art exhibition this weekend.

"Modern Perspectives: Breaking Boundaries"
📅 Saturday & Sunday
⏰ 10 AM - 6 PM
📍 Metropolitan Art Gallery

FEATURED ARTISTS:
• Maria Chen - Mixed Media
• James Wright - Digital Art
• Sofia Patel - Installation
• Robert Kim - Photography

SPECIAL EVENTS:
• Artist Talk: Saturday, 2 PM
• Workshop: Sunday, 11 AM
• Wine Reception: Saturday, 5 PM

Would love to meet you there! Let me know if you'd like to go together.

Best,
Alex Thompson
Curator
Metropolitan Art Gallery
Tel: (555) 234-5678""",
        date=sub_date(now, days=45),
    ),
    Mail(
        id=18,
        from_=MailSender(name="Jordan Garcia", email="jordan.garcia@example.com"),
        subject='🤝 Industry Networking Event: "Connect & Innovate 2024"',
        body="""Dear Professional Network,

You're invited to our premier networking event!

EVENT DETAILS:
📅 March 28th, 2024
⏰ 6:00 PM - 9:00 PM
📍 Innovation Hub
   456 Enterprise Street

SPEAKERS:
• Mark Thompson - "Future of Work"
• Dr. Sarah Chen - "Innovation Trends"
• Robert Mills - "Digital Leadership"

SCHEDULE:
6:00 - Registration & Welcome
6:30 - Keynote Presentations
7:30 - Networking Session
8:30 - Panel Discussion

Complimentary hors d'oeuvres and beverages will be served.

RSVP Required: [Registration Link]

Best regards,
Jordan Garcia
Event Coordinator
Professional Networking Association""",
        date=sub_date(now, days=48),
    ),
    Mail(
        id=19,
        from_=MailSender(name="Taylor Rodriguez", email="taylor.rodriguez@example.com"),
        subject="🌟 Community Service Day - Volunteer Opportunities",
        body="""Dear Colleagues,

Join us for our annual Community Service Day!

EVENT DETAILS:
📅 Saturday, April 6th, 2024
⏰ 9:00 AM - 3:00 PM
📍 Multiple Locations

VOLUNTEER OPPORTUNITIES:
1. City Park Cleanup
   • Garden maintenance
   • Trail restoration
   • Playground repair

2. Food Bank
   • Sorting donations
   • Packing meals
   • Distribution

3. Animal Shelter
   • Dog walking
   • Facility cleaning
   • Social media support

All volunteers receive:
• Company volunteer t-shirt
• Lunch and refreshments
• Certificate of participation
• 8 hours community service credit

Sign up here: [Volunteer Portal]

Making a difference together,
Taylor Rodriguez
Community Outreach Coordinator
Corporate Social Responsibility Team""",
        date=sub_date(now, days=55),
    ),
    Mail(
        id=20,
        from_=MailSender(name="Morgan Lopez", email="morgan.lopez@example.com"),
        subject="🚗 Vehicle Maintenance Reminder: 30,000 Mile Service",
        body="""Dear Valued Customer,

Your vehicle is due for its 30,000-mile maintenance service.

RECOMMENDED SERVICES:
• Oil and filter change
• Tire rotation and alignment
• Brake system inspection
• Multi-point safety inspection
• Fluid level check and top-off
• Battery performance test

SERVICE CENTER DETAILS:
📍 Downtown Auto Care
   789 Service Road

☎️ (555) 987-6543

Available Appointments:
• Monday-Friday: 7:30 AM - 6:00 PM
• Saturday: 8:00 AM - 2:00 PM

Schedule online: [Booking Link]
or call our service desk directly.

Drive safely,
Morgan Lopez
Service Coordinator
Downtown Auto Care
Emergency: (555) 987-6544""",
        date=sub_date(now, days=60),
    ),
]
