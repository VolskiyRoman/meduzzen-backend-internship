from app.db.models import User


def test_create_and_delete_user(db):
    user = User(username='testuser', email='test@example.com', password='securepassword')

    db.add(user)
    db.commit()

    db.delete(user)
    db.commit()

    assert db.query(User).filter(User.username == 'testuser').first() is None