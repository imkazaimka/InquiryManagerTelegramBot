"""
Programmer : Shoniyozov Imronbek 

Filename : handlers/logic.py

Description : Logic shared between admin and user handlers
"""

from database.models import (
    insert_inquiry, get_inquiry, update_inquiry_answer, 
    filter_inquiries_by_status, filter_inquiries_by_workplace
)

def submit_user_inquiry(user_id, username, name, surname, phone, workplace, role, inquiry_text):
    return insert_inquiry(user_id, username, name, surname, phone, workplace, role, inquiry_text)

def answer_inquiry(inquiry_id, answer_text):
    update_inquiry_answer(inquiry_id, answer_text)

def get_inquiry_details(inquiry_id):
    return get_inquiry(inquiry_id)

def get_inquiries_by_status(status):
    return filter_inquiries_by_status(status)

def get_inquiries_by_workplace(workplace):
    return filter_inquiries_by_workplace(workplace)
