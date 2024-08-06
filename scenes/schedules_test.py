from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger


def has_common_element(list1, list2):
    return bool(set(list1) & set(list2))

def create_scheduled_job(job_func,args, day_of_week, hour, minute, second,scheduler, job_id,date=None):
    # Create a new BackgroundScheduler instance if jobstores, executors, or job_defaults are not provided
    
    day_list = ['mon','tue','wed','thu','fri','sat','sun']

    # Create a cron trigger for each selected day of the week
    # if has_common_element(day_of_week,day_list): 
    for day in day_of_week:

        if day == "once":
            print("once job")
            date_time = f'{date} {hour}:{minute}:{second}'
            print(date_time)
            scheduler.add_job(
                job_func,
                args=args,
                trigger=DateTrigger(run_date= date_time),
                id=f"{job_id}_once"  # Append the day to the job ID for uniqueness

            )
        else:
            print("days_job")
            scheduler.add_job(
                job_func,
                args=args,
                trigger=CronTrigger(day_of_week=day, hour=hour, minute=minute, second=second),
                id=f"{job_id}_{day}",  # Append the day to the job ID for uniqueness



            )


def delete_scheduled_job(job_id, scheduler):
    day_list = ['mon','tue','wed','thu','fri','sat','sun','once']
    for day in day_list:
 
        job = scheduler.get_job(f"{job_id}_{day}")
        
        if job:
            scheduler.remove_job(f"{job_id}_{day}")
            print(f"Job with ID '{job_id}_{day}' has been deleted.")
        else:
            print(f"Job with ID '{job_id}_{day}' not found.")
        



