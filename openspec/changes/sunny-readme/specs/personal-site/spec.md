## ADDED Requirements

### Requirement: GitHub Pages personal website

The repository SHALL be configured to serve a personal website via GitHub Pages, displaying the author's content collection, media coverage, and worldview evolution.

#### Scenario: Site is accessible

- **WHEN** GitHub Pages is enabled on the repository
- **THEN** the site is publicly accessible and displays the author's content

### Requirement: Content listing page

The site SHALL include a listing page that displays all collected content (articles, media coverage, presentations) in reverse chronological order, with title, date, source type, and link to original source.

#### Scenario: New content appears on site

- **WHEN** a new content file is added to `content/raw/`
- **THEN** the content listing page includes the new entry after the site is rebuilt

### Requirement: Media coverage section

The site SHALL include a dedicated section for media coverage records, displaying publication name, date, title, and link to the original report.

#### Scenario: Media coverage displayed

- **WHEN** media coverage files exist in the content collection with source type "media"
- **THEN** the media section lists them grouped by year

### Requirement: Worldview evolution display

The site SHALL include a page that visualizes worldview evolution, showing how the author's beliefs on key topics have changed over time, derived from the extraction data.

#### Scenario: Belief evolution visible

- **WHEN** multiple extractions exist for the same topic across different dates
- **THEN** the worldview page displays the chronological progression of stances on that topic
