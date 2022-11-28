SCHEMAS = {
    'BILL': (
        (
            '!TRNS', 
            'TRNSID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME', 
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO', 
            'CLEAR', 
            'TOPRINT', 
            'ADDR5', 
            'DUEDATE', 
            'TERMS'
        ),
        (
            '!SPL', 
            'SPLID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME', 
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO', 
            'CLEAR', 
            'QNTY', 
            'REIMBEXP', 
            'SERVICEDATE', 
            'OTHER2'
        ),
        (
            '!ENDTRNS',
        )											
    ),
    'CREDIT_CARD_PURCHASE': (
        (
            '!TRNS', 
            'TRNSID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME', 
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO', 
            'CLEAR', 
            'TOPRINT', 
            'NAMEISTAXABLE', 
            'ADDR1', 
            'ADDR2', 
            'ADDR3', 
            'ADDR4', 
            'ADDR5', 
            'DUEDATE', 
            'TERMS', 
            'PAID', 
            'SHIPVIA', 
            'SHIPDATE', 
            'YEARTODATE', 
            'WAGEBASE'
        ),
        (
            '!SPL', 
            'SPLID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME',  
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO', 
            'CLEAR', 
            'QNTY', 
            'PRICE', 
            'INVITEM', 
            'PAYMETH', 
            'TAXABLE', 
            'VALADJ', 
            'REIMBEXP', 
            'SERVICEDATE', 
            'OTHER2', 
            'OTHER3', 
            'YEARTODATE', 
            'WAGEBASE'
        ),
        (
            '!ENDTRNS'
        )									
    ),
    'JOURNAL_ENTRY': (
        (
            '!TRNS', 
            'TRNSID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME', 
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO' 
        ),
        (
            '!SPL', 
            'SPLID', 
            'TRNSTYPE', 
            'DATE', 
            'ACCNT', 
            'NAME', 
            'CLASS', 
            'AMOUNT', 
            'DOCNUM', 
            'MEMO' 

        ),
        (
            '!ENDTRNS'
        )					
    )
}
