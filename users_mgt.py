from server import server, db, User, Job
from datetime import datetime
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
# from werkzeug.security import generate_password_hash
#
# password = '1234'
# hashed_password = generate_password_hash(password, method='sha256')
# user = User(username='2023-S1-US-17', password=hashed_password, email='test@test.com')
# db.session.add(user)
# db.session.commit()
#
# new_job = Job(title='runfile', description='session_path', username='current_user.username')

# user=User.query.filter_by(username='2023-S1-US-17').first()
# db.session.delete(user)  # Mark the user for deletion
# db.session.commit()  # Commit the changes to the database

# from sqlalchemy import Column, Integer, String, Text, ForeignKey
# from sqlalchemy.orm import relationship
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_sqlalchemy import SQLAlchemy
# from config import engine
#
# db = SQLAlchemy()
#
#
# def create_user_table():
#     db.create_all(engine)
#
#
# class User(db.Model):
#     id = Column(Integer, primary_key=True)
#     username = Column(String(15), unique=True, nullable=False)
#     email = Column(String(50), unique=True, nullable=False)
#     password = Column(String(80), nullable=False)
#     jobs = relationship('Job', backref="user", lazy=True)
#
#     def set_password(self, password):
#         self.password = generate_password_hash(password, method='sha256')
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
#
#
# class Job(db.Model):
#     id = Column(Integer, primary_key=True)
#     job_title = Column(String(100), nullable=False)
#     job_content = Column(Text)
#     user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
#
#
# def create_user(username, email, password):
#     user = User(username=username, email=email)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()
#
#
# def delete_user(username):
#     user = User.query.filter_by(username=username).first()
#     if user:
#         db.session.delete(user)
#         db.session.commit()
#
#
# def get_all_users():
#     users = User.query.all()
#     return users
#
#
# def add_job(job_title, job_content, username):
#     user = User.query.filter_by(username=username).first()
#     if user:
#         job = Job(job_title=job_title, job_content=job_content, user=user)
#         db.session.add(job)
#         db.session.commit()
#     else:
#         raise ValueError("User not found.")
#
#
# def get_user_jobs(username):
#     user = User.query.filter_by(username=username).first()
#     if user:
#         jobs = user.jobs
#         return jobs
#     else:
#         raise ValueError("User not found.")
#
#
# def delete_job(username, job_title):
#     user = User.query.filter_by(username=username).first()
#     if user:
#         job = Job.query.filter_by(user=user, job_title=job_title).first()
#         if job:
#             db.session.delete(job)
#             db.session.commit()
#         else:
#             raise ValueError("Job not found.")
#     else:
#         raise ValueError("User not found.")

# from sqlalchemy import Table
# from sqlalchemy.sql import select
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash
# from config import engine
#
# db = SQLAlchemy()
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(15), unique=True)
#     email = db.Column(db.String(50), unique=True)
#     password = db.Column(db.String(80))
#     jobs = db.relationship('Job', backref="user", lazy=True)
#
#
# class Job(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     job_title = db.Column(db.String(100), nullable=False)
#     job_content = db.Column(db.Text)
#     username = db.Column(db.Integer, db.ForeignKey("user.username"), nullable=False)
#
#
# User_tbl = Table('user', User.metadata)
# Job_tbl = Table('job', Job.metadata)
#
#
# def create_user_table():
#     User.metadata.create_all(engine)
#     # db.create_all()
#
#
# def add_user(username, password, email):
#     hashed_password = generate_password_hash(password, method='sha256')
#
#     ins = User_tbl.insert().values(
#         username=username, email=email, password=hashed_password)
#
#     conn = engine.connect()
#     conn.execute(ins)
#     conn.close()
#
#
# def del_user(username):
#     delete = User_tbl.delete().where(User_tbl.c.username == username)
#
#     conn = engine.connect()
#     conn.execute(delete)
#     conn.close()
#
#
# def show_users():
#     select_st = select([User_tbl.c.username, User_tbl.c.email])
#
#     conn = engine.connect()
#     rs = conn.execute(select_st)
#
#     for row in rs:
#         print(row)
#
#     conn.close()
#
#
# def add_job(job_title, job_content, username):
#     ins = Job_tbl.insert().values(
#         job_title=job_title, job_content=job_content, username=username)
#
#     conn = engine.connect()
#     conn.execute(ins)
#     conn.close()
#
#
# def show_jobs(username):
#     select_st = select([Job_tbl.c.job_title, Job_tbl.c.job_content]).where(Job_tbl.c.username == username)
#     conn = engine.connect()
#     rs = conn.execute(select_st)
#
#     for row in rs:
#         print(row)
#
#     conn.close()
#
#
# def del_jobs(username, job):
#     delete = User_tbl.delete().where(User_tbl.c.username == username)
#
#     conn = engine.connect()
#     conn.execute(delete)
#     conn.close()
