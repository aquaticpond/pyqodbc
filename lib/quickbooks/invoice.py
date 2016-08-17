from lib.quickbooks.entity import Entity


class Invoice(Entity):

    qodbc_table = 'Invoice'
    mysql_table = 'invoice'

    mysql_legacy_key = 'qb_id'
    qodbc_legacy_key = 'TxnID'

    field_map = (
        ('TxnID',                'qb_id'),
        ('TimeCreated',          'time_created'),
        ('TimeModified',         'time_modified'),
        ('EditSequence',         'edit_sequence'),
        ('TxnNumber',            'txn_number'),
        ('CustomerRefListID',    'customer_qb_id'),
        ('CustomerRefFullName',  'customer_name'),
        ('ClassRefFullName',     'class'),
        ('TxnDate',              'txn_date'),
        ('RefNumber',            'ref_number'),
        ('IsPending',            'is_pending'),
        ('IsFinanceCharge',      'is_finance_charge'),
        ('PONumber',             'po_number'),
        ('TermsRefFullName',     'terms'),
        ('DueDate',              'due_date'),
        ('ShipDate',             'ship_date'),
        ('Subtotal',             'subtotal'),
        ('SalesTaxPercentage',   'sales_tax_percentage'),
        ('SalesTaxTotal',        'sales_tax_total'),
        ('AppliedAmount',        'applied_amount'),
        ('BalanceRemaining',     'balance_remaining'),
        ('IsPaid',               'is_paid'),
        ('IsToBePrinted',        'is_to_be_printed'),
        ('IsToBeEmailed',        'is_to_be_emailed'),
        ('IsTaxIncluded',        'is_tax_included'),
        ('ItemSalesTaxRefFullName', 'item_sales_tax'),
        ('BillAddressAddr1',     'billing_street1'),
        ('BillAddressAddr2',     'billing_street2'),
        ('BillAddressCity',      'billing_city'),
        ('BillAddressState',     'billing_state'),
        ('BillAddressPostalCode', 'billing_postcode'),
        ('BillAddressCountry',   'billing_country'),
        ('ShipAddressAddr1',     'shipping_street1'),
        ('ShipAddressAddr2',     'shipping_street2'),
        ('ShipAddressCity',      'shipping_city'),
        ('ShipAddressState',     'shipping_state'),
        ('ShipAddressPostalCode', 'shipping_postcode'),
        ('ShipAddressCountry',   'shipping_country')
    )

    update_fields = (
        'time_modified',
        'edit_sequence',
        'txn_number',
        'customer_qb_id',
        'customer_name',
        'class',
        'txn_date',
        'ref_number',
        'is_pending',
        'is_finance_charge',
        'po_number',
        'terms',
        'due_date',
        'ship_date',
        'subtotal',
        'sales_tax_percentage',
        'sales_tax_total',
        'applied_amount',
        'balance_remaining',
        'is_paid',
        'is_to_be_printed',
        'is_to_be_emailed',
        'is_tax_included',
        'item_sales_tax',
        'billing_street1',
        'billing_street2',
        'billing_city',
        'billing_state',
        'billing_postcode',
        'billing_country',
        'shipping_street1',
        'shipping_street2',
        'shipping_city',
        'shipping_state',
        'shipping_postcode',
        'shipping_country'
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]


class InvoiceItem(Entity):

    qodbc_table = 'InvoiceLine'
    mysql_table = 'invoice_item'

    mysql_legacy_key = 'qb_invoice_id'
    qodbc_legacy_key = 'TxnID'

    field_map = (
        ('InvoiceLineTxnLineID',        'qb_id'),
        ('TxnID',                       'qb_invoice_id'),
        ('InvoiceLineItemRefListID',    'qb_product_id'),
        ('TimeCreated',                 'time_created'),
        ('TimeModified',                'time_modified'),
        ('InvoiceLineItemRefFullName',  'sku'),
        ('InvoiceLineQuantity',         'quantity'),
        ('InvoiceLineRate',             'rate'),
        ('InvoiceLineAmount',           'amount'),
        ('InvoiceLineClassRefFullName', 'class')
    )

    update_fields = (
        'invoice_id',
        'time_modified',
        'qb_product_id',
        'sku',
        'quantity',
        'rate',
        'amount',
        'class'
    )

    custom_mysql_fields = ('company_file', 'invoice_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        invoice_id = self.get_surrogate_key_invoice_id(record)
        return (self.company_file, invoice_id)

    def get_surrogate_key_invoice_id(self, record):
        pos = -1
        company_file = self.company_file
        invoice_table = Invoice.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'TxnID':
                qb_id = record[pos]

        qb_id = self.mysql.db.escape(qb_id)
        query = "SELECT id AS invoice_id FROM " + invoice_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        result = self.mysql.query(query)

        if len(result) > 0:
            return result[0][0]

        return None

    def sync_invoices_without_items(self):
        ignore_list = "', '".join(self.ignore_list)
        query = "SELECT `invoice`.`qb_id` FROM `invoice` " \
                "LEFT JOIN `invoice_item` AS `item` ON (`item`.`invoice_id` = `invoice`.`id`) " \
                "WHERE `invoice`.`company_file` = " + self.company_file + " AND `invoice`.`qb_id` NOT IN ('" + ignore_list + "') " \
                "AND `item`.`id` IS NULL"

        invoices_without_items = self.mysql.query(query)
        for row in invoices_without_items:
            self.sync_items_by_invoice(row[0])

    def get_item_data_from_quickbooks_by_invoice_id(self, qb_invoice_id):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE TxnID = '" + qb_invoice_id + "'"
        return self.qodbc.query(query)

    def sync_items_by_invoice(self, qb_invoice_id):
        data = self.get_item_data_from_quickbooks_by_invoice_id(qb_invoice_id)
        data = self.append_custom_data(data)
        self.write_batch(data)


class InvoiceLink(InvoiceItem):

    qodbc_table = 'InvoiceLinkedTxn'
    mysql_table = 'invoice_link'

    field_map = (
        ('TxnID',            'qb_invoice_id'),
        ('LinkedTxnTxnID',   'link_qb_transaction_id'),
        ('LinkedTxnTxnType', 'link_type'),
        ('TimeCreated',      'time_created'),
        ('TimeModified',     'time_modified')
    )

    update_fields = (
        'company_file',
        'invoice_id',
        'link_transaction_id',
        'time_created',
        'time_modified'
    )

    custom_mysql_fields = ('company_file', 'invoice_id', 'link_transaction_id')

    def get_custom_data_tuple_for_record(self, record):
        invoice_id = self.get_surrogate_key_invoice_id(record)
        link_transaction_id = self.get_surrogate_key_link_transaction_id(record)
        return (self.company_file, invoice_id, link_transaction_id)

    # @todo: implement linked transactions
    def get_surrogate_key_link_transaction_id(self, record):
        pos = -1
        company_file = self.company_file
        invoice_table = Invoice.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'LinkedTxnTxnID':
                qb_id = record[pos]

        #qb_id = self.mysql.db.escape(qb_id)
        #query = "SELECT id AS invoice_id FROM " + invoice_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        #result = self.mysql.query(query)

        #if len(result) > 0:
        #    return result[0][0]

        return None
