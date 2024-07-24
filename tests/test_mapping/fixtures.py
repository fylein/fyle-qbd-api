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
    'project_list': 
    [
        {
            'count': 2, 
            'data': 
            [
                {
					"attribute_type": "PROJECT",
					"source_value": "Aaron",
					"source_id": "1234"
                },
                {
					"attribute_type": "PROJECT",
					"source_value": "Abbott",
					"source_id": "5678"
                },
            ]
        }
    ],
    'cost_center_list': 
    [
        {
            'count': 2, 
            'data': 
            [
                {
					"attribute_type": "COST_CENTER",
					"source_value": "Administration",
					"source_id": "1234"
                },
                {
					"attribute_type": "COST_CENTER",
					"source_value": "Analytics",
					"source_id": "5678"
                },
            ]
        }
    ],
    'get_qbd_ccc_mapping_cost_center': {
        "count": 2,
        "next": "http://localhost:8008/api/workspaces/1/qbd_mappings/?attribute_type=ITEMS",
        "previous": '',
        "results": [
            {
                "id": 3,
                "attribute_type": "COST_CENTER",
                "source_value": "Administration",
                "source_id": "1234",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.625706Z",
                "updated_at": "2023-08-28T05:46:59.326614Z",
                "workspace": 1
            },
            {
                "id": 4,
                "attribute_type": "COST_CENTER",
                "source_value": "Analytics",
                "source_id": "5678",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.627857Z",
                "updated_at": "2023-08-28T05:46:59.330073Z",
                "workspace": 1
            },
        ]
    },
    'get_qbd_ccc_mapping_project': {
        "count": 2,
        "next": "http://localhost:8008/api/workspaces/1/qbd_mappings/?attribute_type=ITEMS",
        "previous": '',
        "results": [
            {
                "id": 3,
                "attribute_type": "PROJECT",
                "source_value": "Aaron",
                "source_id": "1234",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.625706Z",
                "updated_at": "2023-08-28T05:46:59.326614Z",
                "workspace": 1
            },
            {
                "id": 4,
                "attribute_type": "PROJECT",
                "source_value": "Abbott",
                "source_id": "5678",
                "destination_value": "",
                "created_at": "2023-08-25T11:19:09.627857Z",
                "updated_at": "2023-08-28T05:46:59.330073Z",
                "workspace": 1
            },
        ]
    },
     'post_qbd_ccc_mapping_project': {
        "id": 1,
        "attribute_type": "PROJECT",
        "source_value": "Aaron",
        "source_id": "1234",
        "destination_value": "Mastercard",
        "created_at": "2023-08-25T11:19:09.608035Z",
        "updated_at": "2023-08-28T10:07:30.524503Z",
        "workspace": 1
    },
     'post_qbd_ccc_mapping_cost_center': {
        "id": 1,
        "attribute_type": "COST_CENTER",
        "source_value": "Analystics",
        "source_id": "5678",
        "destination_value": "Mastercard",
        "created_at": "2023-08-25T11:19:09.608035Z",
        "updated_at": "2023-08-28T10:07:30.524503Z",
        "workspace": 1
    },
}
