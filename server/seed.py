from faker import Faker

from app import app
from config import db
from models import User, Note

fake = Faker()

with app.app_context():
    print("Clearing db...")
    Note.query.delete()
    User.query.delete()

    print("Seeding users...")
    users = []
    for _ in range(5):
        user = User(username=fake.unique.user_name())
        user.password_hash = "password123"
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    print("Seeding notes...")
    notes = []
    for user in users:
        for _ in range(3):
            notes.append(Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(nb_sentences=3),
                user_id=user.id,
            ))
    db.session.add_all(notes)
    db.session.commit()

    print("Done seeding!")