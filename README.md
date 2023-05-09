# lmt_web
1. Make sure lmtoy is available.

2. Create a virtual environment: python3 -m venv env

3. Activate the virtual environment: source env/bin/activate

4. Install the required packages: pip install -r requirements.txt

  Make sure the versions of FLask-SQLAlchemy and SQLAlchemy are like below.

  Flask-SQLAlchemy==2.5.1
  
  SQLAlchemy==1.4.36

5. Change the path in 'config.txt' to your work_lmt

6. Create a users.db or add a user using the python code as follows:
  
  import users_mgt as um
  
  um.create_user_table() # create a users.db
  
  um.add_user('pid','password','email') # add a user
  
  um.show_users() # show users
  
  um.del_user() # delete a user
  
8. Run the application by: python3 app.py

7. The app will be running on http://127.0.0.1:8000

8. Login using pid. For example pid = 2023-S1-US-17 password = 1234

9. Choose a PID and click 'MAKE RUNS' button. If it runs on unity, it will run ./mk_run.py.

10. After choose a PID, the available runfiles will appear as the options of the "Choose a runfile:" dropdown.

11. Choose a runfile and the parameters will appear in the table below.
![image](https://user-images.githubusercontent.com/63130123/233525112-e696f968-bc3d-47ba-88e1-002ed73a7684.png)

12. Click the 'Run' button, it will excute 'sbatch_lmtoy.sh 2023-S1-US-17.run1'

13. Run via Unity tab content will show the jobs on unity by lmthelpdesk account

Next steps:
1. Make the table editable. Save the new paremeter to the $PID.run1 

2. Get the "Make summary" function working
