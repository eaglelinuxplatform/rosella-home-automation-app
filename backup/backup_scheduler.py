from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from datetime import datetime, timedelta
import time

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Placeholder for the backup function
# def backup_function():
#     print(f"Backup function executed at {datetime.now()}")

# Function to schedule or reschedule the backup function
def schedule_backup(backup_function):
    # Job id for the backup function
    job_id = 'backup_job'

    # Cancel the existing job if it exists
    try:
        scheduler.remove_job(job_id)
        print(f"Existing job {job_id} removed")
    except JobLookupError:
        print(f"No existing job with id {job_id} found")

    # Schedule the backup function to run 10 minutes from now
    run_time = datetime.now() + timedelta(minutes=10)
    scheduler.add_job(backup_function, 'date', run_date=run_time, id=job_id)
    print(f"Backup function scheduled for {run_time}")

def main():
    # Start the scheduler
    scheduler.start()

#     try:
#         while True:
#             # Wait for user input to schedule the backup function
#             user_input = input("Press Enter to schedule the backup function or 'q' to quit: ")
#             if user_input.lower() == 'q':
#                 break
#             schedule_backup()

#             # Sleep for a short duration to prevent excessive CPU usage
#             time.sleep(1)
#     except (KeyboardInterrupt, SystemExit):
#         scheduler.shutdown()

# if __name__ == "__main__":
#     main()
