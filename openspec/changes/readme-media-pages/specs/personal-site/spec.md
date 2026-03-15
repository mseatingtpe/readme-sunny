## MODIFIED Requirements

### Requirement: GitHub Pages personal website

The repository SHALL be configured to serve a personal website via GitHub Pages, displaying the author's content collection, media coverage, and worldview evolution. The repository SHALL be set to public visibility to enable GitHub Pages on a free plan.

#### Scenario: Site is accessible

- **WHEN** GitHub Pages is enabled on the repository with source set to `docs/` directory
- **THEN** the site is publicly accessible at `https://mseatingtpe.github.io/readme-sunny/`

#### Scenario: Dashboard link in README

- **WHEN** GitHub Pages is active
- **THEN** the README "互動式儀表板" section SHALL link to the GitHub Pages URL instead of a local file path

## ADDED Requirements

### Requirement: README structure with Skill prominence

The README SHALL place the Skill section immediately after the intro, before the worldview snapshot, to maximize visibility of the most externally valuable output. The full section order SHALL be: intro, Skill, 世界觀快照, 互動式儀表板, 媒體與分享, 文章.

#### Scenario: Skill appears before worldview

- **WHEN** `generate_readme.py` generates the README
- **THEN** the Skill section appears as the first content section after the introductory text
