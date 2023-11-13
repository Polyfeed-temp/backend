# enums.py
from enum import Enum

class AnnotationTag(Enum):
    Strength = 'strength'
    Weakness = 'weakness'
    ActionItem = 'action item'
    Confused = 'confused'
    Other = 'other'

class ActionPointCategory(Enum):
    FurtherPractice = 'further practice'
    ContactTutor = 'contact tutor'
    ReferLearningResources = 'refer learning resources'
