## ADDED Requirements

### Requirement: Media data index file

The system SHALL maintain a `content/media.yaml` file as the single source of truth for all media appearances (interviews, talks, writing contributions). Each entry SHALL contain: title, date, type (interview/talk/writing), publication, url, speaker, and has_content flag.

#### Scenario: CSV import populates media.yaml

- **WHEN** the import script processes the team CSV file filtered for Sunny C entries
- **THEN** `content/media.yaml` contains all matching entries with structured metadata

#### Scenario: Manual entries alongside CSV data

- **WHEN** a media item is not in the CSV (e.g., INSIDE article, wazaiii writing)
- **THEN** the entry can be manually added to `content/media.yaml` following the same schema

### Requirement: Media content fetching for extraction

The system SHALL fetch full-text content from web-accessible interview articles and writing contributions, saving them as markdown files in `content/raw/` with `source_type: media` or `source_type: writing` frontmatter.

#### Scenario: Fetchable article is downloaded

- **WHEN** a media.yaml entry has type "interview" or "writing" and a valid URL pointing to a web article
- **THEN** the article text is fetched, cleaned, and saved to `content/raw/` with appropriate frontmatter

#### Scenario: Non-fetchable entry is skipped

- **WHEN** a media.yaml entry points to a Canva presentation, paywalled article, or non-text resource
- **THEN** the entry is listed in README but no content file is created and no extraction is attempted

### Requirement: README media section generation

The system SHALL generate a "媒體與分享" section in README.md from `content/media.yaml`, organized into three subsections: 採訪報導 (interviews), 演講與論壇 (talks), and 供稿 (writing). Each entry SHALL include date, title with hyperlink, and publication/venue name.

#### Scenario: README displays all media types

- **WHEN** `generate_readme.py` runs with media.yaml containing entries of all three types
- **THEN** README.md contains three subsection tables with linked entries sorted by date descending
