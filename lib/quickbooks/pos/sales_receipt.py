from lib.quickbooks.entity import Entity

class SalesReceipt(Entity):

    qodbc_table = 'SalesReceipt'
    mysql_table = 'pos_sales_receipt'

    field_map = (
    )

    update_fields = (
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]