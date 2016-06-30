from lib.quickbooks.entity import Entity

class Inventory(Entity):

    qodbc_table = 'Inventory'
    mysql_table = 'pos_inventory'

    field_map = (

    )

    update_fields = (

    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]