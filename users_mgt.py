from my_server import server, db, User, Job
from datetime import datetime

# add user
with server.app_context():
    db.create_all()
    new_user = User(username='2023-S1-US-17', password='1234', email='test@test.com')
    new_user1 = User(username='2023-S1-US-18', password='1234', email='test1@test.com')
    new_job = Job(title='test1', session='test for 17', create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  username='2023-S1-US-17')
    db.session.add(new_user)
    db.session.add(new_user1)
    db.session.add(new_job)
    db.session.commit()
# delete user
with server.app_context():
    user_to_delete = User.query.filter_by(username='2023-S1-US-17').first()
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
