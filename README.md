# lmt_web
1. Make sure lmtoy is available.
2. Create a virtual environment: python3 -m venv env
3. Activate the virtual environment: source env/bin/activate 
4. Install the required packages: pip install -r requirements.txt
   Make sure the versions of FLask-SQLAlchemy and SQLAlchemy are like below. 
   Flask-SQLAlchemy==2.5.1
   SQLAlchemy==1.4.36
5. Optional: Change the path in 'config.txt' to your work_lmt in case the program couldn't find the environment variable WORK_LMT
6. Optional: The repo includes a 'users.db'. If you want to create a new users.db or add a user, you can use the python code as follows:
  
   import users_mgt as um
  
   um.create_user_table() # create a users.db
  
   um.add_user('pid','password','email') # add a user
  
   um.show_users() # show users
  
   um.del_user() # delete a user
7. Run the application by: python3 app.py. The app will be running on http://127.0.0.1:8000
   If you run the app in a remote server, you can localforward it to your local machine by adding 'localforward 5000 127.0.0.1:8000' in .ssh/config which will set up local port forwarding from port 5000 on your local machine to port 8000 on the remote server. And then open it using a web browser using the address of http://127.0.0.1:5000. 
   If you want to change the port that the app is running on, go the bottom of "app.py" and change port='8000' to your desired number.
8. Login using pid. For example pid = 2023-S1-US-17 password = 1234
9. Click 'MAKE RUNS' button. It will run ./mk_run.py and the available runfiles will appear as the options of the "Choose a runfile:" dropdown.
10. Choose a runfile and the parameters will appear in the table below.
11. You can revise the values of the parameter and save it to a new file by input a filename and click 'SAVE' button. If you don't put a filename it will save the new data to the original file. 'ADD A ROW' and 'ADD A COLUMN' functions need more work. And if you click MAKE RUNS again, it will reset those runfiles.
12. If you choose '2023-S1-US-17.run1' and click the orange 'Run' button, it will execute 'sbatch_lmtoy.sh 2023-S1-US-17.run1'
13. Jobs running on unity container will show the jobs on unity by lmthelpdesk account and update every 10 second.
14. If there's no job running, there will be a 'Make Summary' link. For now, I just put an unreachable link there.
15. I put a 'CANCEL SELECTED JOB' button there to cancel the selected job. And it needs more work here.
