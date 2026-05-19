from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, time

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class SymptomBase(BaseModel):
    symptoms_text: str

class SymptomCreate(SymptomBase):
    pass

class Symptom(SymptomBase):
    id: int
    user_id: int
    prediction: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    reminder_type: str
    title: str
    dosage: Optional[str] = None
    reminder_time: time
    frequency: Optional[str] = "Daily"
    meal_timing: Optional[str] = "None"
    status: Optional[str] = "Upcoming"

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    status: str

class Reminder(ReminderBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    doctor_name: str
    appointment_time: datetime

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True

class GlucoseReadingBase(BaseModel):
    value: int
    reading_type: str

class GlucoseReadingCreate(GlucoseReadingBase):
    pass

class GlucoseReading(GlucoseReadingBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RiskData(BaseModel):
    age: str
    time_in_hospital: int
    num_lab_procedures: int
    num_medications: int
    number_diagnoses: int
    insulin: str
    change: str
    diabetesMed: str
