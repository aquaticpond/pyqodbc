from lib.quickbooks.entity import Entity


class SalesReceipt(Entity):

    qodbc_table = 'SalesReceipt'
    mysql_table = 'pos_sales_receipt'

    qodbc_legacy_key = 'TxnID'
    mysql_legacy_key = 'qb_id'

    field_map = (
        ('TxnID',                           'qb_id'),
        ('SalesReceiptNumber',              'sales_receipt_number'),
        ('Associate',                       'associate'),
        ('Comments',                        'comments'),
        ('CustomerListID',                  'qb_customer_id'),
        ('Discount',                        'discount'),
        ('DiscountPercent',                 'discount_percent'),
        ('ItemsCount',                      'items_count'),
        ('PromoCode',                       'promo_code'),
        ('Subtotal',                        'subtotal'),
        ('SalesReceiptType',                'sales_receipt_type'),
        ('TimeModified',                    'time_modified'),
        ('TimeCreated',                     'time_created'),
        ('BillingInformationFirstName',     'first_name'),
        ('BillingInformationLastName',      'last_name'),
        ('BillingInformationState',         'billing_state'),
        ('BillingInformationPostalCode',    'billing_postcode')

    )

    update_fields = (
        'associate',
        'comments',
        'discount',
        'discount_percent',
        'items_count',
        'promo_code',
        'subtotal',
        'sales_receipt_type',
        'time_modified',
        'first_name',
        'last_name',
        'billing_state',
        'billing_postcode'
    )

    custom_mysql_fields = ('company_file',)

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]


class SalesReceiptItem(Entity):

    qodbc_table = 'SalesReceiptItem'
    mysql_table = 'pos_sales_receipt_item'

    qodbc_legacy_key = 'TxnID'
    mysql_legacy_key = 'qb_sales_receipt_id'

    field_map = (
        ('TxnID',                           'qb_sales_receipt_id'),
        ('TimeCreated',                     'time_created'),
        ('TimeModified',                    'time_modified'),
        ('SalesReceiptItemListID',          'qb_id'),
        ('SalesReceiptItemALU',             'sku'),
        ('SalesReceiptItemDesc2',           'description'),
        ('SalesReceiptItemDiscount',        'discount'),
        ('SalesReceiptItemDiscountPercent', 'discount_percent'),
        ('SalesReceiptItemTaxAmount',       'tax'),
        ('SalesReceiptItemTaxCode',         'tax_code'),
        ('SalesReceiptItemPrice',           'price'),
        ('SalesReceiptItemQty',             'quantity'),
    )

    update_fields = (
        'time_modified',
        'discount',
        'discount_percent',
        'tax',
        'tax_code',
        'price',
        'quantity',
        'description'
    )

    custom_mysql_fields = ('company_file', 'sales_receipt_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        sales_receipt_id = self.get_surrogate_key_sales_receipt_id(record)
        return (self.company_file, sales_receipt_id)

    def get_surrogate_key_sales_receipt_id(self, record):
        pos = -1
        company_file = self.company_file
        sales_receipt_table = SalesReceipt.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'TxnID':
                qb_id = record[pos]

        qb_id = self.mysql.db.escape(qb_id)
        query = "SELECT id AS receipt_id FROM " + sales_receipt_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        result = self.mysql.query(query)

        if len(result) > 0:
            return result[0][0]

        return None

    def sync_items_custom(self):
        query = "SELECT DISTINCT `" + self.mysql_legacy_key + "` FROM `" + self.mysql_table + "` WHERE `company_file` = " + self.company_file + " AND `description` IS NULL"

        invoices = self.mysql.query(query)
        for row in invoices:
            self.sync_by_parent(row[0])

    def get_data_from_quickbooks_by_parent_id(self, qb_parent_id):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE " + self.qodbc_legacy_key + " = '" + qb_parent_id + "'"
        return self.qodbc.query(query)

    def sync_by_parent(self, qb_parent_id):
        data = self.get_data_from_quickbooks_by_parent_id(qb_parent_id)
        data = self.append_custom_data(data)
        self.write_batch(data)
