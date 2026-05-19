from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Time
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    symptoms = relationship("Symptom", back_populates="owner")
    medicines = relationship("Reminder", back_populates="owner")
    appointments = relationship("Appointment", back_populates="owner")
    glucose_readings = relationship("GlucoseReading", back_populates="owner")
    chat_history = relationship("ChatMessage", back_populates=None)

class GlucoseReading(Base):
    __tablename__ = "glucose_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    value = Column(Integer) # mg/dL
    reading_type = Column(String) # Fasting, Post-meal, Random
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="glucose_readings")

class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symptoms_text = Column(Text)
    prediction = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="symptoms")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_type = Column(String) # MEDICINE, WATER, GLUCOSE, EXERCISE, MEAL, SLEEP, APPOINTMENT
    title = Column(String) # Medicine name or task
    dosage = Column(String, nullable=True)
    reminder_time = Column(Time)
    frequency = Column(String, default="Daily")
    meal_timing = Column(String, default="None") # Before Meal, After Meal, None
    status = Column(String, default="Upcoming") # Upcoming, Completed, Missed, Delayed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="medicines")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doctor_name = Column(String)
    appointment_time = Column(DateTime)
    status = Column(String, default="Scheduled")

    owner = relationship("User", back_populates="appointments")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
