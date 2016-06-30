from lib.quickbooks.entity import Entity


class Invoice(Entity):

    qodbc_table = 'Invoice'
    mysql_table = 'invoice'

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
        'item_sales_tax'
    )

    custom_mysql_fields = ('company_file', )

    def append_custom_data(self, raw):
        return [each + (self.company_file,) for each in raw]
