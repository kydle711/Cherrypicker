from app_config import URL


class MethodRequest:
    """ Generates URLs for the various types of requests needed"""
    @classmethod
    def get_base_url(cls) -> str:
        return f"{URL}/tables/Activity"

    @classmethod
    def get_request_by_range(cls, start_date: str, end_date: str, skip_amount=0) -> str:
        return (f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,"
                f"EntityCompanyName&top=100&filter=ActualCompletedDate ge '{start_date}T00:00:00' "
                f"and ActualCompletedDate lt '{end_date}T00:00:00'")

    @classmethod
    def get_request_by_num(cls, num_requested: int) -> str:
        return f"{URL}/tables/Activity/{num_requested}"

    @classmethod
<<<<<<< HEAD
    def get_job_items(cls, work_order_num: int) -> str:
        return (f"{URL}/tables/ActivityJobItems?top=100&select=ActivityNo,Item,IsRestocked,RestockTo,"
                f"ItemDescription,Qty&filter=ActivityNo eq '{work_order_num}'")

    @classmethod
    def get_customer_pm_report(cls, customer_name: str, start_date: str | None, end_date: str | None, filter_type=None, skip_amount=0) -> str:
        if start_date:
            start_date_filter = f"ActualCompletedDate ge '{start_date}T00:00:00'"
=======
    def get_job_items(cls) -> str:
        return f"{URL}/tables/ActivityJobItems"

    @classmethod
    def get_job_items_params(cls, work_order_num: int) -> dict:
        return {"skip": 0,
                "top": 100,
                "select": "ActivityNo,Item,IsRestocked,RestockTo,ItemDescription,Qty",
                "filter": f"ActivityNo eq '{work_order_num}'"}

    @classmethod
    def get_pm_report_params(cls, start_date: str=None, end_date: str=None,
                             filter_type: str=None, customer: str=None) -> dict:
        if start_date and end_date:
            date_filter = (f"ActualCompletedDate ge '{start_date}T00:00:00' and "
                           f"ActualCompletedDate lt '{end_date}T00:00:00'")
>>>>>>> 8ebbc3e (Debugged GUI PM Audit functions)
        else:
            start_date_filter = ''

        if end_date:
            end_date_filter = f" ActualCompletedDate lt '{end_date}T00:00:00'"
        else:
            end_date_filter = ''

        if filter_type:
<<<<<<< HEAD
            wo_type = f" Comments eq '{filter_type}'"
        else:
            wo_type = ''
        request_url = f"{URL}/tables/Activity?skip={skip_amount}&select=RecordID,Comments,EntityCompanyName&top=100&filter="\
                      f"{start_date_filter} and{end_date_filter} and EntityCompanyName eq '{customer_name}' and{wo_type}"
        print(request_url)
        return
=======
            wo_type = f" and contains(Comments, '{filter_type}')"
        else:
            wo_type = ''
        if customer:
            customer_name_filter = f" and EntityCompanyName eq '{customer}'"
        else:
            customer_name_filter = ''

        activity_filter = " and ActivityType eq 'Work Order'"

        filter_string = f"{date_filter}{activity_filter}{customer_name_filter}{wo_type}"
        return {"skip": 0,
                "top": 100,
                "select": "RecordID,Comments,EntityCompanyName,SignatureURL",
                "filter": filter_string}
>>>>>>> 8ebbc3e (Debugged GUI PM Audit functions)

    @classmethod
    def get_customer_names(cls, skip_amount=0) -> str:
        return f"{URL}/tables/Entity?skip={skip_amount}&top=100&select=CompanyName&filter=EntityType eq 'customer'"

    #TODO: increment skip param if request returns a count of less than 100
    @staticmethod
    def increment_skip(request_string: str) -> str:
        pass
