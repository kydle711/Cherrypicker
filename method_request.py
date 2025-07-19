from datetime import date, timedelta
from config import URL


class MethodRequest:
    @classmethod
    def get_request_by_range(cls, interval=1, skip_amount=0):
        end = cls._set_end()
        start = cls._set_start(time_interval=interval)
        return (f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,"
                f"EntityCompanyName&top=100&filter=ActualCompletedDate ge '{start}T00:00:00' "
                f"and ActualCompletedDate lt '{end}T00:00:00'")

    @classmethod
    def get_request_by_num(cls, num_requested):
        return f"{URL}/tables/Activity/{num_requested}"

    @classmethod
    def _set_end(cls) -> str:
        today = date.today()
        date_string = f"{today.year}-{today.month}-{today.day}"
        return date_string

    @classmethod
    def _set_start(cls, time_interval) -> str:
        end = date.today()
        delta = timedelta(days=time_interval)
        start = end - delta
        date_string = f"{start.year}-{start.month}-{start.day}"
        return date_string
