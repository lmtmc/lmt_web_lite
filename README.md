# lmt_web
1. Create a virtual environment: python3 -m venv env

2. Activate the virtual environment: source env/bin/activate

3. Install the required packages: pip install -r requirements.txt
Make sure the versions of FLask-SQLAlchemy and SQLAlchemy are like below.
Flask-SQLAlchemy==2.5.1
SQLAlchemy==1.4.36

4. Run the application by: python3 app.py

5. The app will be running on http://127.0.0.1:8000

6. Login using 'xia', '1234' or sign up an account

7. Choose a PID and click 'MAKE RUNS' button. If it runs on unity, it will run ./mk_run.py.

8. After choose a PID, the available runfiles will appear as the options of the "Choose a runfile:" dropdown.

9. Choose a runfile and the parameters will appear in the table below.
![image](https://user-images.githubusercontent.com/63130123/233525112-e696f968-bc3d-47ba-88e1-002ed73a7684.png)

10. Click the 'Run' button, it will excute 'sbatch_lmtoy.sh 2023-S1-US-17.run1'

11. Run via Unity will show the jobs on unity by lmthelpdesk account

Next steps:
1. Make the table editable. Save the new paremeter to the $PID.run1 

2. Get the "Make summary" function working
