
"""NBA_ENDPOINT_MAP
    endpoint_type:
    endpoint_specifier:
    snowflake_table:
    table_append:
    fn_get_keys: 
    
"""
NBA_ENDPOINT_MAP = {
    'uri_base': 'http://api.sportradar.us/nba/trial/v7/en',
    'changes': {
        'fn_get_keys': lambda year, month, day: [
            'league',
            year,
            month,
            day,
            'changes.json',
        ],
    },
    'pbp': {
        'table_append':False,
        's3_dir': 'games/',
        'file_replace': True,
        'table': 'sr_nba.parsed_pbp',
        'fn_get_keys': lambda row_id, last_modified: [
            'games',
            row_id,
            'pbp.json',
        ],
    }
}
