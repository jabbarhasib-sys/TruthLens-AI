"""
TruthLens AI – Database Seeding Script
Populates the SQLite database with a default hackathon judge user and realistic,
high-fidelity mock verification reports (both News and Image scans) containing
detailed metadata, GPS parameters, SafeSearch annotations, and AI reasoning.
"""
import sys
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import SessionLocal, Base, engine
from app.models.user import User
from app.models.analysis import Analysis
from app.core.security import get_password_hash

def seed_db():
    print("Connecting to database and verifying tables exist...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1a. Create Admin User
        admin_email = "admin@truthlens.ai"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"Admin '{admin_email}' already exists. Ensuring admin role...")
            existing_admin.role = "admin"
            existing_admin.full_name = "TruthLens Admin"
            existing_admin.is_active = True
            db.commit()
            admin_user = existing_admin
        else:
            print(f"Creating admin user '{admin_email}' with password '123456'...")
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("123456"),
                full_name="TruthLens Admin",
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Admin user created successfully.")

        # 1b. Create Default Judge User
        judge_email = "judge@hackathon.com"
        existing_user = db.query(User).filter(User.email == judge_email).first()
        if existing_user:
            print(f"User '{judge_email}' already exists. Updating fields...")
            existing_user.full_name = existing_user.full_name or "Hackathon Judge"
            existing_user.is_active = True
            db.commit()
            user = existing_user
        else:
            print(f"Creating default user '{judge_email}' with password '123456'...")
            user = User(
                email=judge_email,
                hashed_password=get_password_hash("123456"),
                full_name="Hackathon Judge",
                role="user",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Default user created successfully.")


        # 2. Clear old demo analyses to avoid duplicates during multiple runs
        db.query(Analysis).filter(Analysis.user_id == user.id).delete()
        db.commit()
        print("Cleared previous analysis reports for the seed user.")

        # 3. Insert News Analysis 1 (LOW RISK / Artemis Lunar Mission)
        print("Seeding News Analysis 1 (Artemis Mission - Low Risk)...")
        news_artemis = Analysis(
            id=str(uuid.uuid4()),
            type="news",
            query="NASA launches its new Artemis lunar rover to explore south pole water ice reserves.",
            status="completed",
            trust_score=96.0,
            risk_level="LOW",
            created_at=datetime.utcnow(),
            user_id=user.id,
            details={
                "is_mock": True,
                "scoring_breakdown": {
                    "deductions": [],
                    "bonuses": [
                        {"text": "Matches verified reports from reputable NASA science bulletins.", "url": "https://www.nasa.gov/artemis", "source": "NASA"},
                        {"text": "Corroborated by Snopes Fact-Checking Archive.", "url": "https://www.snopes.com/factchecks/nasa-lunar-water-ice-rover/", "source": "Snopes"},
                        {"text": "Direct citation sources match high-authority media domains (Reuters, BBC).", "url": "https://www.reuters.com/science/nasa-artemis-moon-water-ice-rover", "source": "Reuters"}
                    ]
                },
                "ai_reasoning": (
                    "### Executive Summary\n"
                    "The claim stating that NASA is launching a lunar rover as part of the Artemis program "
                    "to investigate water ice at the south pole is **fully verified and authentic**.\n\n"
                    "### Findings & Credibility Check\n"
                    "- **Official Press Releases**: NASA has published official press packets for the VIPER "
                    "lunar rover and Artemis campaign, detailing water ice extraction projects.\n"
                    "- **Independent Verification**: PolitiFact and Snopes records confirm the scope, budget, and timeline of the rover launch.\n"
                    "- **Media Alignment**: Coverage in BBC Science and Reuters matches NASA's technical specifications exactly.\n\n"
                    "### Conclusion\n"
                    "No indicators of misinformation or fabrication are present. Trust level is exceptional."
                ),
                "fact_checks": [
                    {
                        "claimText": "NASA plans to launch a lunar rover to map water ice at the South Pole.",
                        "claimant": "Scientific American Reports",
                        "claimDate": "2026-05-10T00:00:00Z",
                        "claimReview": [
                            {
                                "publisher": {"name": "Snopes", "site": "snopes.com"},
                                "url": "https://www.snopes.com/factchecks/nasa-lunar-water-ice-rover/",
                                "textualRating": "True",
                                "languageCode": "en"
                            }
                        ]
                    }
                ],
                "news_reports": [
                    {
                        "title": "NASA's Artemis Campaign: Sending Rovers to Map Moon Water Ice Reserves",
                        "source": "Reuters",
                        "url": "https://www.reuters.com/science/nasa-artemis-moon-water-ice-rover",
                        "published_at": "2026-06-02T14:35:00Z",
                        "description": "NASA engineers are putting the final touches on the rover designed to navigate the permanent shadows of the lunar south pole."
                    },
                    {
                        "title": "Mapping Lunar Ice: The Key to Long-term Human Habitation on the Moon",
                        "source": "BBC News",
                        "url": "https://www.bbc.com/news/science-environment-lunarmap",
                        "published_at": "2026-06-03T09:12:00Z",
                        "description": "Corroborated details from the European Space Agency show coordinated support for NASA's Artemis water mining efforts."
                    }
                ]
            }
        )
        db.add(news_artemis)

        # 4. Insert News Analysis 2 (CRITICAL RISK / Lemon Juice COVID Cure)
        print("Seeding News Analysis 2 (Lemon Juice COVID Cure - Critical Risk)...")
        news_lemon = Analysis(
            id=str(uuid.uuid4()),
            type="news",
            query="Drinking freshly squeezed warm lemon juice in the morning completely cures COVID-19.",
            status="completed",
            trust_score=12.0,
            risk_level="CRITICAL",
            created_at=datetime.utcnow(),
            user_id=user.id,
            details={
                "is_mock": True,
                "scoring_breakdown": {
                    "deductions": [
                        {"text": "Direct match with cataloged medical misinformation in Google Fact Check DB.", "url": "https://www.politifact.com/factchecks/lemon-juice-doesnt-cure-covid-19/", "source": "PolitiFact"},
                        {"text": "Zero matching scientific papers or official health directives found.", "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters", "source": "WHO Myth Busters"},
                        {"text": "Language uses high-intensity sales triggers and absolute claim modifiers ('completely cures').", "url": "https://www.snopes.com/factchecks/lemon-water-prevent-coronavirus/", "source": "Snopes"}
                    ],
                    "bonuses": []
                },
                "ai_reasoning": (
                    "### Medical Advisory Alert\n"
                    "> [!CAUTION]\n"
                    "> This claim is dangerous medical misinformation. There is no clinical basis supporting lemon juice as a cure.\n\n"
                    "### Analysis of Rumor Origin\n"
                    "- **Social Media Dissemination**: This rumor originated in viral TikTok and WhatsApp forward messages in early 2020 and has resurfaced periodically.\n"
                    "- **Fact Check Status**: Categorically debunked as **False** by Snopes, WHO, and PolitiFact.\n"
                    "- **Scientific Consensus**: The World Health Organization (WHO) has officially warned that while lemons contain Vitamin C, they do not prevent or treat SARS-CoV-2 infections.\n\n"
                    "### Credibility Score Card\n"
                    "The claim has a Trust Score of 12%, indicating severe risk of active health deception."
                ),
                "fact_checks": [
                    {
                        "claimText": "Lemons and warm water serve as an immediate remedy to cure COVID-19.",
                        "claimant": "Viral WhatsApp Messages",
                        "claimDate": "2026-01-15T00:00:00Z",
                        "claimReview": [
                            {
                                "publisher": {"name": "PolitiFact", "site": "politifact.com"},
                                "url": "https://www.politifact.com/factchecks/lemon-juice-doesnt-cure-covid-19/",
                                "textualRating": "False / No Medical Basis",
                                "languageCode": "en"
                            }
                        ]
                    },
                    {
                        "claimText": "Drink warm lemon water to prevent coronavirus infection.",
                        "claimant": "Facebook Posts",
                        "claimDate": "2026-02-01T00:00:00Z",
                        "claimReview": [
                            {
                                "publisher": {"name": "Snopes", "site": "snopes.com"},
                                "url": "https://www.snopes.com/factchecks/lemon-water-prevent-coronavirus/",
                                "textualRating": "False",
                                "languageCode": "en"
                            }
                        ]
                    }
                ],
                "news_reports": [
                    {
                        "title": "WHO Warns Against Viral Home Remedy Rumors Surrounding Covid Treatment",
                        "source": "Associated Press",
                        "url": "https://apnews.com/article/fact-check-who-home-remedies-warning",
                        "published_at": "2026-03-10T11:00:00Z",
                        "description": "Medical experts urge citizens to seek approved clinical advice rather than forwarding unverified natural remedy claims."
                    }
                ]
            }
        )
        db.add(news_lemon)

        # 5. Insert Image Analysis 1 (CRITICAL RISK / UFO Deepfake)
        print("Seeding Image Analysis 1 (White House UFO - Critical Risk Deepfake)...")
        img_ufo = Analysis(
            id=str(uuid.uuid4()),
            type="image",
            query="leaked_whitehouse_ufo.jpg",
            status="completed",
            trust_score=8.5,
            risk_level="CRITICAL",
            created_at=datetime.utcnow(),
            user_id=user.id,
            details={
                "is_mock": True,
                "scoring_breakdown": {
                    "deductions": [
                        {"text": "Hive AI scan indicates 94% probability of generative adversarial generation (AI-generated).", "url": "https://thehive.ai", "source": "Hive Moderation AI"},
                        {"text": "Image is completely stripped of EXIF and camera firmware metadata.", "url": "", "source": ""},
                        {"text": "No match for original news release domains. Confined to conspiracy threads.", "url": "https://reddit.com/r/conspiracy/comments/synthetic-ufo-render", "source": "Reddit / Conspiracy Board"}
                    ],
                    "bonuses": []
                },
                "ai_reasoning": (
                    "### Forensic Deepfake Findings\n"
                    "Forensic inspection confirms this image is **AI-Generated / Manipulated**.\n\n"
                    "### Heuristics Breakdown\n"
                    "- **Generative Noise Signatures**: High-frequency analysis shows artificial pixel gradients and edge blur consistent with DALL-E 3 or Midjourney v6 rendering.\n"
                    "- **EXIF Analysis**: Standard metadata is entirely stripped. The image lacks camera manufacturer signatures, device models, or location logs, confirming it was saved directly from editing or generation tools.\n"
                    "- **Visual Entities**: Reverse-image search links the upload to discussion boards discussing synthetic media experiments.\n\n"
                    "### Final Verdict\n"
                    "This image is synthetic. Treat as an engineered hoax."
                ),
                "hive_data": {
                    "predictions": [
                        {"class": "ai_generated", "score": 0.94},
                        {"class": "manipulated", "score": 0.04},
                        {"class": "original", "score": 0.02}
                    ]
                },
                "vision_data": {
                    "safeSearchAnnotation": {
                        "adult": "VERY_UNLIKELY",
                        "spoof": "VERY_LIKELY",
                        "medical": "VERY_UNLIKELY",
                        "violence": "VERY_UNLIKELY",
                        "racy": "UNLIKELY"
                    },
                    "webDetection": {
                        "pagesWithMatchingImages": [
                            {
                                "pageTitle": "Conspiracy Theories & Synthetic Media Art Board",
                                "url": "https://reddit.com/r/conspiracy/comments/synthetic-ufo-render"
                            }
                        ]
                    }
                },
                "image_metadata": {
                    "has_exif": False,
                    "dimensions": {
                        "width": 1024,
                        "height": 1024,
                        "megapixels": 1.05,
                        "aspect_ratio": "1024:1024"
                    },
                    "format": {
                        "format": "JPEG",
                        "mode": "RGB"
                    },
                    "camera": {},
                    "settings": {},
                    "gps": {},
                    "anomalies": [
                        "No EXIF metadata detected — image may have been screenshot, stripped, or AI-generated."
                    ]
                }
            }
        )
        db.add(img_ufo)

        # 6. Insert Image Analysis 2 (HIGH RISK / Photoshopped Giant Bear)
        print("Seeding Image Analysis 2 (Manhattan Bear - High Risk Photoshop)...")
        img_bear = Analysis(
            id=str(uuid.uuid4()),
            type="image",
            query="giant_bear_manhattan.png",
            status="completed",
            trust_score=26.0,
            risk_level="HIGH",
            created_at=datetime.utcnow(),
            user_id=user.id,
            details={
                "is_mock": True,
                "scoring_breakdown": {
                    "deductions": [
                        {"text": "EXIF software metadata watermark identifies 'Adobe Photoshop CS6'.", "url": "", "source": ""},
                        {"text": "Hive AI scan indicates manipulated compositing (68% manipulated, 20% original).", "url": "https://thehive.ai", "source": "Hive Moderation AI"},
                        {"text": "safeSearch spoof index is high, suggesting composited elements.", "url": "https://cloud.google.com/vision/docs/detecting-safe-search", "source": "Google Vision API"}
                    ],
                    "bonuses": []
                },
                "ai_reasoning": (
                    "### Digital Alteration Report\n"
                    "This image contains **heavy editing and digital manipulation**.\n\n"
                    "### Forensic Trace Data\n"
                    "- **Software Watermark**: The EXIF metadata explicitly preserves a software watermark identifying **Adobe Photoshop CS6** as the last writing utility.\n"
                    "- **Composition Inconsistencies**: The shadows cast by the bear do not align with the ambient lighting of the surrounding Manhattan street structures, confirming a paste composite.\n"
                    "- **Social Context**: Debunked by local wildlife organizations who confirmed no black bears were active in New York County during this timeframe.\n\n"
                    "### Verdict\n"
                    "A composite photograph combining an authentic street shot with an external bear asset."
                ),
                "hive_data": {
                    "predictions": [
                        {"class": "ai_generated", "score": 0.12},
                        {"class": "manipulated", "score": 0.68},
                        {"class": "original", "score": 0.20}
                    ]
                },
                "vision_data": {
                    "safeSearchAnnotation": {
                        "adult": "VERY_UNLIKELY",
                        "spoof": "POSSIBLE",
                        "medical": "VERY_UNLIKELY",
                        "violence": "UNLIKELY",
                        "racy": "VERY_UNLIKELY"
                    },
                    "webDetection": {
                        "pagesWithMatchingImages": [
                            {
                                "pageTitle": "Photoshop Battles: Urban Wildlife Challenges",
                                "url": "https://example.org/photoshop-battles/bears-in-city"
                            }
                        ]
                    }
                },
                "image_metadata": {
                    "has_exif": True,
                    "dimensions": {
                        "width": 1200,
                        "height": 900,
                        "megapixels": 1.08,
                        "aspect_ratio": "1200:900"
                    },
                    "format": {
                        "format": "PNG",
                        "mode": "RGBA"
                    },
                    "camera": {
                        "Software": "Adobe Photoshop CS6 (Windows)"
                    },
                    "settings": {},
                    "gps": {},
                    "anomalies": [
                        "Editing software detected in EXIF: 'Adobe Photoshop CS6 (Windows)'. Image was altered after capture.",
                        "EXIF is present but camera make/model fields are absent — this is common in screenshots or edited files."
                    ]
                }
            }
        )
        db.add(img_bear)

        # 7. Insert Image Analysis 3 (LOW RISK / Yosemite Valley Sony Camera)
        print("Seeding Image Analysis 3 (Yosemite Sunrise - Low Risk Original)...")
        img_yosemite = Analysis(
            id=str(uuid.uuid4()),
            type="image",
            query="yosemite_sunrise_sony.jpg",
            status="completed",
            trust_score=97.8,
            risk_level="LOW",
            created_at=datetime.utcnow(),
            user_id=user.id,
            details={
                "is_mock": True,
                "scoring_breakdown": {
                    "deductions": [],
                    "bonuses": [
                        {"text": "Full EXIF metadata containing camera make, model, and lens specifics.", "url": "", "source": ""},
                        {"text": "Valid, unaltered camera firmware software tags detected.", "url": "", "source": ""},
                        {"text": "Embedded GPS location coordinates match Yosemite Valley landmarks.", "url": "https://www.google.com/maps?q=37.742541,-119.571412", "source": "Google Maps"},
                        {"text": "Hive AI scan indicates 98% original probability (0% AI / 2% manipulated).", "url": "https://thehive.ai", "source": "Hive Moderation AI"}
                    ]
                },
                "ai_reasoning": (
                    "### Authenticity Analysis\n"
                    "This image is **100% authentic and unaltered**.\n\n"
                    "### Camera & Lens Details\n"
                    "- **Hardware**: Captured using a high-end **Sony ILCE-7RM4 (Alpha 7R IV)** camera body paired with a **FE 24-70mm F2.8 GM** lens.\n"
                    "- **Camera Settings**: Aperture set to `f/8.0` with a focal length of `35mm` and exposure time of `1/250s` at `ISO 100`, optimal for tripod landscape photography at sunrise.\n\n"
                    "### Geolocation Mapping\n"
                    "- **Yosemite Geotag**: The image has embedded GPS tags indicating exactly `37.7425` Latitude and `-119.5714` Longitude. This coordinates place the camera at **Glacier Point, Yosemite Valley, California**, pointing directly East."
                ),
                "hive_data": {
                    "predictions": [
                        {"class": "ai_generated", "score": 0.00},
                        {"class": "manipulated", "score": 0.02},
                        {"class": "original", "score": 0.98}
                    ]
                },
                "vision_data": {
                    "safeSearchAnnotation": {
                        "adult": "VERY_UNLIKELY",
                        "spoof": "VERY_UNLIKELY",
                        "medical": "VERY_UNLIKELY",
                        "violence": "VERY_UNLIKELY",
                        "racy": "VERY_UNLIKELY"
                    },
                    "webDetection": {
                        "pagesWithMatchingImages": [
                            {
                                "pageTitle": "Yosemite Valley Landscape Galleries",
                                "url": "https://yosemitephotos.com/gallery/sunrise-glacier-point"
                            }
                        ]
                    }
                },
                "image_metadata": {
                    "has_exif": True,
                    "dimensions": {
                        "width": 6000,
                        "height": 4000,
                        "megapixels": 24.0,
                        "aspect_ratio": "3:2"
                    },
                    "format": {
                        "format": "JPEG",
                        "mode": "RGB"
                    },
                    "camera": {
                        "Make": "Sony",
                        "Model": "ILCE-7RM4",
                        "LensModel": "FE 24-70mm F2.8 GM",
                        "Software": "Sony Camera Firmware v1.20"
                    },
                    "settings": {
                        "FNumber": "8.0",
                        "ExposureTime": "1/250",
                        "ISOSpeedRatings": 100,
                        "FocalLength": "35.0"
                    },
                    "gps": {
                        "latitude": 37.742541,
                        "longitude": -119.571412,
                        "altitude_m": 2199.0,
                        "maps_url": "https://www.google.com/maps?q=37.742541,-119.571412"
                    },
                    "capture_time": {
                        "formatted": "June 05, 2026 at 05:48:32",
                        "iso8601": "2026-06-05T05:48:32",
                        "timestamp_unix": 1780705712
                    },
                    "anomalies": []
                }
            }
        )
        db.add(img_yosemite)

        db.commit()
        print("\nDatabase seeded successfully!")
        print("\nDemo Account Credentials:")
        print(f"  [ADMIN] Email: {admin_email}")
        print("          Password: 123456")
        print(f"  [USER]  Email: {judge_email}")
        print("          Password: 123456")
        print("\nPopulated 5 realistic analysis reports.")


    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
