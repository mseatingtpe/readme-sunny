## ADDED Requirements

### Requirement: Extract worldview snapshot from content

The system SHALL process each raw content file and produce an extraction file containing seven dimensions:

1. **Timestamp**: The publication date of the content
2. **Topics**: One or more topic tags (e.g., AI, entrepreneurship, identity, love)
3. **Stance**: What the author believes at this point in time
4. **Tension**: What this belief opposes or contradicts
5. **Connections**: Cross-domain references the author draws between different fields
6. **Shift signal**: Any indication of belief change ("I used to think X, now I think Y")
7. **Key quote**: The single most representative sentence from the content

#### Scenario: New content file is added

- **WHEN** a new file appears in `content/raw/`
- **THEN** the system generates an extraction YAML file in `content/extractions/` with all seven dimensions populated

#### Scenario: Content has no shift signal

- **WHEN** the content does not contain any indication of belief change
- **THEN** the shift signal field SHALL be set to null

### Requirement: Extraction output format

Each extraction SHALL be stored as a YAML file in `content/extractions/` with the same base filename as the source content file.

The YAML file SHALL reference the source content file path.

#### Scenario: Extraction file structure

- **WHEN** an extraction is generated for `content/raw/2025-07-22-ai.md`
- **THEN** the extraction is saved as `content/extractions/2025-07-22-ai.yaml` with a `source` field pointing to the raw file

### Requirement: Extraction triggered automatically

The extraction process SHALL be triggered automatically after new content is collected via the RSS pipeline, using the Claude API to perform the extraction.

#### Scenario: RSS collection triggers extraction

- **WHEN** a GitHub Actions workflow collects a new Substack article
- **THEN** the same workflow run SHALL invoke the Claude API to extract the seven dimensions and commit the extraction file

### Requirement: Worldview timeline

The system SHALL maintain a cumulative worldview profile file (`content/worldview-profile.yaml`) that aggregates all extractions, organized by topic, with chronological ordering to reveal belief evolution.

#### Scenario: Profile updated after extraction

- **WHEN** a new extraction file is committed
- **THEN** the worldview profile file is regenerated to include the new extraction data
