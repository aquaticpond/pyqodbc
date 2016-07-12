from lib.quickbooks.entity import Entity


class Inventory(Entity):

    qodbc_table = 'ItemInventory'
    mysql_table = 'pos_inventory'

    field_map = (
        ('ListID', 'qb_id'),
        ('ALU', 'sku'),
        ('QuantityOnCustomerOrder', 'on_customer_order'),
        ('QuantityOnHand', 'on_hand'),
        ('QuantityOnOrder', 'on_order'),
        ('QuantityOnPendingOrder', 'on_pending_order'),
        ('ReorderPoint', 'reorder_point'),
        ('IsUnorderable', 'is_unorderable'),
        ('IsBelowReorder', 'is_below_reorder'),
        ('TimeCreated', 'time_created'),
        ('TimeModified', 'time_modified')
    )

    update_fields = (
        'on_customer_order',
        'on_hand',
        'on_order',
        'on_pending_order',
        'reorder_point',
        'is_unorderable',
        'is_below_reorder',
        'time_modified'
    )

    custom_mysql_fields = ('company_file', 'product_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        product_id = self.get_surrogate_key_product_id(record)
        return (self.company_file, product_id)

    def get_surrogate_key_product_id(self, record):
        return None

    def get_last_modified(self):
        return None

    def get_latest_data_from_quickbooks(self):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table
        return self.qodbc.query(query)
