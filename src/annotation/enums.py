# enums.py
from enum import Enum

class AnnotationTag(Enum):
    Strength = 'Strength'
    Weakness = 'Weakness'
    ActionItem = 'Action Item'
    Confused = 'Confused'
    Other = 'Other'

class ActionPointCategory(Enum):
    FurtherPractice = 'further practice'
    ContactTutor = 'contact tutor'
    ReferLearningResources = 'refer learning resources'
