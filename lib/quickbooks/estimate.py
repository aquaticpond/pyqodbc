from lib.quickbooks.entity import Entity


class Estimate(Entity):

    qodbc_table = 'Estimate'
    mysql_table = 'estimate'

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
        ('IsActive',                        'is_active'),
        ('CreateChangeOrder',               'create_change_order'),
        ('PONumber',                        'po_number'),
        ('TermsRefFullName',                'terms'),
        ('DueDate',                         'due_date'),
        ('Subtotal',                        'subtotal'),
        ('ItemSalesTaxRefFullName',         'item_sales_tax'),
        ('SalesTaxPercentage',              'sales_tax_percent'),
        ('SalesTaxTotal',                   'sales_tax_total'),
        ('TotalAmount',                     'total_amount'),
        ('Memo',                            'memo'),
        ('IsToBeEmailed',                   'is_to_be_emailed'),
        ('IsTaxIncluded',                   'is_tax_included'),
        ('CustomerSalesTaxCodeRefFullName', 'customer_sales_tax_code')

    )

    update_fields = (
        'time_modified',
        'txn_number',
        'qb_customer_id',
        'customer_name',
        'class',
        'txn_date',
        'ref_number',
        'is_active',
        'create_change_order',
        'po_number',
        'terms',
        'due_date',
        'subtotal',
        'item_sales_tax',
        'sales_tax_percent',
        'sales_tax_total',
        'total_amount',
        'memo',
        'is_to_be_emailed',
        'is_tax_included',
        'customer_sales_tax_code'
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]


class EstimateItem(Entity):

    qodbc_table = 'EstimateLine'
    mysql_table = 'estimate_item'

    field_map = (
        ('TxnID',                                   'qb_estimate_id'),
        ('TimeCreated',                             'time_created'),
        ('TimeModified',                            'time_modified'),
        ('EstimateLineTxnLineID',                   'qb_id'),
        ('EstimateLineItemRefListID',               'qb_product_id'),
        ('EstimateLineItemRefFullName',             'sku'),
        ('EstimateLineQuantity',                    'quantity'),
        ('EstimateLineRate',                        'rate'),
        ('EstimateLineRatePercent',                 'rate_percent'),
        ('EstimateLineClassRefFullName',            'class'),
        ('EstimateLineAmount',                      'amount'),
        ('EstimateLineTaxAmount',                   'tax_amount'),
        ('EstimateLineSalesTaxCodeRefFullName',     'sales_tax_code'),
        ('EstimateLineTaxCodeRefFullName',          'tax_code'),
        ('EstimateLineMarkupRate',                  'markup_rate'),
        ('EstimateLIneMarkupRatePercent',           'markup_rate_percent')

    )

    update_fields = (
        'time_modified',
        'qb_id',
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
        'markup_rate',
        'markup_rate_percent'
    )

    custom_mysql_fields = ('company_file', 'estimate_id')

    def append_custom_data(self, raw):
        return [each + self.get_custom_data_tuple_for_record(each) for each in raw]

    def get_custom_data_tuple_for_record(self, record):
        estimate_id = self.get_surrogate_key_estimate_id(record)
        return (self.company_file, estimate_id)

    def get_surrogate_key_estimate_id(self, record):
        pos = -1
        company_file = self.company_file
        estimate_table = Estimate.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'TxnID':
                qb_id = record[pos]

        qb_id = self.mysql.db.escape(qb_id)
        query = "SELECT id AS estimate_id FROM " + estimate_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        result = self.mysql.query(query)

        if len(result) > 0:
            return result[0][0]

        return None



class EstimateLink(EstimateItem):

    qodbc_table = 'EstimateLinkedTxn'
    mysql_table = 'estimate_link'

    field_map = (
        ('TxnID',            'qb_estimate_id'),
        ('LinkedTxnTxnID',   'link_qb_transaction_id'),
        ('LinkedTxnTxnType', 'link_type'),
        ('TimeCreated',      'time_created'),
        ('TimeModified',     'time_modified')
    )

    update_fields = (
        'company_file',
        'estimate_id',
        'link_transaction_id',
        'time_created',
        'time_modified'
    )

    custom_mysql_fields = ('company_file', 'estimate_id', 'link_transaction_id')

    def get_custom_data_tuple_for_record(self, record):
        estimate_id = self.get_surrogate_key_estimate_id(record)
        link_transaction_id = self.get_surrogate_key_link_transaction_id(record)
        return (self.company_file, estimate_id, link_transaction_id)

    # @todo: implement linked transactions
    def get_surrogate_key_link_transaction_id(self, record):
        pos = -1
        company_file = self.company_file
        estimate_table = Estimate.mysql_table
        qb_id = None

        for field in self.field_map:
            pos += 1
            if field[0] == 'LinkedTxnTxnID':
                qb_id = record[pos]

        #qb_id = self.mysql.db.escape(qb_id)
        #query = "SELECT id AS estimate_id FROM " + estimate_table + " WHERE company_file=" + company_file + " AND qb_id=" + qb_id
        #result = self.mysql.query(query)

        #if len(result) > 0:
        #    return result[0][0]

        return None
