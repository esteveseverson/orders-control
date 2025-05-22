from sqlalchemy import select

from src.models.auth_model import User


def test_create_user(session):
    new_user = User(email='test@test', password='secret')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.email == 'test@test'))

    assert user.email == 'test@test'
