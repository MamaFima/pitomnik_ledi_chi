import schedule
import time
from integrations.google_calendar import check_upcoming_appointments

def run_scheduler():
    """Запускает проверку записей в питомник каждые 5 минут."""
    schedule.every(5).minutes.do(check_upcoming_appointments)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
