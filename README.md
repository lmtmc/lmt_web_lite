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
   
   If you run the app in a remote server, you can local forward it to your local machine by adding 'localforward 5000 127.0.0.1:8000' in .ssh/config which will set up local port forwarding from port 5000 on your local machine to port 8000 on the remote server. And then open it using a web browser using the address of http://127.0.0.1:5000. 
   
    If you want to change the port that the app is running on, go the bottom of "app.py" and change port='8000' to your desired number:
   
![image](https://github.com/lmtmc/lmt_web/assets/63130123/0d5d3ac4-2fa9-47c9-af32-cb7f9a1e0262)


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
