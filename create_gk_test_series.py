"""
Script to create General Knowledge (GK) questions and 10 Test Series in the database.
Covers GK - India, GK - West Bengal, GK - Global, GK - Science, Sports, Environment, etc.
"""

from datetime import datetime, timezone
from decimal import Decimal
import app.models.question_option
import app.models.topic
import app.models.series_question
import app.models.question
import app.models.test_series
import app.models.user
from app.database import SessionLocal
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.series_question import SeriesQuestion
from app.models.test_series import TestSeries
from app.models.topic import Topic


def seed_gk_data():
    db = SessionLocal()
    try:
        print("Starting GK Test Series creation...")

        # 1. Create or get Topics
        topic_data = [
            ("GK - India", "#FF9933"),
            ("GK - West Bengal", "#138808"),
            ("GK - Global", "#000080"),
            ("GK - Science & Tech", "#E03C11"),
            ("GK - Sports & Environment", "#8B5CF6"),
        ]

        topics_map = {}
        for name, color in topic_data:
            existing = db.query(Topic).filter(Topic.name == name).first()
            if not existing:
                t = Topic(name=name, color=color, org_id=1, is_active=True)
                db.add(t)
                db.flush()
                topics_map[name] = t.id
                print(f"Created topic: {name} (ID: {t.id})")
            else:
                topics_map[name] = existing.id
                print(f"Existing topic found: {name} (ID: {existing.id})")

        # 2. Define 10 Test Series with Questions & Options
        test_series_definitions = [
            # -------------------------------------------------------------
            # SERIES 1: GK - India: History & Freedom Movement
            # -------------------------------------------------------------
            {
                "title": "GK - India: History & Freedom Movement",
                "topic": "GK - India",
                "duration": 600,  # 10 minutes
                "questions": [
                    {
                        "q": "<p>Who was the first Governor-General of Independent India?</p>",
                        "opts": [
                            ("Lord Mountbatten", True),
                            ("C. Rajagopalachari", False),
                            ("Lord Wavell", False),
                            ("Jawaharlal Nehru", False),
                        ],
                    },
                    {
                        "q": "<p>In which year did the Quit India Movement begin under Mahatma Gandhi's leadership?</p>",
                        "opts": [
                            ("1942", True),
                            ("1930", False),
                            ("1920", False),
                            ("1945", False),
                        ],
                    },
                    {
                        "q": "<p>Who gave the famous slogan 'Give me blood, and I shall give you freedom!'?</p>",
                        "opts": [
                            ("Netaji Subhas Chandra Bose", True),
                            ("Bhagat Singh", False),
                            ("Mahatma Gandhi", False),
                            ("Bal Gangadhar Tilak", False),
                        ],
                    },
                    {
                        "q": "<p>The tragic Jallianwala Bagh massacre took place in which city in 1919?</p>",
                        "opts": [
                            ("Amritsar", True),
                            ("Lahore", False),
                            ("Jalandhar", False),
                            ("Delhi", False),
                        ],
                    },
                    {
                        "q": "<p>Who was the founder of the ancient Maurya Empire in India?</p>",
                        "opts": [
                            ("Chandragupta Maurya", True),
                            ("Ashoka the Great", False),
                            ("Bindusara", False),
                            ("Samudragupta", False),
                        ],
                    },
                    {
                        "q": "<p>Which decisive battle fought in 1757 laid the foundation of British rule in Bengal and India?</p>",
                        "opts": [
                            ("Battle of Plassey", True),
                            ("Battle of Buxar", False),
                            ("Third Battle of Panipat", False),
                            ("Battle of Haldighati", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 2: GK - India: Geography & Rivers
            # -------------------------------------------------------------
            {
                "title": "GK - India: Geography & Rivers",
                "topic": "GK - India",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which river is commonly known as the 'Dakshin Ganga' (Ganga of the South)?</p>",
                        "opts": [
                            ("Godavari", True),
                            ("Kaveri", False),
                            ("Krishna", False),
                            ("Narmada", False),
                        ],
                    },
                    {
                        "q": "<p>Which is the highest mountain peak located entirely within India?</p>",
                        "opts": [
                            ("Kangchenjunga", True),
                            ("Nanda Devi", False),
                            ("K2 (Godwin-Austen)", False),
                            ("Kamet", False),
                        ],
                    },
                    {
                        "q": "<p>Which state in India has the longest coastline?</p>",
                        "opts": [
                            ("Gujarat", True),
                            ("Andhra Pradesh", False),
                            ("Tamil Nadu", False),
                            ("Maharashtra", False),
                        ],
                    },
                    {
                        "q": "<p>Majuli, the world's largest river island, is situated on which river in Assam?</p>",
                        "opts": [
                            ("Brahmaputra River", True),
                            ("Ganga River", False),
                            ("Subansiri River", False),
                            ("Barak River", False),
                        ],
                    },
                    {
                        "q": "<p>Which Indian river flows westward into the Arabian Sea through a rift valley?</p>",
                        "opts": [
                            ("Narmada", True),
                            ("Godavari", False),
                            ("Mahanadi", False),
                            ("Krishna", False),
                        ],
                    },
                    {
                        "q": "<p>Kaziranga National Park in Assam is world-famous for protecting which endangered animal?</p>",
                        "opts": [
                            ("Great One-horned Rhinoceros", True),
                            ("Royal Bengal Tiger", False),
                            ("Asian Elephant", False),
                            ("Asiatic Lion", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 3: GK - India: Constitution & Polity
            # -------------------------------------------------------------
            {
                "title": "GK - India: Constitution & Polity",
                "topic": "GK - India",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Who was the Chairman of the Drafting Committee of the Indian Constitution?</p>",
                        "opts": [
                            ("Dr. B. R. Ambedkar", True),
                            ("Dr. Rajendra Prasad", False),
                            ("Jawaharlal Nehru", False),
                            ("Sardar Vallabhbhai Patel", False),
                        ],
                    },
                    {
                        "q": "<p>Which Articles of the Indian Constitution guarantee the Fundamental Right to Equality?</p>",
                        "opts": [
                            ("Articles 14 to 18", True),
                            ("Articles 19 to 22", False),
                            ("Articles 23 to 24", False),
                            ("Articles 25 to 28", False),
                        ],
                    },
                    {
                        "q": "<p>What is the minimum age eligibility required to be elected as the President of India?</p>",
                        "opts": [
                            ("35 years", True),
                            ("30 years", False),
                            ("25 years", False),
                            ("40 years", False),
                        ],
                    },
                    {
                        "q": "<p>Which Constitutional Amendment added 'Socialist', 'Secular', and 'Integrity' to the Preamble in 1976?</p>",
                        "opts": [
                            ("42nd Amendment Act", True),
                            ("44th Amendment Act", False),
                            ("86th Amendment Act", False),
                            ("73rd Amendment Act", False),
                        ],
                    },
                    {
                        "q": "<p>Who serves as the ex-officio Chairman of the Rajya Sabha (Upper House of Parliament)?</p>",
                        "opts": [
                            ("Vice President of India", True),
                            ("Speaker of Lok Sabha", False),
                            ("Prime Minister of India", False),
                            ("President of India", False),
                        ],
                    },
                    {
                        "q": "<p>In 1959, the Panchayati Raj system was first inaugurated in Nagaur district of which Indian state?</p>",
                        "opts": [
                            ("Rajasthan", True),
                            ("Andhra Pradesh", False),
                            ("Gujarat", False),
                            ("Punjab", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 4: GK - West Bengal: History, Literature & Culture
            # -------------------------------------------------------------
            {
                "title": "GK - West Bengal: History, Literature & Culture",
                "topic": "GK - West Bengal",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Who composed the National Anthem of India, 'Jana Gana Mana'?</p>",
                        "opts": [
                            ("Rabindranath Tagore", True),
                            ("Bankim Chandra Chattopadhyay", False),
                            ("Kazi Nazrul Islam", False),
                            ("Michael Madhusudan Dutt", False),
                        ],
                    },
                    {
                        "q": "<p>In which year was the Partition of Bengal first announced by Viceroy Lord Curzon?</p>",
                        "opts": [
                            ("1905", True),
                            ("1911", False),
                            ("1947", False),
                            ("1899", False),
                        ],
                    },
                    {
                        "q": "<p>Who wrote the National Song of India, 'Vande Mataram', in his novel 'Anandamath'?</p>",
                        "opts": [
                            ("Bankim Chandra Chattopadhyay", True),
                            ("Rabindranath Tagore", False),
                            ("Sarat Chandra Chattopadhyay", False),
                            ("Ishwar Chandra Vidyasagar", False),
                        ],
                    },
                    {
                        "q": "<p>Who is widely revered as the 'Father of the Bengal Renaissance'?</p>",
                        "opts": [
                            ("Raja Ram Mohan Roy", True),
                            ("Swami Vivekananda", False),
                            ("Ishwar Chandra Vidyasagar", False),
                            ("Keshab Chandra Sen", False),
                        ],
                    },
                    {
                        "q": "<p>Who led the famous Chittagong Armoury Raid in 1930 during India's freedom movement?</p>",
                        "opts": [
                            ("Surya Sen (Masterda)", True),
                            ("Khudiram Bose", False),
                            ("Jatindranath Mukherjee (Bagha Jatin)", False),
                            ("Rash Behari Bose", False),
                        ],
                    },
                    {
                        "q": "<p>Which iconic historical fort in Kolkata served as a key stronghold during British colonial rule?</p>",
                        "opts": [
                            ("Fort William", True),
                            ("Fort St. George", False),
                            ("Asiatic Fort", False),
                            ("Victoria Fort", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 5: GK - West Bengal: Geography & State Symbols
            # -------------------------------------------------------------
            {
                "title": "GK - West Bengal: Geography & State Symbols",
                "topic": "GK - West Bengal",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>What is the official State Animal of West Bengal?</p>",
                        "opts": [
                            ("Fishing Cat (Mecho Biral)", True),
                            ("Royal Bengal Tiger", False),
                            ("Indian Elephant", False),
                            ("One-horned Rhinoceros", False),
                        ],
                    },
                    {
                        "q": "<p>Which river in West Bengal was historically called the 'Sorrow of Bengal' due to frequent floods?</p>",
                        "opts": [
                            ("Damodar River", True),
                            ("Hooghly River", False),
                            ("Teesta River", False),
                            ("Rupnarayan River", False),
                        ],
                    },
                    {
                        "q": "<p>The Sundarbans delta mangrove forest in West Bengal derives its name from which species of trees?</p>",
                        "opts": [
                            ("Sundari Tree (Heritiera fomes)", True),
                            ("Sal Tree", False),
                            ("Teak Tree", False),
                            ("Banyan Tree", False),
                        ],
                    },
                    {
                        "q": "<p>What is the official State Tree of West Bengal?</p>",
                        "opts": [
                            ("Chatim Tree (Devil's Tree)", True),
                            ("Banyan Tree", False),
                            ("Mango Tree", False),
                            ("Neem Tree", False),
                        ],
                    },
                    {
                        "q": "<p>Which scenic hill station in North Bengal is famously nicknamed the 'Queen of the Hills'?</p>",
                        "opts": [
                            ("Darjeeling", True),
                            ("Kalimpong", False),
                            ("Mirik", False),
                            ("Kurseong", False),
                        ],
                    },
                    {
                        "q": "<p>What is the official State Flower of West Bengal?</p>",
                        "opts": [
                            ("Night-flowering Jasmine (Shiuli / Parijat)", True),
                            ("Lotus", False),
                            ("Marigold", False),
                            ("Rose", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 6: GK - Global: World Geography & Capitals
            # -------------------------------------------------------------
            {
                "title": "GK - Global: World Geography & Capitals",
                "topic": "GK - Global",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which is the largest ocean on Earth by surface area and total water volume?</p>",
                        "opts": [
                            ("Pacific Ocean", True),
                            ("Atlantic Ocean", False),
                            ("Indian Ocean", False),
                            ("Arctic Ocean", False),
                        ],
                    },
                    {
                        "q": "<p>What is the official capital city of Australia?</p>",
                        "opts": [
                            ("Canberra", True),
                            ("Sydney", False),
                            ("Melbourne", False),
                            ("Brisbane", False),
                        ],
                    },
                    {
                        "q": "<p>Which river is globally recognized as the longest river in the world?</p>",
                        "opts": [
                            ("Nile River", True),
                            ("Amazon River", False),
                            ("Yangtze River", False),
                            ("Mississippi River", False),
                        ],
                    },
                    {
                        "q": "<p>Mount Kilimanjaro, the highest peak on the African continent, is located in which country?</p>",
                        "opts": [
                            ("Tanzania", True),
                            ("Kenya", False),
                            ("Uganda", False),
                            ("Ethiopia", False),
                        ],
                    },
                    {
                        "q": "<p>Which landlocked South American nation shares borders with Brazil, Argentina, and Bolivia?</p>",
                        "opts": [
                            ("Paraguay", True),
                            ("Uruguay", False),
                            ("Peru", False),
                            ("Ecuador", False),
                        ],
                    },
                    {
                        "q": "<p>The Strait of Gibraltar connects the Atlantic Ocean to which major sea?</p>",
                        "opts": [
                            ("Mediterranean Sea", True),
                            ("Red Sea", False),
                            ("Black Sea", False),
                            ("Baltic Sea", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 7: GK - Global: International Organizations & World History
            # -------------------------------------------------------------
            {
                "title": "GK - Global: International Organizations & World History",
                "topic": "GK - Global",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Where is the official headquarters of the United Nations (UN) located?</p>",
                        "opts": [
                            ("New York City, USA", True),
                            ("Geneva, Switzerland", False),
                            ("Paris, France", False),
                            ("Vienna, Austria", False),
                        ],
                    },
                    {
                        "q": "<p>In which year did World War II officially end with the surrender of the Axis powers?</p>",
                        "opts": [
                            ("1945", True),
                            ("1939", False),
                            ("1918", False),
                            ("1950", False),
                        ],
                    },
                    {
                        "q": "<p>Where is the International Court of Justice (ICJ) headquartered?</p>",
                        "opts": [
                            ("The Hague, Netherlands", True),
                            ("Geneva, Switzerland", False),
                            ("Brussels, Belgium", False),
                            ("London, UK", False),
                        ],
                    },
                    {
                        "q": "<p>The famous ancient UNESCO World Heritage site 'Machu Picchu' is located in which country?</p>",
                        "opts": [
                            ("Peru", True),
                            ("Chile", False),
                            ("Mexico", False),
                            ("Colombia", False),
                        ],
                    },
                    {
                        "q": "<p>Which United Nations agency was awarded the Nobel Peace Prize in 2020 for combatting global hunger?</p>",
                        "opts": [
                            ("World Food Programme (WFP)", True),
                            ("UNICEF", False),
                            ("World Health Organization (WHO)", False),
                            ("UNHCR", False),
                        ],
                    },
                    {
                        "q": "<p>Which nation was the birthplace of the Industrial Revolution in the mid-18th century?</p>",
                        "opts": [
                            ("Great Britain", True),
                            ("Germany", False),
                            ("United States", False),
                            ("France", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 8: GK - Science & Technology
            # -------------------------------------------------------------
            {
                "title": "GK - General Science & Technology",
                "topic": "GK - Science & Tech",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which gas comprises approximately 78% of Earth's atmosphere by volume?</p>",
                        "opts": [
                            ("Nitrogen", True),
                            ("Oxygen", False),
                            ("Carbon Dioxide", False),
                            ("Argon", False),
                        ],
                    },
                    {
                        "q": "<p>What is the chemical symbol for Gold in the periodic table?</p>",
                        "opts": [
                            ("Au", True),
                            ("Ag", False),
                            ("Fe", False),
                            ("Pb", False),
                        ],
                    },
                    {
                        "q": "<p>Which organ in the human body regulates blood glucose by producing Insulin?</p>",
                        "opts": [
                            ("Pancreas", True),
                            ("Liver", False),
                            ("Kidney", False),
                            ("Thyroid", False),
                        ],
                    },
                    {
                        "q": "<p>What was the name of ISRO's historic space mission that landed on the Moon's South Pole in 2023?</p>",
                        "opts": [
                            ("Chandrayaan-3", True),
                            ("Chandrayaan-2", False),
                            ("Mangalyaan", False),
                            ("Aditya-L1", False),
                        ],
                    },
                    {
                        "q": "<p>Deficiency of Vitamin C (Ascorbic Acid) leads to which disease?</p>",
                        "opts": [
                            ("Scurvy", True),
                            ("Beriberi", False),
                            ("Rickets", False),
                            ("Night Blindness", False),
                        ],
                    },
                    {
                        "q": "<p>What is the approximate speed of light in a vacuum?</p>",
                        "opts": [
                            ("3 × 10^8 meters per second", True),
                            ("3 × 10^5 meters per second", False),
                            ("1.5 × 10^8 meters per second", False),
                            ("3 × 10^10 meters per second", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 9: GK - Sports & Awards
            # -------------------------------------------------------------
            {
                "title": "GK - Sports, Awards & Honours",
                "topic": "GK - Sports & Environment",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which country won the FIFA World Cup 2022 held in Qatar?</p>",
                        "opts": [
                            ("Argentina", True),
                            ("France", False),
                            ("Brazil", False),
                            ("Croatia", False),
                        ],
                    },
                    {
                        "q": "<p>Who won India's first-ever Olympic Gold Medal in Track and Field Athletics (Javelin Throw)?</p>",
                        "opts": [
                            ("Neeraj Chopra", True),
                            ("Abhinav Bindra", False),
                            ("Milkha Singh", False),
                            ("PV Sindhu", False),
                        ],
                    },
                    {
                        "q": "<p>Who were the first recipients of India's highest civilian honor, the Bharat Ratna, in 1954?</p>",
                        "opts": [
                            ("C. Rajagopalachari, S. Radhakrishnan, and C. V. Raman", True),
                            ("Jawaharlal Nehru", False),
                            ("Mahatma Gandhi", False),
                            ("Dr. B. R. Ambedkar", False),
                        ],
                    },
                    {
                        "q": "<p>How many players per team are on the field during a standard match of Cricket?</p>",
                        "opts": [
                            ("11", True),
                            ("10", False),
                            ("12", False),
                            ("9", False),
                        ],
                    },
                    {
                        "q": "<p>The Davis Cup is a premier international team event in which sport?</p>",
                        "opts": [
                            ("Lawn Tennis", True),
                            ("Badminton", False),
                            ("Golf", False),
                            ("Table Tennis", False),
                        ],
                    },
                    {
                        "q": "<p>Who holds the historic record for scoring 100 international centuries in Cricket?</p>",
                        "opts": [
                            ("Sachin Tendulkar", True),
                            ("Virat Kohli", False),
                            ("Ricky Ponting", False),
                            ("Jacques Kallis", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 10: GK - Environment, Ecology & Current Awareness
            # -------------------------------------------------------------
            {
                "title": "GK - Environment, Ecology & Current Awareness",
                "topic": "GK - Sports & Environment",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>World Environment Day is observed globally every year on which date?</p>",
                        "opts": [
                            ("June 5", True),
                            ("April 22", False),
                            ("March 22", False),
                            ("September 16", False),
                        ],
                    },
                    {
                        "q": "<p>Which Ramsar wetland site located near Kolkata acts as a vital natural sewage recycling system?</p>",
                        "opts": [
                            ("East Kolkata Wetlands", True),
                            ("Deepor Beel", False),
                            ("Chilika Lake", False),
                            ("Bhoj Wetland", False),
                        ],
                    },
                    {
                        "q": "<p>Which greenhouse gas contributed primarily by human fossil fuel combustion causes global warming?</p>",
                        "opts": [
                            ("Carbon Dioxide (CO2)", True),
                            ("Nitrogen (N2)", False),
                            ("Oxygen (O2)", False),
                            ("Helium (He)", False),
                        ],
                    },
                    {
                        "q": "<p>Silent Valley National Park, famous for its undisturbed tropical evergreen rainforest, is in which Indian state?</p>",
                        "opts": [
                            ("Kerala", True),
                            ("Tamil Nadu", False),
                            ("Karnataka", False),
                            ("Uttarakhand", False),
                        ],
                    },
                    {
                        "q": "<p>In which year was 'Project Tiger' launched in India to save Bengal tigers from extinction?</p>",
                        "opts": [
                            ("1973", True),
                            ("1980", False),
                            ("1992", False),
                            ("1968", False),
                        ],
                    },
                    {
                        "q": "<p>Which atmospheric layer contains the Ozone Layer that absorbs harmful ultraviolet rays?</p>",
                        "opts": [
                            ("Stratosphere", True),
                            ("Troposphere", False),
                            ("Mesosphere", False),
                            ("Thermosphere", False),
                        ],
                    },
                ],
            },
        ]

        # 3. Insert Questions and Test Series
        valid_until_dt = datetime(2030, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        for s_idx, series_data in enumerate(test_series_definitions, start=1):
            print(f"\n--- Creating Series {s_idx}/10: {series_data['title']} ---")
            
            # Step A: Insert Questions and Options
            question_ids = []
            topic_id = topics_map[series_data["topic"]]

            for q_data in series_data["questions"]:
                question_obj = Question(
                    question=q_data["q"],
                    organization_id=1,
                    user_id=1,
                    is_global=True,
                    marks=Decimal("1.00"),
                    is_active=True,
                    topic_id=topic_id,
                )
                db.add(question_obj)
                db.flush()  # get question_obj.id

                for opt_text, is_corr in q_data["opts"]:
                    option_obj = QuestionOption(
                        q_id=question_obj.id,
                        ans=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(option_obj)
                
                question_ids.append(question_obj.id)

            db.flush()

            # Step B: Insert Test Series
            test_series = TestSeries(
                name=series_data["title"],
                access_type="public",
                valid_until=valid_until_dt,
                duration_seconds=series_data["duration"],
                is_active=True,
                org_id=1,
                created_by=1,
            )
            db.add(test_series)
            db.flush()  # get test_series.id

            # Step C: Link Questions via SeriesQuestion association
            for pos, q_id in enumerate(question_ids, start=1):
                sq = SeriesQuestion(
                    series_id=test_series.id,
                    question_id=q_id,
                    position=pos,
                )
                db.add(sq)

            db.commit()
            print(f"Successfully created Series '{series_data['title']}' (ID: {test_series.id}) with {len(question_ids)} questions.")

        print("\nAll 10 GK Test Series and questions successfully seeded into the database!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_gk_data()
