# DiaBeat AI — Smart Diabetes Care Assistant (PRD)

## 1. Product Name
**DiaBeat — Intelligent Diabetes Management Chatbot**

---

## 2. Product Vision
DiaBeat is a specialized AI assistant designed to help diabetic and pre-diabetic patients manage their condition. It tracks blood glucose levels, provides personalized diet and exercise recommendations, and offers 24/7 AI-powered support for diabetes-related queries.

The goal is to simplify diabetes management through data tracking and actionable AI insights.

---

## 3. Problem Statement
Managing diabetes requires constant monitoring of glucose, careful diet planning, and regular exercise, which can be overwhelming for many patients.

Current challenges:
* Difficulty in tracking and visualizing glucose trends.
* Lack of immediate feedback on sugar levels.
* Confusion over diet and exercise choices.
* Poor adherence to monitoring routines.

DiaBeat solves these issues by providing an integrated platform for tracking and AI-driven lifestyle coaching.

---

## 4. Objectives
* Log and visualize blood glucose levels.
* Provide instant AI feedback on sugar readings.
* Suggest diabetes-friendly diets and exercises.
* Send medication and monitoring reminders.
* Offer personalized health insights based on historical data.

---

## 5. Scope

### In Scope
* Glucose level logging and history.
* AI chatbot for diabetes advice.
* Diet and exercise recommendation engine.
* User authentication and data privacy.
* Health dashboard with trend charts.
* Medicine/Monitoring reminders.

---

## 8. Core Features

### 8.1 Diabetes-Specific AI Chatbot
* Contextual advice on glucose management.
* Diet suggestions (Low GI foods, carb counting assistance).
* Exercise tips for blood sugar regulation.
* **Intelligent Feedback**: Real-time analysis of logged readings with specific advice for Very High, High, Normal, and Low ranges.
* **Personalized Nutrition**: Context-aware food suggestions based on your most recent sugar reading and the type of reading (Fasting, Before Bed, etc.).
* **Smart Hydration Guidance**: Tailored water intake recommendations to help manage glucose-related dehydration.
* **Actionable Health Coaching**: Immediate and long-term strategies for reducing blood sugar levels based on current data.
* **Emergency Treatment Protocols**: Clear, step-by-step guidance for managing critical events like hypoglycemia (15-15 Rule).

---

### 8.2 Glucose Tracking & Trends
* Log glucose readings (mg/dL or mmol/L).
* Categorize by time (Fasting, Post-meal, Before bed).
* Interactive charts showing trends over time.

---

### 8.3 Data-Driven Risk Assessment
* AI model trained on 100,000+ clinical records from 130 US hospitals.
* Estimates hospital readmission risk based on patient metrics.
* Analyzes medication impacts (Insulin, Metformin, etc.).

---

### 8.4 Clinical Knowledge Base
* Extracted knowledge from medical research (`description.pdf`).
* Provides evidence-based advice on HbA1c and clinical protocols.

---

## 11. AI Model Design (Updated)
* **Model**: Random Forest Classifier.
* **Knowledge Retrieval**: Keyword-based search from extracted clinical PDF text.
* **Data Source**: UCI Diabetes 130-US Hospitals Dataset.

---

## 17. Tech Stack
* **Frontend**: HTML5, CSS3, JavaScript (Premium Aesthetics).
* **Backend**: FastAPI (Python).
* **Database**: SQLite (Development).
* **AI/ML**: Scikit-Learn, Pandas, PyPDF.
