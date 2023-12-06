# enums.py
from enum import Enum


class ActionPointCategory(Enum):
    FurtherPractice = 'Further Practice'
    ContactTutor = 'Contact Tutor'
    ReferLearningResources = 'Refer Learning Resources'
    ExploreOnline= 'Explore Online'
    Other = 'Other'
    AskClassmates = 'Ask Classmates'
