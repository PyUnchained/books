from books.models.config import AccountSettings

class FinancialStatement():
    def __init__(self,system_account, *args, **kwargs):
        self.system_account = system_account