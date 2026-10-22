# Manual Test Findings

This document tracks findings discovered during manual testing of the Obforce functionality.
It serves as a rough punch list of items to be addressed either as part of the current 
implementation scope or in a fast-follow or future release.

---

## Findings

The findings are outlined in the sections below.

### MTF-1 - HTML character references displayed literally in generated notes

- **Internal Tracking ID**: MTF-1
- **Title**: HTML character references displayed literally in generated notes
- **Categories**: Templates; Note Rendering; User Experience
- **Proposed Release**: v0.1.0

#### Details

HTML numeric character references are displayed within the Obsidian Markdown notes 
when viewing the notes in the *Live Preview* mode, causing readability issues when not 
viewing notes in *Reading* mode.

For example:

- Underscores are represented as `&#95;`
- Double quotes are represented as `&#34;`
- Hyphens are represented as `&#45;`

Below is Markdown output from the **Salesforce Metadata** section of a note for an Apex class.

````markdown
## Salesforce Metadata

- ApexClass: DemoService
- Namespace: none
- Source: local
- Source provenance: local&#45;apex&#45;xml&#45;v1
- api&#95;version: &#34;67&#46;0&#34;
- created&#95;at: unavailable (not collected or accessible)
- created&#95;by: unavailable (not collected or accessible)
- last&#95;modified&#95;at: unavailable (not collected or accessible)
- last&#95;modified&#95;by: unavailable (not collected or accessible)
- status: &#34;Active&#34;
````

As end-users will likely spend most of their time in the *Live Preview* mode, these HTML entities 
should be converted to their standard values to ensure readability.

It is also worth noting that standard double quotes (`"`) should be used instead of curly double 
quotes so that anything copied/pasted will be formatted properly.

