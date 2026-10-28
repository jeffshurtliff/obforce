# Recover an interrupted operation

Stop ordinary writes when a command reports recovery required. Start with the
same explicit config and a read-only local preview:

```sh
obforce recover --config "/absolute/path/Fictional Workspace/Config with spaces.toml"
```

The default and `--dry-run` are write-free. Recovery never acquires source data or
queries Salesforce. Review the validated phase and recommended operation:

| Validated phase | Selected operation | Effect |
| --- | --- | --- |
| Precommit | `--rollback` | Restore matching before-images and complete prior state/evidence |
| Committed | `--cleanup` | Retain published output and remove only proven transaction-owned material |
| No pending evidence | None | Write-free no-op |
| Ambiguous, unsafe or incomplete | None | Refuse and retain evidence for private manual resolution |

```sh
# Execute only the one recommended by the validated preview:
obforce recover --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --rollback
# Or, for committed evidence:
obforce recover --config "/absolute/path/Fictional Workspace/Config with spaces.toml" --cleanup
```

The flags are mutually exclusive. Wrong-phase selection refuses with 3 and
preserves evidence. Intervening human edits must not be overwritten by rollback.
Cleanup removes only proven owned staging/new files with matching identity and
content. No recursive deletion, forced recovery, reset or adoption is provided.

Keep private evidence in place. Request private maintainer assistance for
contradictory journals or changed targets; do not paste notes/state/before-images
into public issues. Setup interrupted before a validated journal may leave
unprovable ownership requiring manual review. Rollback retains the control/lock;
it does not make the destination eligible for another initial build. Missing,
corrupt or unknown state is not reconstructed from notes. Legacy evidence-less
sync and journal-schema-1 recovery remain refused without migration.

## A safe fictional interruption exercise

Use only the development verification harness with fresh synthetic workspaces.
There is no public fault-injection command. Follow [contributor artifact
verification](../CONTRIBUTING.md#fresh-artifacts-and-tutorials) to build fresh
artifacts and select `dev/verify_tutorials.py` as the independent-install checker.
It copies only the supplied fictional DX sample outside checkout/cwd, verifies
both installed entry points and active runtime network/process denial, and injects
synthetic precommit/committed checkpoint failures. It executes preview, wrong-phase
refusal, rollback and committed cleanup, with byte/mtime checks and retained human
context. It also checks that intervening edits refuse recovery unchanged.
This is a bounded verification exercise, not an operational recovery API.

Never deliberately interrupt a real vault to practice recovery. Cooperating
writer/process/checkpoint tests do not qualify power loss, hostile races, Windows
ACL/directory durability, atomic snapshots or atomic multi-file publication.
Maintain independent vault backups yourself. See [safety](SYNC_SAFETY.md) and
[qualification](QUALIFICATION.md) for precise limits.
