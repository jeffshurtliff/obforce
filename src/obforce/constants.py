# -*- coding: utf-8 -*-
"""
:Module:            obforce.constants
:Synopsis:          Defines versioned internal configuration and ownership contracts
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     26 Oct 2026
"""

CONFIG_SCHEMA_VERSION = 1
MODEL_SCHEMA_VERSION = 1
NOTE_SCHEMA_VERSION = 1
STATE_SCHEMA_VERSION = 1
STATE_DOCUMENT_VERSION = 2
EVIDENCE_SCHEMA_VERSION = 1
MAX_EVIDENCE_BYTES = 8_388_608
MARKER_VERSION = 1
RENDERER_VERSION = 4
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
        'sf_created',
        'sf_created_by',
        'sf_last_modified_at',
        'sf_last_modified',
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
DASHBOARD_SCHEMA_VERSION = 1
DASHBOARD_FILENAME = 'Apex Classes.base'
DASHBOARD_MARKER = b'# obforce:dashboard:apex_classes:v1\n'
MAX_DASHBOARD_BYTES = 16_384

# Live collection uses bounded SELECT keyset pages, never arbitrary continuation URLs.
LIVE_APEX_METHOD = 'live-apex-keyset-v1'
LIVE_AUDIT_METHOD = 'live-apex-scoped-audit-v1'
LIVE_PAGE_SIZE = 200
MAX_LIVE_PAGES = 51
MAX_LIVE_RECORDS = 10_000
MAX_LIVE_QUERIES = 156
LIVE_TIMEOUT_SECONDS = 300
MAX_LIVE_STDOUT_BYTES = 262_144

# Relationship probes cannot prove exhaustion: MCD forbids ordered/queryMore paging.
RELATIONSHIP_METHOD = 'platform-mcd-equality-v1'
MAX_RELATIONSHIP_QUERIES = 101  # Includes the minimal Organization identity query.
MAX_RELATIONSHIP_RECORDS = 10_000  # Counts returned rows before deduplication.
MAX_RELATIONSHIP_PAGE_RECORDS = 2_000  # Current documented Tooling cap, not exhaustion proof.
MAX_RELATIONSHIP_STDOUT_BYTES = 1_048_576
RELATIONSHIP_TIMEOUT_SECONDS = 300
MAX_RELATIONSHIP_LABEL_CHARS = 512
MAX_GRAPH_EDGES = 20_000
MAX_GRAPH_OBSERVATIONS = 40_000

# Candidate rendering uses finite interpolation, never general template execution.
MARKDOWN_LIST_INDENT = '    '
TEMPLATE_SLOTS = {
    'apex_created.md.j2': (),
    'apex_generated.md.j2': ('metadata', 'coverage', 'references', 'referenced_by'),
}
MAX_TEMPLATE_BYTES = 16_384
MAX_TEMPLATE_NODES = 256
MAX_RENDER_TEXT_CHARS = 4_096
MAX_RENDER_INPUT_BYTES = 2_097_152
MAX_RENDER_INPUT_NODES = 100_000
MAX_RENDER_COMPONENTS = 10_000
MAX_RENDER_EDGES = 2_000
MAX_RENDER_PATH_CHARS = 1_024
MAX_RENDER_PATH_DEPTH = 32
MAX_RENDER_SECTION_BYTES = 524_288
MAX_NOTE_BYTES = 1_048_576

# Existing-note parsing checks tokens/events before constructing round-trip objects.
MAX_FRONTMATTER_BYTES = 65_536
MAX_NOTE_PROPERTIES = 128
MAX_YAML_TOKENS = 8_192
MAX_YAML_NODES = 4_096
MAX_YAML_DEPTH = 2
MAX_YAML_SCALAR_BYTES = 16_384
MAX_YAML_LIST_ITEMS = 1_024

# State/discovery limits bound private reads and candidate output, never publication.
MAX_STATE_BYTES = 16_777_216
MAX_STATE_DEPTH = 16
MAX_STATE_NODES = 250_000
MAX_STATE_TEXT_BYTES = 2_097_152
MAX_STATE_NOTES = 10_000
MAX_VAULT_ENTRIES = 50_000
MAX_VAULT_READ_BYTES = 67_108_864

# Complete read-only planning and local reporting bounds, independent of read limits.
MAX_PLAN_COMPONENTS = 10_000
MAX_PLAN_ACTIONS = 10_000
MAX_PLAN_INPUT_BYTES = 16_777_216
MAX_PLAN_OUTPUT_BYTES = 67_108_864
MAX_PLAN_PRECONDITIONS = 400_000
MAX_REPORT_ACTIONS = 1_000
MAX_REPORT_BYTES = 262_144
PLANNER_UUID_NAMESPACE = 'bdc896b6-c99e-571e-bf41-35e33fd18eab'
CONTROL_DIRECTORIES = frozenset({'.git', '.obsidian', '.obforce'})

# Internal transaction/recovery refusal limits; not public tuning options.
TRANSACTION_SCHEMA_VERSION = 2
MAX_TRANSACTION_FILES = 128
MAX_TRANSACTION_BYTES = 33_554_432
MAX_JOURNAL_BYTES = 16_777_216
MAX_JOURNAL_DEPTH = 20
MAX_JOURNAL_NODES = 300_000
MAX_TRANSACTION_GUARDS = 50_000
MAX_TRANSACTION_DIRECTORIES = 256
MAX_TRANSACTION_REPORT_BYTES = 1_024
MAX_TRANSACTION_ABSOLUTE_CHARS = 4_096

# Initial public setup never recursively creates unbounded ancestry.
MAX_SETUP_DIRECTORIES = 32
