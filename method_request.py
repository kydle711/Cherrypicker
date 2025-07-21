from config import URL


class MethodRequest:
    @classmethod
    def get_request_by_range(cls, start_date: str, end_date: str, skip_amount=0) -> str:
        return (f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,"
                f"EntityCompanyName&top=100&filter=ActualCompletedDate ge '{start_date}T00:00:00' "
                f"and ActualCompletedDate lt '{end_date}T00:00:00'")

    @classmethod
    def get_request_by_num(cls, num_requested: int) -> str:
        return f"{URL}/tables/Activity/{num_requested}"
