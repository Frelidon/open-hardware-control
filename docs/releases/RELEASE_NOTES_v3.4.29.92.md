# Open Hardware Control 3.4.29.92 INTERN

- Static and animated LCD designs share the existing single daemon IPC ticker.
  Static frames are periodically sent to prevent the documented TRCC display
  timeout; hidden pages and close-to-tray keep physical output active.
- LCD Runtime 1.0 recognizes successful complete positive sent-byte messages
  from the official CLI (installed 9.9.12 source checked). A live process, banner,
  stderr chatter or incomplete output never renews progress. 45-s startup/finite
  command deadlines; 15-s missing-progress deadline after successful sends.
  Timeout stops only the concrete owned client and delegates existing bounded
  ticker/daemon recovery; five-minute daemon cooldown and quarantine remain.
- Process Runtime 1.1 captures sensor stderr/tracebacks and invalid protocol
  causes. Existing RGB SDK client gains five-second ready/frame deadlines,
  1/2/4-s backoff and three automatic retries. Only confirmed progress in a
  30-s stable generation renews the SDK restart budget. Existing hardware owner,
  effect phase, selection and fail-closed permissions remain authoritative.
- Private bounded module-events.jsonl records version/session/time, module,
  PID, exit code/status, runtime, request/failure evidence and recovery decisions.
  Errors also enter errors.log; diagnostics export remains explicit/anonymized.
- Read-only GameMode/process-name probing runs outside the Qt GUI with one
  in-flight probe, bounded execution and current-intent guards. System Status
  displays LCD send count/age and an explicit read-only sensor-restart action.
  1,481 complete DE/EN/ES/FR messages. Test cache/state are isolated.
- Correct ZIP installation examples to the actual current INTERN archive/folder.

The supplied .91 log has successful design starts and tray operation, no LCD
failure, but covers less than five minutes. No hardware soak test or physical
LCD/readback guarantee. The send parser targets the verified CLI contract;
unsupported output fails visibly. A native backend crash still quarantines
rather than entering an automatic crash loop. Cooling/core and GUI are not yet
fully separated services; existing calibrated PWM and firmware watchdog remain.
No installation, firmware/backend update or public publishing.

Reference: [official TRCC CLI](https://github.com/Lexonight1/thermalright-trcc-linux/blob/main/doc/REFERENCE_CLI.md).
Validation: all 17 new fault-injection tests and the complete 673-test release
gate passed, including four-language UI, security/privacy and module budgets.
DE/FR System Status rendered and reviewed. Packaged artifact verification pending.

Post-build completion: both ZIP CRCs, 227 current Python sources, source archive,
RPM digests/metadata and complete-history Git bundle verified. Dist/.91/.92
SHA256 passed; exactly two complete backups remain, .90 rotated under standing
approval. DEB unavailable. Added after packaging; archived notes retain the
pre-build status. No installation or live hardware soak test.
