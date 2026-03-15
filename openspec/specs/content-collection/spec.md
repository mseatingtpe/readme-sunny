# content-collection Specification

## Purpose

TBD - created by archiving change 'sunny-readme'. Update Purpose after archive.

## Requirements

### Requirement: Collect content from Substack RSS

The system SHALL automatically fetch new articles from a configured Substack RSS feed URL on a daily schedule via GitHub Actions.

Each fetched article SHALL be stored as a Markdown file with YAML frontmatter containing: title, date, source URL, and source type ("substack").

The system SHALL NOT re-fetch articles that already exist in the repository (determined by source URL).

#### Scenario: New Substack article published

- **WHEN** a new article appears in the Substack RSS feed
- **THEN** the system creates a new Markdown file in `content/raw/` with the article body and frontmatter metadata

#### Scenario: Article already collected

- **WHEN** the RSS feed contains an article whose source URL matches an existing file
- **THEN** the system skips that article without creating a duplicate

---
### Requirement: Store media coverage records

The system SHALL support manually adding media coverage as Markdown files with YAML frontmatter containing: title, date, source URL, publication name, and source type ("media").

#### Scenario: User adds media coverage

- **WHEN** a user creates a new Markdown file in `content/raw/` with source type "media"
- **THEN** the file is included in the content collection and available for extraction

---
### Requirement: Store presentation content

The system SHALL support manually adding presentation content as Markdown files with YAML frontmatter containing: title, date, source type ("presentation"), and optional link to original source.

#### Scenario: User adds presentation notes

- **WHEN** a user creates a new Markdown file in `content/raw/` with source type "presentation"
- **THEN** the file is included in the content collection and available for extraction

---
### Requirement: Content directory structure

All raw content files SHALL be stored under `content/raw/` with filenames in the format `YYYY-MM-DD-<slug>.md`.

#### Scenario: File naming convention

- **WHEN** a new content file is created (automatically or manually)
- **THEN** the filename follows the pattern `YYYY-MM-DD-<slug>.md` where the date matches the content's publication date
