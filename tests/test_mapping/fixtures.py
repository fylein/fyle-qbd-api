fixture = {
    'credit_card_sdk': 
    [
        {
            'count': 16, 
            'data': 
            [
                {
                    "id":"bacc1DHywC3YAd",
                    "bank_name": "American Express",
                    "card_number": "55470055470",
                    "updated_at": "2023-08-28T05:46:59.330073Z",
                },
                {
                    "bank_name": "American Express",
                    "id": "baccEg1AzugNxZ",
                    "card_number": "55470077674",
                    "updated_at": "2023-08-28T05:46:59.330073Z",
                },
            ]
        }
    ],
    'post_qbd_ccc_mapping': {
        "id": 1,
        "attribute_type": "CORPORATE_CARD",
        "source_value": "AMERICAN EXPRESS - 4818",
        "source_id": "baccwOdiRCcWWQ",
        "destination_value": "Mastercard",
        "created_at": "2023-08-25T11:19:09.608035Z",
        "updated_at": "2023-08-28T10:07:30.524503Z",
        "workspace": 1
    },
    'get_qbd_ccc_mapping_state': {
        "all_attributes_count":2,
        "unmapped_attributes_count":2
    },
    'create_qbd_mapping': [
        {
            'attribute_type': 'CORPORATE_CARD',
            'value': 'American Express - 055470',
            'source_id': 'bacc1DHywC3YAd', 
        },
        {
            'attribute_type': 'CORPORATE_CARD',
            'value': 'American Express - 077674',
            'source_id': 'baccEg1AzugNxZ', 
        }
    ],
    'get_qbd_ccc_mapping': {
        "count": 2,
        "next": "http://localhost:8008/api/workspaces/1/qbd_mappings/?attribute_type=CORPORATE_CARD",
        "previous": '',
        "results": [
            {
                "id": 3,
                "attribute_type": "CORPORATE_CARD",
                "source_value": "American Express - 055470",
                "source_id": "bacc1DHywC3YAd",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.625706Z",
                "updated_at": "2023-08-28T05:46:59.326614Z",
                "workspace": 1
            },
            {
                "id": 4,
                "attribute_type": "CORPORATE_CARD",
                "source_value": "American Express - 077674",
                "source_id": "baccEg1AzugNxZ",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.627857Z",
                "updated_at": "2023-08-28T05:46:59.330073Z",
                "workspace": 1
            },
        ]
    },
    'get_all_custom_fields':[
        {
            'data': [
                {
                    "category_ids": [
                        142030,
                        142031,
                        142032,
                        142033
                    ],
                    "code": None,
                    "column_name": "text_column6",
                    "created_at": "2021-10-22T07:50:04.613487+00:00",
                    "default_value": None,
                    "field_name": "Class",
                    "id": 197380,
                    "is_custom": True,
                    "is_enabled": True,
                    "is_mandatory": False,
                    "options": [
                        "Servers",
                        "Home",
                        "Office",
                        "Hardware",
                        "Furniture",
                        "Other",
                        "Racks",
                        "Wood",
                        "Non Wood",
                        "Accessories",
                        "Miscellaneous",
                        "Merchandise",
                        "Consumer Goods",
                        "Services",
                        "Internal",
                        "R&D",
                        "Materials",
                        "Manufacturing"
                    ],
                    "org_id": "orGcBCVPijjO",
                    "placeholder": "Select Class",
                    "seq": 1,
                    "type": "SELECT",
                    "updated_at": "2023-01-01T05:35:26.345303+00:00"
                },
                {
                    "category_ids": [
                        201334,
                        201335,
                        201336,
                        201337,
                        224631,
                        224632
                    ],
                    "code": None,
                    "column_name": "text_column7",
                    "created_at": "2022-09-22T06:42:41.008885+00:00",
                    "default_value": None,
                    "field_name": "Labhvam",
                    "id": 211017,
                    "is_custom": True,
                    "is_enabled": True,
                    "is_mandatory": False,
                    "options": [],
                    "org_id": "orGcBCVPijjO",
                    "placeholder": "Select Labhvam",
                    "seq": 1,
                    "type": "SELECT",
                    "updated_at": "2023-01-01T05:35:26.345303+00:00"
                }
            ]
        }
    ]
}
