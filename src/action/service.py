from sqlalchemy.orm import Session
from .models import Highlight
from .schemas import HighlightPydantic, DomMeta, FeedbackHighlightPydantic
import json

localDatabase = []


def get_highlights_by_url(db: Session, url: str):
    db_highlights = db.query(Highlight).filter(Highlight.url == url).all()
    if db_highlights:
        for db_highlight in db_highlights:
            db_highlight.start_meta = DomMeta(**json.loads(db_highlight.start_meta))
            db_highlight.end_meta = DomMeta(**json.loads(db_highlight.end_meta))
    return db_highlights


def create_highlight(db: Session, highlight_data: FeedbackHighlightPydantic):
    print(highlight_data)
    start_meta = (highlight_data.annotation.startMeta.model_dump_json())
    end_meta = highlight_data.annotation.endMeta.model_dump_json()
    db_highlight = Highlight(id=str(highlight_data.id), url=str(highlight_data.url), startMeta=start_meta,
                             endMeta=end_meta, text=highlight_data.text, annotation_tag=highlight_data.annotation_tag,
                             notes=highlight_data.notes)

    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return highlight_data


def get_highlights(db: Session):
    return db.query(Highlight).all()


def get_highlight_tags(db: Session):
    return db.query(Highlight.annotation_tag).distinct().all()
