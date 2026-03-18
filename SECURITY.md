# Security Policy

## Who This Document Is For

This document is for:

- people using MedBot for personal or family health management
- self-hosters and deployers
- developers and contributors

It explains how to use MedBot more safely when the project handles **medical and health-related data**, especially household records, symptoms, medications, reports, measurements, and doctor-facing exports.

This document is **not** a prompt for the agent. It is a user-facing security and safety guide.

## Reporting a Vulnerability

If you discover a security vulnerability in MedBot, please report it by:

1. **Do not** open a public GitHub issue for sensitive vulnerabilities.
2. Create a private security advisory on GitHub or contact the maintainers at `xubinrencs@gmail.com`.
3. Include:
   - a clear description of the issue
   - reproduction steps
   - possible impact
   - a suggested fix if available

We aim to respond to security reports within 48 hours.

## Sensitive Data Scope

MedBot may process highly sensitive data, including:

- names or identities of family members
- symptom descriptions and timelines
- chronic conditions, diagnoses, surgeries, and hospitalizations
- medications, allergies, contraindications, and side effects
- laboratory results, medical imaging summaries, and uploaded reports
- blood pressure, blood glucose, weight, and other longitudinal health metrics
- doctor-facing exports and follow-up plans

Treat all data under `~/.medbot/`, especially `workspace/family/`, `workspace/memory/`, `workspace/sessions/`, `media/`, and exported records, as sensitive by default.

## Core Security Principles

### 1. Local-First by Default

MedBot is designed to keep health data local by default.

Recommendations:

- store the workspace on a device and disk you trust
- avoid placing `~/.medbot/` in broadly synced public/shared folders
- protect local backups as carefully as the live data

### 2. Minimum Necessary Disclosure

Only send the minimum necessary content to:

- external LLM providers
- search or web services
- chat channels such as `qq`, `telegram`, `whatsapp`, `email`, or `feishu`

Before enabling outbound delivery, ask yourself:

- does this destination really need the content
- does it need the full record, or only a summary
- is the destination controlled by the intended recipient

### 3. Household Data Separation

MedBot is built for family use, which introduces a special risk: **mixing one member's data with another member's record**.

You should:

- review household member records periodically
- confirm names and family relationships carefully
- pay extra attention when multiple family members have similar conditions
- verify exports before forwarding them to clinicians or relatives

## Recommended Deployment Practices

### Config and Local Permissions

Never commit API keys or real health data to version control.

```bash
chmod 700 ~/.medbot
chmod 600 ~/.medbot/config.json
chmod 700 ~/.medbot/workspace
```

If you use the WhatsApp bridge:

```bash
chmod 700 ~/.medbot/whatsapp-auth
```

### Dedicated Runtime User

For long-running deployments, use a dedicated non-root user account.

Do not run MedBot as `root`.

### Channel Access Control

Always configure `allowFrom` or equivalent allow-lists for production usage.

This is especially important for channels that can receive messages from multiple people or groups.

Example:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["123456789"]
    },
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

Security note:

- empty `allowFrom` should not be treated as public access
- use explicit allow-lists unless you intentionally want broader access

## Medical Data Handling Risks

### 1. Automatic Record Capture

MedBot may extract and structure health information from normal conversation.

Benefits:

- less manual record-keeping
- better pre-visit preparation
- more complete family timelines

Risks:

- user statements may be incomplete or ambiguous
- one family member's information may be captured under the wrong person
- casual conversation may be mistaken for durable facts if not reviewed

Best practice:

- review important records periodically
- correct mistakes early
- verify auto-captured facts before using them in doctor-facing exports

### 2. Doctor-Facing Exports

MedBot can generate clinician-facing summaries and exports.

You should assume exported files may be:

- forwarded outside your device
- printed
- stored by other people or systems
- shared across channels like `qq`, `whatsapp`, or `email`

Before sending an export:

- check that the correct family member is selected
- review the summary for accuracy
- remove unrelated personal details if they are not needed
- confirm the target channel or recipient is correct

### 3. PDF and File Conversion

If you convert doctor-facing Markdown exports into PDF or other formats, remember:

- converted files are still sensitive medical data
- file conversion may produce extra copies on disk
- forwarding the PDF is effectively forwarding the medical record

After conversion, know:

- where the file was saved
- who will receive it
- whether it should be deleted after use

## Third-Party Service Risks

### LLM Providers

If you use a third-party model provider, your prompts and attached content may leave your machine.

Review the provider's:

- privacy policy
- data retention policy
- enterprise / no-training options if available

If you handle real household medical data, prefer providers and deployment modes that match your privacy requirements.

### Search, Fetch, OCR, Transcription, and Conversion

Optional features such as:

- web search
- web fetch
- OCR
- transcription
- external converters

may involve additional privacy and security considerations depending on how they are configured.

Only enable such capabilities when you understand where data may be sent and processed.

## Not a Medical Device

MedBot is a health support assistant, not a licensed medical device, not a diagnostic system, and not an emergency response tool.

Do not rely on MedBot alone for:

- emergency triage
- urgent diagnosis
- medication prescription decisions
- critical care or life-threatening scenarios

If symptoms suggest an emergency, seek professional medical help immediately.

## Logs, Sessions, and Backups

Be aware that the following may contain sensitive information:

- `~/.medbot/workspace/sessions/`
- `~/.medbot/workspace/family/`
- `~/.medbot/workspace/memory/`
- `~/.medbot/logs/`
- exported medical summaries and converted PDFs

Recommendations:

- protect local logs and backups
- avoid sharing session files for debugging without redaction
- sanitize data before using screenshots or examples publicly

## Dependency and Supply Chain Security

Keep both Python and Node.js dependencies up to date.

Recommended checks:

```bash
pip install pip-audit
pip-audit
```

For the bridge:

```bash
cd bridge
npm audit
```

Also review custom skills before using them, especially if they:

- run shell commands
- send network requests
- read or export medical records
- introduce new conversion or upload flows

## Incident Response

If you suspect misuse, data leakage, or unauthorized access:

1. revoke or rotate compromised API keys immediately
2. disable affected chat channels temporarily
3. inspect recent logs and session history
4. review exported files and recent forwarding actions
5. check whether family records were modified incorrectly
6. update dependencies and redeploy if needed
7. report security issues to the maintainers when appropriate

## Security Checklist

Before using MedBot with real family health data:

- [ ] `~/.medbot` permissions are restricted
- [ ] API keys are not committed to git
- [ ] chat channels use explicit allow-lists
- [ ] MedBot runs as a non-root user
- [ ] you understand which providers and services receive data
- [ ] household member records are reviewed for mix-ups
- [ ] exported files are checked before forwarding
- [ ] logs and backups are protected
- [ ] dependencies and custom skills are reviewed regularly

## License

See `LICENSE` for license details.
