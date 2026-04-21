from app.models import db

def get_db():
    db.connect()
    try:
        yield db
    finally:
        db.close()