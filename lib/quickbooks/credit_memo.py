from lib.quickbooks.entity import Entity


class CreditMemo(Entity):

    qodbc_table = 'CreditMemo'
    mysql_table = 'creditmemo'

    field_map = (
        ('TxnID',                       'qb_id'),
        ('TimeCreated',                 'time_created'),
        ('TimeModified',                'time_modified'),
        ('TxnNumber',                   'txn_number'),
        ('CustomerRefListId',           'customer_qb_id'),
        ('CustomerRefFullName',         'customer_name'),
        ('ClassRefFullName',            'class'),
        ('TxnDate',                     'txn_date'),
        ('RefNumber',                   'ref_number'),
        ('IsPending',                   'is_pending'),
        ('PONumber',                    'po_number'),
        ('TermsRefFullName',            'terms'),
        ('DueDate',                     'due_date'),
        ('ShipDate',                    'ship_date'),
        ('Subtotal',                    'subtotal'),
        ('ItemSalesTaxRefFullName',     'item_sales_tax'),
        ('SalesTaxPercentage',          'sales_tax_percentage'),
        ('SalesTaxTotal',               'sales_tax_total'),
        ('TotalAmount',                 'total_amount'),
        ('CreditRemaining',             'credit_remaining'),
        ('Memo',                        'memo'),
        ('IsToBePrinted',               'is_to_be_printed'),
        ('IsToBeEmailed',               'is_to_be_emailed'),
        ('IsTaxIncluded',               'is_tax_included'),
        ('CustomerSalesTaxCodeRefFullName', 'customer_sales_tax_code'),
    )

    update_fields = (
        'time_modified',
        'txn_number',
        'customer_qb_id',
        'customer_name',
        'class',
        'txn_date',
        'ref_number',
        'is_pending',
        'po_number',
        'terms',
        'due_date',
        'ship_date',
        'subtotal',
        'item_sales_tax',
        'sales_tax_percentage',
        'sales_tax_total',
        'total_amount',
        'credit_remaining',
        'memo',
        'is_to_be_printed',
        'is_to_be_emailed',
        'is_tax_included',
        'customer_sales_tax_code'
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]


class CreditMemoItem(Entity):

    qodbc_table = 'CreditMemoLine'
    mysql_table = 'creditmemo_item'

    field_map = (
        ('TxnID',                                   'qb_creditmemo_id'),
        ('TimeCreated',                             'time_created'),
        ('TimeModified',                            'time_modified'),
        ('CreditMemoLineTxnLineID',                 'qb_id'),
        ('CreditMemoLineItemRefListID',             'qb_product_id'),
        ('CreditMemoLineItemRefFullName',           'sku'),
        ('CreditMemoLineQuantity',                  'quantity'),
        ('CreditMemoLineRate',                      'rate'),
        ('CreditMemoLineRatePercent',               'rate_percent'),
        ('CreditMemoLineClassRefFullName',          'class'),
        ('CreditMemoLineAmount',                    'amount'),
        ('CreditMemoLineTaxAmount',                 'tax_amount'),
        ('CreditMemoLineSalesTaxCodeRefFullName',   'sales_tax_code'),
        ('CreditMemoLineTaxCodeRefFullName',        'tax_code'),
    )

    update_fields = (
        'time_modified',
        'qb_product_id',
        'sku',
        'quantity',
        'rate',
        'rate_percent',
        'class',
        'amount',
        'tax_amount',
        'sales_tax_code',
        'tax_code',
        'creditmemo_id',
    )

    custom_mysql_fields = ('company_file', 'creditmemo_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        creditmemo_id = self.get_surrogate_key_creditmemo_id(record)
        return (self.company_file, creditmemo_id)

    def get_surrogate_key_creditmemo_id(self, record):
        pos = -1
        company_file = self.company_file
        creditmemo_table = CreditMemo.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'TxnID':
                qb_id = record[pos]

        qb_id = self.mysql.db.escape(qb_id)
        query = "SELECT id AS creditmemo_id FROM " + creditmemo_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        result = self.mysql.query(query)

        if len(result) > 0:
            return result[0][0]

        return None


class CreditMemoLink(CreditMemoItem):

    qodbc_table = 'CreditMemoLinkedTxn'
    mysql_table = 'creditmemo_link'

    field_map = (
        ('TxnID',            'qb_creditmemo_id'),
        ('LinkedTxnTxnID',   'link_qb_transaction_id'),
        ('LinkedTxnTxnType', 'link_type')
    )

    update_fields = (
        'company_file',
        'creditmemo_id',
        'link_transaction_id'
    )


    custom_mysql_fields = ('company_file', 'creditmemo_id', 'link_transaction_id')

    def get_custom_data_tuple_for_record(self, record):
        invoice_id = self.get_surrogate_key_creditmemo_id(record)
        link_transaction_id = self.get_surrogate_key_link_transaction_id(record)
        return (self.company_file, invoice_id, link_transaction_id)

    # @todo: implement linked transactions
    def get_surrogate_key_link_transaction_id(self, record):
        pos = -1
        company_file = self.company_file
        creditmemo_table = CreditMemo.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'LinkedTxnTxnID':
                qb_id = record[pos]

        #qb_id = self.mysql.db.escape(qb_id)
        #query = "SELECT id AS creditmemo_id FROM " + creditmemo_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        #result = self.mysql.query(query)

        #if len(result) > 0:
        #    return result[0][0]

        return None