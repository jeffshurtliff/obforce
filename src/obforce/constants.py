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

# Offline acquisition limits are refusal boundaries, never truncation controls.
MAX_PROJECT_BYTES = 65_536
MAX_APEX_XML_BYTES = 65_536
MAX_APEX_SOURCE_BYTES = 1_048_576
MAX_LOCAL_ENTRIES = 50_000
MAX_LOCAL_DEPTH = 32
MAX_LOCAL_PACKAGES = 128
MAX_LOCAL_XML_TOTAL_BYTES = 16_777_216
MAX_XML_ELEMENTS = 256
MAX_XML_DEPTH = 16
SALESFORCE_METADATA_NAMESPACE = 'http://soap.sforce.com/2006/04/metadata'
LOCAL_APEX_METHOD = 'local-apex-xml-v1'

# CLI byte limits apply during collection, before decoding or JSON parsing.
SF_TIMEOUT_SECONDS = 60
SF_CLEANUP_SECONDS = 2
MAX_SF_STDOUT_BYTES = 8_388_608
MAX_SF_STDERR_BYTES = 65_536
MAX_SF_JSON_DEPTH = 32
MAX_SF_JSON_NODES = 100_000
MAX_SF_RECORDS = 10_000
MAX_SF_TARGET_CHARS = 256
MAX_SF_QUERY_CHARS = 16_384

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
