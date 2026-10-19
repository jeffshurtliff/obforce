# -*- coding: utf-8 -*-
"""
:Module:            obforce.constants
:Synopsis:          Defines versioned internal configuration and ownership contracts
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     19 Oct 2026
"""

CONFIG_SCHEMA_VERSION = 1
MODEL_SCHEMA_VERSION = 1
NOTE_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1
MARKER_VERSION = 1
RENDERER_VERSION = 1
MAX_CONFIG_BYTES = 65_536

GENERATED_START = '<!-- obforce:generated:start -->'
GENERATED_END = '<!-- obforce:generated:end -->'
IDENTITY_PROPERTIES = frozenset({'obforce_id', 'obforce_schema'})
SF_PROPERTIES = frozenset(
    {
        'sf_type',
        'sf_full_name',
        'sf_namespace',
        'sf_api_version',
        'sf_status',
        'sf_created_at',
        'sf_created_by',
        'sf_last_modified_at',
        'sf_last_modified_by',
        'sf_source_mode',
        'sf_dependency_coverage',
        'sf_lifecycle',
    }
)
OWNED_PROPERTIES = IDENTITY_PROPERTIES | SF_PROPERTIES
COMPONENT_ATTRIBUTES = frozenset({'api_version', 'status', 'created_at', 'created_by', 'last_modified_at', 'last_modified_by'})
DEFAULT_APEX_DIRECTORY = 'Custom Code/Apex Classes'
DEFAULT_DASHBOARD_DIRECTORY = 'Dashboards'
