import re
from app_config import URL


class MethodRequest:
    """ Generates URLs for the various types of requests needed"""
    @classmethod
    def get_request_by_range(cls, start_date: str, end_date: str, skip_amount=0) -> str:
        return (f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,"
                f"EntityCompanyName&top=100&filter=ActualCompletedDate ge '{start_date}T00:00:00' "
                f"and ActualCompletedDate lt '{end_date}T00:00:00'")

    @classmethod
    def get_request_by_num(cls, num_requested: int) -> str:
        return f"{URL}/tables/Activity/{num_requested}"

    @classmethod
    def get_job_items(cls, work_order_num: int) -> str:
        return (f"{URL}/tables/ActivityJobItems?top=100&select=ActivityNo,Item,IsRestocked,RestockTo,"
                f"ItemDescription,Qty&filter=ActivityNo eq '{work_order_num}'")

    @classmethod
    def get_customer_pm_report(cls, start_date: str | None, end_date: str | None, customer_name: str, wo_filter=None, skip_amount=0) -> str:
        if start_date:
            start_date_filter = f" ActualCompletedDate ge '{start_date}T00:00:00'"
        else:
            start_date_filter = ''

        if end_date:
            end_date_filter = f" ActualCompletedDate lt '{end_date}T00:00:00'"
        else:
            end_date_filter = ''

        if filter:
            wo_type = f" Comments eq '{filter}'"
        else:
            wo_type = ''

        return (f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,EntityCompanyName&top=100&filter="
                f"EntityCompanyName eq '{customer_name}'{start_date_filter}{end_date_filter}{wo_type}")

    @classmethod
    def get_customer_names(cls, skip_amount=0) -> str:
        return f"{URL}/tables/Entity?skip={skip_amount}&top=100&select=CompanyName&filter=EntityType eq 'customer'"

    #TODO: increment skip param if request returns a count of less than 100
    @staticmethod
    def increment_skip(request_string: str) -> str:
        pass
