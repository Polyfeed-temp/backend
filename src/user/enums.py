# enums.py
from enum import Enum


class Role(Enum):
    Student = 'Student'
    Tutor = 'Tutor'
    CE = 'Chief Examiner'
    Admin = 'Admin'


class Faculty(Enum):
    Engineering = 'Engineering'
    IT = 'Information Technology'
    Science = 'Science'
    Business = 'Business and Economics'
    Arts = 'Arts'
    Medicine = 'Medicine, Nursing and Health Sciences'
    Pharmacy = 'Pharmacy and Pharmaceutical Sciences'
    Law = 'Law'
    Education = 'Education'
    ADA = 'Art, Design and Architecture'
