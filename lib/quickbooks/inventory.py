from lib.quickbooks.entity import Entity
from time import gmtime, strftime

class Inventory(Entity):

    qodbc_table = 'ItemInventory'
    mysql_table = 'inventory'

    field_map = (
        ('Name', 'sku'),
        ('SalesDesc', 'description'),
        ('SalesTaxCodeRefFullName', 'sales_tax_code'),
        ('SalesPrice', 'sales_price'),
        ('CustomFieldRetailPrice', 'retail_price'),
        ('PurchaseCost', 'purchase_cost'),
        ('ReorderPoint', 'reorder_point'),
        ('QuantityOnHand', 'quantity_on_hand'),
        ('QuantityOnOrder', 'quantity_on_order'),
        ('QuantityOnSalesOrder', 'quantity_on_sales_order'),
        ('IsActive', 'is_active'),

    )

    update_fields = (
        'sku',
        'description',
        'is_active',
        'sales_tax_code',
        'sales_price',
        'retail_price',
        'purchase_cost',
        'reorder_point',
        'quantity_on_hand',
        'quantity_on_order',
        'quantity_on_sales_order',
        'time_updated'
    )

    custom_mysql_fields = ('company_file', 'time_updated')

    def append_custom_data(self, raw):
        return [each + (self.company_file, self.get_now_datetime()) for each in raw]

    def get_now_datetime(self):
        return strftime("%Y-%m-%d %H:%M:%S", gmtime())

    def get_latest_data_from_quickbooks(self):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table
        return self.qodbc.query(query)

    def get_last_modified(self):
        return '0000-00-00 00:00:00'