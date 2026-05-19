import pickle
import os
import pandas as pd
import numpy as np
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIService:
    def __init__(self):
        self.model = None
        self.encoders = None
        self.knowledge = ""
        self.load_resources()
        self.init_intents()
        self.gemini_model = genai.GenerativeModel('gemini-flash-latest')

    def init_intents(self):
        # Mapping intents to answers and their semantic keyword sets
        self.intents = {
            "CAUSES": {
                "answer": "Diabetes may happen due to genetics, insulin resistance, lifestyle factors, or autoimmune conditions.",
                "keywords": ["why", "how", "cause", "happen", "occur", "affect", "came", "make", "diabetic"],
                "synonyms": {"sugar problem": "diabetes", "came for me": "happen", "occour": "occur", "happen": "occur"}
            },
            "SYMPTOMS": {
                "answer": "Common symptoms include thirst, frequent urination, fatigue, blurred vision, and slow wound healing.",
                "keywords": ["symptom", "sign", "look", "how know", "what happens", "feel", "notice"],
                "synonyms": {"sugar problem": "diabetes", "how know": "symptoms"}
            },
            "LOW_SUGAR_TREATMENT": {
                "answer": "Mild low sugar is often treated with 15g of fast-acting carbohydrates (like juice or honey). Follow the 15-15 Rule: eat, wait 15 mins, and re-check.",
                "keywords": ["low", "drop", "solution", "do", "treat", "fix", "become", "hypo"],
                "synonyms": {"sugar drops": "low sugar", "face": "treat"}
            },
            "DIET": {
                "answer": "A healthy diabetic diet focuses on whole grains (like chapati), lean proteins, vegetables, and fiber. Avoid sugary drinks and processed sweets.",
                "keywords": ["eat", "food", "meal", "snack", "best", "healthy", "control", "diet", "breakfast", "lunch", "dinner"],
                "synonyms": {"sugar patient": "diabetic", "eat": "diet"}
            },
            "HYDRATION": {
                "answer": "Staying hydrated is crucial. Most diabetics benefit from 8-10 glasses of water daily, especially if sugar levels are high.",
                "keywords": ["water", "drink", "amount", "need", "daily", "hydrate"],
                "synonyms": {"take": "drink", "amount": "quantity"}
            },
            "GENERAL": {
                "answer": "Diabetes is a condition where the body has trouble controlling blood sugar levels. It's usually managed long-term with healthy habits.",
                "keywords": ["what is", "about", "permanent", "cure", "long term", "life"],
                "synonyms": {"permanent": "long term"}
            }
        }
        
        # Setup TF-IDF Vectorizer for semantic matching
        self.faq = {
            # General & Overview
            "what is diabetes": "Diabetes is a condition where the body has trouble controlling blood sugar levels.",
            "what causes diabetes": "Diabetes can develop due to genetics, lifestyle factors, insulin resistance, or autoimmune conditions.",
            "what are the types of diabetes": "Common types include Type 1 diabetes, Type 2 diabetes, gestational diabetes, and prediabetes.",
            "what is type 1 diabetes": "Type 1 diabetes is a condition where the immune system attacks insulin-producing cells.",
            "what is type 2 diabetes": "Type 2 diabetes happens when the body becomes resistant to insulin or doesn’t make enough insulin.",
            "what is prediabetes": "Prediabetes means blood sugar levels are higher than normal but not high enough to be diagnosed as diabetes.",
            "can diabetes be cured": "Diabetes is usually managed rather than cured, but healthy habits can improve blood sugar control.",
            "is diabetes hereditary": "Genetics can increase the risk of developing diabetes.",
            "can children get diabetes": "Yes. Children can develop both Type 1 and Type 2 diabetes.",
            "how common is diabetes": "Diabetes is a very common health condition affecting millions of people worldwide.",
            "can diabetes affect daily life": "Yes. Diabetes can affect energy, eating habits, sleep, and daily routines, but proper management helps many people live healthy lives.",
            "why does diabetes happen": "Diabetes may happen due to genetics, insulin resistance, autoimmune conditions, or lifestyle factors.",
            "is diabetes permanent": "Diabetes is usually managed long-term, though healthy habits can greatly improve control.",
            "can stress cause diabetes": "Stress alone may not directly cause diabetes, but long-term stress can affect blood sugar and overall health.",
            "what age can diabetes start": "Diabetes can develop at almost any age, including childhood and adulthood.",
            "is diabetes contagious": "No. Diabetes does not spread from person to person.",
            "can thin people get diabetes": "Yes. People of any body type can develop diabetes.",
            "what happens inside the body during diabetes": "The body either does not produce enough insulin or cannot use insulin effectively, causing sugar to build up in the blood.",
            "why is insulin important": "Insulin helps move glucose from the bloodstream into the body’s cells for energy.",
            "can diabetes run in families": "Yes. Family history can increase diabetes risk.",
            "can diabetes affect daily life": "Yes. Diabetes can affect energy, eating habits, sleep, and daily routines, but proper management helps many people live healthy lives.",

            # Symptoms & How you feel
            "what are the symptoms of diabetes": "Common symptoms include thirst, frequent urination, fatigue, blurred vision, and slow wound healing.",
            "why am i always thirsty": "Excessive thirst can happen when blood sugar levels are high.",
            "why do i urinate frequently": "High blood sugar can cause the body to remove excess glucose through urine.",
            "can diabetes cause fatigue": "Yes. Blood sugar imbalance may lead to tiredness and low energy.",
            "does diabetes cause blurred vision": "High blood sugar may temporarily affect eyesight and cause blurry vision.",
            "why do wounds heal slowly": "Diabetes can affect blood circulation and slow the healing process.",
            "can diabetes cause weight loss": "Uncontrolled diabetes can sometimes cause unexplained weight loss.",
            "what are early signs of diabetes": "Early signs may include thirst, fatigue, frequent urination, and increased hunger.",
            "how do i know if i have diabetes": "A healthcare professional can diagnose diabetes using blood sugar tests.",
            "can diabetes cause dizziness": "Yes. Blood sugar fluctuations may sometimes cause dizziness.",
            "why do i feel tired after eating": "Blood sugar fluctuations after meals may sometimes cause tiredness.",
            "can diabetes cause headaches": "Yes. Both high and low blood sugar can sometimes lead to headaches.",
            "why am i hungry all the time": "Hunger may increase when the body has difficulty using glucose properly.",
            "can high sugar make me sleepy": "Yes. High blood sugar may cause fatigue and sleepiness.",
            "why do my hands shake": "Shaking can happen during low blood sugar episodes.",
            "can diabetes cause dry mouth": "Yes. High blood sugar may contribute to dry mouth and thirst.",
            "why do i wake up at night to urinate": "High blood sugar can increase urination frequency, including during the night.",
            "can diabetes cause itchy skin": "Yes. Dry skin and circulation changes may sometimes cause itching.",
            "why do i feel weak suddenly": "Sudden weakness may happen due to blood sugar fluctuations.",
            "can diabetes affect concentration": "Yes. Blood sugar imbalance may affect focus and concentration.",

            # Blood Sugar & Monitoring
            "what is a normal blood sugar level": "Normal fasting blood sugar is usually around 70–99 mg/dL.",
            "what is high blood sugar": "High blood sugar means glucose levels are above the healthy range.",
            "what is low blood sugar": "Low blood sugar, or hypoglycemia, happens when glucose levels drop too low.",
            "what is fasting blood sugar": "Fasting blood sugar is your glucose level after not eating for several hours.",
            "what is post-meal blood sugar": "Post-meal blood sugar is the glucose level measured after eating.",
            "is 140 sugar level normal": "A reading of 140 mg/dL may be normal after meals but depends on timing and individual health.",
            "is 200 blood sugar dangerous": "A blood sugar level of 200 mg/dL is high and should be monitored carefully.",
            "what happens if sugar levels increase": "High sugar levels may cause thirst, fatigue, dehydration, and long-term complications.",
            "why does blood sugar fluctuate": "Food, stress, exercise, sleep, and medications can affect blood sugar levels.",
            "how often should i check sugar": "The ideal frequency depends on your condition and your healthcare provider’s advice.",
            "why is my sugar high in the morning": "Morning sugar may rise due to hormones, late meals, or overnight glucose changes.",
            "can eating late increase sugar": "Yes. Late-night eating may affect blood sugar levels.",
            "does stress raise blood sugar": "Stress can sometimes increase blood sugar levels.",
            "can fever increase sugar levels": "Yes. Illness and fever may affect glucose levels.",
            "why do i feel sleepy with high sugar": "High blood sugar may lead to tiredness and low energy.",
            "can dehydration worsen high sugar": "Yes. Dehydration may make blood sugar levels harder to control.",
            "what are warning signs of very high sugar": "Extreme thirst, fatigue, blurred vision, and frequent urination may be warning signs.",
            "why is my sugar high even after medicine": "Food, stress, illness, or medication timing may affect sugar levels.",
            "can lack of exercise increase sugar": "Yes. Physical inactivity may contribute to higher sugar levels.",
            "how long does high sugar stay": "It depends on food intake, activity, medication, and overall health.",
            
            # Low Sugar (Hypoglycemia)
            "why do i suddenly feel shaky": "Sudden shakiness may happen during low blood sugar.",
            "can low sugar happen during sleep": "Yes. Low blood sugar can sometimes occur overnight.",
            "why do i sweat when sugar drops": "Sweating is a common symptom of low blood sugar.",
            "what drink helps low sugar quickly": "Juice or other fast-acting carbohydrate drinks may help raise low blood sugar quickly.",
            "can low sugar cause anxiety": "Yes. Hypoglycemia may sometimes cause nervousness or anxiety-like symptoms.",
            "why does my heart beat fast during low sugar": "Low blood sugar can trigger stress responses that increase heart rate.",
            "what happens if low sugar is ignored": "Severe low sugar may lead to confusion, fainting, or emergencies if untreated.",
            "can exercise cause low sugar": "Yes. Intense activity may sometimes lower blood sugar too much.",
            "can low sugar happen without diabetes": "Yes. Low blood sugar can occasionally occur in people without diabetes.",
            "how long does low sugar last": "It varies depending on the cause and how quickly it is treated.",
            
            # Diet & Food
            "is chapati better than rice for diabetes": "Whole grain chapati may help some people manage blood sugar better than refined rice.",
            "can diabetics eat eggs": "Yes. Eggs can be part of a balanced diabetic diet in moderation.",
            "is coffee safe for diabetics": "Many people with diabetes can drink coffee in moderation.",
            "can diabetics drink tea": "Yes. Unsweetened tea may be a suitable option.",
            "which snacks are good for diabetes": "Nuts, yogurt, fruits, and high-fiber snacks are often better choices.",
            "is peanut butter good for diabetics": "Peanut butter in moderation may fit into a balanced meal plan.",
            "can diabetics eat watermelon": "Watermelon can be eaten in moderation with portion awareness.",
            "what foods reduce sugar naturally": "Fiber-rich foods, vegetables, and balanced meals may help support sugar control.",
            "can diabetics eat at restaurants": "Yes. Choosing balanced meals and portion control can help.",
            "is fasting safe for diabetics": "Fasting may affect blood sugar, so medical guidance is recommended.",
            
            # Hydration
            "does drinking water lower sugar": "Staying hydrated may support healthy blood sugar management.",
            "why do diabetics feel thirsty often": "High blood sugar can increase thirst and dehydration.",
            "can dehydration increase blood sugar": "Yes. Dehydration may contribute to higher glucose levels.",
            "is coconut water good for diabetes": "Coconut water may be consumed in moderation depending on sugar content.",
            "how do i know if i am dehydrated": "Dry mouth, dark urine, and dizziness may be signs of dehydration.",
            "should i drink water during low sugar": "Hydration is important, but fast-acting carbohydrates are usually needed for low sugar.",
            "can too little water affect glucose": "Yes. Poor hydration may affect blood sugar balance.",
            "what drinks should diabetics avoid": "Sugary drinks and excessive sweetened beverages are generally best limited.",
            "are energy drinks bad for diabetes": "Many energy drinks contain high sugar and caffeine, which may affect glucose levels.",
            "is lemon water good for diabetes": "Lemon water without added sugar can be a refreshing low-calorie drink.",
            
            # Exercise
            "is morning walking good for diabetes": "Yes. Morning walking may help improve glucose control and energy levels.",
            "can exercise lower sugar immediately": "Physical activity may help lower blood sugar levels.",
            "is climbing stairs good for diabetics": "Stair climbing can be a helpful form of physical activity.",
            "can diabetics do weight training": "Yes. Strength exercises may support overall glucose management.",
            "is stretching useful for diabetes": "Stretching may improve flexibility and overall wellness.",
            "what exercises are safe for seniors with diabetes": "Walking, light stretching, and gentle exercises are often suitable options.",
            "can over exercise lower sugar too much": "Yes. Intense exercise may sometimes lead to low blood sugar.",
            "is dancing good exercise for diabetes": "Yes. Dancing can be a fun form of physical activity.",
            "how soon should i exercise after eating": "Many people benefit from light activity after meals, depending on their health needs.",
            "can sitting too long affect sugar": "Long periods of inactivity may affect blood sugar management."
        }
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.faq_questions = list(self.faq.keys())
            # Normalize questions to help vectorizer
            normalized_qs = [self.normalize_text(q) for q in self.faq_questions]
            
            # Using character n-grams makes it very robust to typos, broken English, and grammar mistakes
            self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
            self.faq_vectors = self.vectorizer.fit_transform(normalized_qs)
        except Exception as e:
            print("TF-IDF Setup Error:", e)
            self.vectorizer = None
            self.faq_vectors = None

    def load_resources(self):
        model_path = 'backend/data/diabetes_model.pkl'
        encoder_path = 'backend/data/encoders.pkl'
        knowledge_path = 'backend/data/knowledge.txt'

        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        if os.path.exists(encoder_path):
            with open(encoder_path, 'rb') as f:
                self.encoders = pickle.load(f)
        if os.path.exists(knowledge_path):
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                self.knowledge = f.read()

    def normalize_text(self, text):
        text = text.lower().strip()
        # Handle common informalities & regional phrasing
        text = re.sub(r'\bplz\b|\bpls\b', 'please', text)
        text = re.sub(r'\bu\b', 'you', text)
        text = re.sub(r'\br\b', 'are', text)
        text = re.sub(r'\bwanna\b', 'want to', text)
        text = re.sub(r'\bgonna\b', 'going to', text)
        text = re.sub(r'\bgotta\b', 'got to', text)
        text = re.sub(r'\bim\b', 'i am', text)
        text = re.sub(r'\bi\s?m\b', 'i am', text)
        text = re.sub(r'\bcant\b', 'cannot', text)
        text = re.sub(r'\bdont\b', 'do not', text)
        # Regional/Typo handling
        text = re.sub(r'\bsugar prob\w*\b', 'diabetes', text)
        text = re.sub(r'\bbp\b', 'blood pressure', text)
        text = re.sub(r'\bsugar level\b', 'glucose', text)
        text = re.sub(r'\boccour\b|\bocur\b', 'occur', text)
        text = re.sub(r'\bhappen\b', 'occur', text)
        
        # Remove punctuation but keep intent
        text = re.sub(r'[^\w\s]', '', text)
        
        # Stop word filtering (refined)
        stop_words = ["is", "are", "do", "does", "will", "can", "the", "a", "an", "i", "me", "my", "you", "your", "it", "its"]
        text = " ".join([w for w in text.split() if w not in stop_words])
        return text

    def calculate_match_score(self, msg, intent_data):
        score = 0
        words = msg.split()
        
        # Match keywords
        for kw in intent_data["keywords"]:
            if kw in msg:
                score += 1
                if kw in words: # Exact word match gets more weight
                    score += 1
        
        # Match synonyms/phrases
        for phrase, target in intent_data.get("synonyms", {}).items():
            if phrase in msg:
                score += 3
        
        # Special weight for "diabetes", "sugar", or "water" if present with other keywords
        if any(w in msg for w in ["diabetes", "sugar", "water", "glucose"]):
            score += 1
            
        return score

    async def get_response(self, user_input: str, history=None, latest_readings=None) -> str:
        msg = self.normalize_text(user_input)
        
        # 1. EMERGENCY DETECTION (Highest Priority)
        emergency_terms = ["vomit", "confus", "breath", "unconscious", "chest pain", "severe", "faint", "pass out"]
        if any(word in msg for word in emergency_terms):
            return "⚠️ **EMERGENCY NOTICE**: Based on the symptoms you've mentioned, please seek immediate medical attention or call emergency services right away. Your safety is the priority."

        # 2. RETRIEVAL (Find relevant FAQs/Knowledge for Gemini context)
        context_snippets = []
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            query_vec = self.vectorizer.transform([msg])
            similarities = cosine_similarity(query_vec, self.faq_vectors).flatten()
            
            top_indices = np.argsort(similarities)[-3:][::-1]
            for idx in top_indices:
                if similarities[idx] > 0.3:
                    context_snippets.append(f"FAQ: {self.faq_questions[idx]} - {self.faq[self.faq_questions[idx]]}")
        except:
            pass

        # 3. PREPARE GEMINI PROMPT (Memory + RAG + Personalization + Reminder Detection)
        try:
            chat_history_str = ""
            if history:
                for m in history:
                    chat_history_str += f"{m.role.capitalize()}: {m.content}\n"

            health_context = "No recent readings."
            latest_val = None
            if latest_readings:
                health_context = "Latest Glucose Readings:\n"
                for r in latest_readings:
                    health_context += f"- {r.value} mg/dL ({r.reading_type}) on {r.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
                latest_val = latest_readings[0].value

            system_prompt = f"""
            You are DiaBeat AI, a futuristic and intelligent diabetes healthcare assistant.
            
            CORE MISSION:
            1. Act as a supportive wellness tracker and medication assistant.
            2. Detect if the user wants to set a reminder (medicine, water, exercise, etc.).
            3. Provide glucose-aware guidance based on the latest readings.
            
            GLUCOSE GUIDANCE RULES:
            - If sugar > 250: Warn about dehydration, prioritize water, medication, and monitoring.
            - If sugar > 180: Encourage hydration and light movement.
            - If sugar < 70: Prioritize safety, suggest 15g fast carbs, advise rest.
            - If stable: Positively reinforce habits.
            
            REMINDER DETECTION:
            If the user asks for a reminder, acknowledge it naturally AND append the exact tag: [REMINDER_ACTION: {{"type": "...", "title": "...", "dosage": "...", "time": "HH:MM", "meal_timing": "..."}}]
            - type: MEDICINE, WATER, GLUCOSE, EXERCISE, MEAL, SLEEP, APPOINTMENT
            - time: Convert to 24h format (e.g., 8 PM -> 20:00).
            
            TONE:
            - Supportive, calm, motivating, and conversational.
            - Avoid robotic text. Instead of "Take medicine", use "It's time for your scheduled medication to support your glucose balance."
            
            USER HEALTH PROFILE:
            {health_context}
            Latest Value: {latest_val if latest_val else 'Unknown'}
            
            KNOWLEDGE BASE GUIDANCE:
            {chr(10).join(context_snippets)}
            
            CONVERSATION CONTEXT:
            {chat_history_str}
            
            USER CURRENT INPUT:
            {user_input}
            """
            
            response = self.gemini_model.generate_content(system_prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print("Gemini Error:", e)

        # 4. FALLBACK
        return "I'm DiaBeat AI. Staying consistent with your routine is key to managing diabetes. Would you like me to set a reminder for your next medication or check your latest trend?"

    def predict_readmission_risk(self, data: dict):
        if not self.model or not self.encoders:
            return {"error": "AI Model not loaded."}
        
        try:
            # Prepare features in correct order
            # features = ['age', 'time_in_hospital', 'num_lab_procedures', 'num_medications', 'number_diagnoses', 'insulin', 'change', 'diabetesMed']
            input_data = []
            
            # 1. Age (Encoded)
            age_val = data.get('age', '[40-50)')
            input_data.append(self.encoders['age'].transform([age_val])[0])
            
            # 2. Time in hospital
            input_data.append(int(data.get('time_in_hospital', 3)))
            
            # 3. Num lab procedures
            input_data.append(int(data.get('num_lab_procedures', 40)))
            
            # 4. Num medications
            input_data.append(int(data.get('num_medications', 15)))
            
            # 5. Number diagnoses
            input_data.append(int(data.get('number_diagnoses', 7)))
            
            # 6. Insulin (Encoded)
            insulin_val = data.get('insulin', 'No')
            input_data.append(self.encoders['insulin'].transform([insulin_val])[0])
            
            # 7. Change (Encoded)
            change_val = data.get('change', 'No')
            input_data.append(self.encoders['change'].transform([change_val])[0])
            
            # 8. diabetesMed (Encoded)
            med_val = data.get('diabetesMed', 'Yes')
            input_data.append(self.encoders['diabetesMed'].transform([med_val])[0])
            
            # Predict
            X = np.array(input_data).reshape(1, -1)
            prob = self.model.predict_proba(X)[0][1] # Probability of class 1 (readmitted)
            
            return {
                "risk_score": round(prob * 100, 2),
                "risk_level": "High" if prob > 0.5 else "Moderate" if prob > 0.3 else "Low",
                "message": "Based on clinical patterns, your hospital readmission risk is analyzed."
            }
        except Exception as e:
            return {"error": str(e)}

ai_service = AIService()
