from lib.quickbooks.entity import Entity


class SalesOrder(Entity):

    qodbc_table = 'SalesOrder'
    mysql_table = 'sales_order'

    field_map = (
        ('TxnID',                           'qb_id'),
        ('TimeCreated',                     'time_created'),
        ('TimeModified',                    'time_modified'),
        ('TxnNumber',                       'txn_number'),
        ('CustomerRefListID',               'qb_customer_id'),
        ('CustomerRefFullName',             'customer_name'),
        ('ClassRefFullName',                'class'),
        ('TxnDate',                         'txn_date'),
        ('RefNumber',                       'ref_number'),
        ('PONumber',                        'po_number'),
        ('TermsRefFullName',                'terms'),
        ('DueDate',                         'due_date'),
        ('ShipDate',                        'ship_date'),
        ('Subtotal',                        'subtotal'),
        ('ItemSalesTaxRefFullName',         'item_sales_tax'),
        ('SalesTaxPercentage',              'sales_tax_percent'),
        ('SalesTaxTotal',                   'sales_tax_total'),
        ('TotalAmount',                     'total_amount'),
        ('IsManuallyClosed',                'is_manually_closed'),
        ('IsFullyInvoiced',                 'is_fully_invoiced'),
        ('Memo',                            'memo'),
        ('IsToBePrinted',                   'is_to_be_printed'),
        ('IsToBeEmailed',                   'is_to_be_emailed'),
        ('IsTaxIncluded',                   'is_tax_included'),
        ('CustomerSalesTaxCodeRefFullName', 'customer_sales_tax')
    )

    update_fields = (
        'time_modified',
        'txn_number',
        'customer_name',
        'class',
        'txn_date',
        'ref_number',
        'po_number',
        'terms',
        'due_date',
        'ship_date',
        'subtotal',
        'item_sales_tax',
        'sales_tax_percent',
        'sales_tax_total',
        'total_amount',
        'is_manually_closed',
        'is_fully_invoiced',
        'memo',
        'is_to_be_printed',
        'is_to_be_emailed',
        'is_tax_included',
        'customer_sales_tax'
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]


class SalesOrderItem(Entity):

    qodbc_table = 'SalesOrderLine'
    mysql_table = 'sales_order_item'

    field_map = (
        ('TxnID',                                   'qb_order_id'),
        ('TimeCreated',                             'time_created'),
        ('TimeModified',                            'time_modified'),
        ('SalesOrderLineTxnLineId',                 'qb_id'),
        ('SalesOrderLineItemRefListID',             'qb_product_id'),
        ('SalesOrderLineItemRefFullName',           'sku'),
        ('SalesOrderLineQuantity',                  'quantity'),
        ('SalesOrderLineRate',                      'rate'),
        ('SalesOrderLineRatePercent',               'rate_percent'),
        ('SalesOrderLineClassRefFullName',          'class'),
        ('SalesOrderLineAmount',                    'amount'),
        ('SalesOrderLineTaxAmount',                 'tax_amount'),
        ('SalesOrderLineSalesTaxCodeRefFullName',   'sales_tax_code'),
        ('SalesOrderLineTaxCodeRefFullName',        'tax_code'),
        ('SalesOrderLineInvoiced',                  'quantity_invoiced'),
        ('SalesOrderLineIsManuallyClosed',          'is_manually_closed'),
    )

    update_fields = (
        'time_modified',
        'sku',
        'quantity',
        'rate',
        'rate_percent',
        'class',
        'amount',
        'tax_amount',
        'sales_tax_code',
        'tax_code',
        'quantity_invoiced',
        'is_manually_closed',
        'qb_id'
    )

    custom_mysql_fields = ('company_file', 'order_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        order_id = self.get_surrogate_key_order_id(record)
        return (self.company_file, order_id)

    def get_surrogate_key_order_id(self, record):
        pos = -1
        company_file = self.company_file
        order_table = SalesOrder.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'TxnID':
                qb_id = record[pos]

        qb_id = self.mysql.db.escape(qb_id)
        query = "SELECT id AS order_id FROM " + order_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        result = self.mysql.query(query)

        if len(result) > 0:
            return result[0][0]

        return None

    def sync_orders_without_items(self):
        query = "SELECT `order`.`qb_id` FROM `sales_order` AS `order` " \
                "LEFT JOIN `sales_order_item` AS `item` ON (`item`.`order_id` = `order`.`id`) " \
                "WHERE `order`.`company_file` = " + self.company_file + " AND `item`.`id` IS NULL"

        orders_without_items = self.mysql.query(query)
        for row in orders_without_items:
            self.sync_items_by_order(row[0])

    def get_item_data_from_quickbooks_by_order_id(self, qb_order_id):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE TxnID = '" + qb_order_id + "'"
        return self.qodbc.query(query)

    def sync_items_by_order(self, qb_order_id):
        data = self.get_item_data_from_quickbooks_by_order_id(qb_order_id)
        data = self.append_custom_data(data)
        self.write_batch(data)


class SalesOrderLink(SalesOrderItem):

    qodbc_table = 'SalesOrderLinkedTxn'
    mysql_table = 'sales_order_link'

    field_map = (
        ('TxnID',            'qb_order_id'),
        ('LinkedTxnTxnID',   'link_qb_transaction_id'),
        ('LinkedTxnTxnType', 'link_type'),
        ('TimeCreated',      'time_created'),
        ('TimeModified',     'time_modified')
    )

    update_fields = (
        'company_file',
        'order_id',
        'link_transaction_id',
        'time_created',
        'time_modified'
    )

    custom_mysql_fields = ('company_file', 'order_id', 'link_transaction_id')

    def get_custom_data_tuple_for_record(self, record):
        order_id = self.get_surrogate_key_order_id(record)
        link_transaction_id = self.get_surrogate_key_link_transaction_id(record)
        return (self.company_file, order_id, link_transaction_id)

    # @todo: implement linked transactions
    def get_surrogate_key_link_transaction_id(self, record):
        pos = -1
        company_file = self.company_file
        order_table = SalesOrder.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'LinkedTxnTxnID':
                qb_id = record[pos]

        #qb_id = self.mysql.db.escape(qb_id)
        #query = "SELECT id AS order_id FROM " + order_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        #result = self.mysql.query(query)

        #if len(result) > 0:
        #    return result[0][0]

        return None
