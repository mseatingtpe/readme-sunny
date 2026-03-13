## ADDED Requirements

### Requirement: Generate Claude Code Skill from extractions

The system SHALL generate a Claude Code Skill file that captures the author's thinking framework, structured in three layers:

1. **Core identity**: Fundamental beliefs and reasoning habits (updated infrequently)
2. **Topic stances**: Positions on specific topics with evolution history (updated every ~6 months)
3. **Recent dynamics**: Latest thinking and focus areas (updated with each new extraction)

#### Scenario: Skill generated from existing extractions

- **WHEN** the skill generation process runs
- **THEN** a Skill prompt file is produced that reflects the author's current worldview across all three layers

### Requirement: Skill reflects author voice

The generated Skill SHALL capture:
- The author's vocabulary and phrasing patterns
- The author's reasoning style (cross-domain connection-making, finding balance in contradictions)
- The author's decision-making tendencies

#### Scenario: Skill used by another person

- **WHEN** another user activates the Skill in Claude Code and asks a question
- **THEN** the AI response SHALL reflect the author's characteristic reasoning patterns and vocabulary

#### Scenario: Author uses Skill for self-extension

- **WHEN** the author activates the Skill and asks Claude to extend an idea
- **THEN** the AI response SHALL build on the author's established thinking framework

### Requirement: Skill auto-updated after extraction

The Skill file SHALL be regenerated automatically whenever the worldview profile is updated.

#### Scenario: New article triggers Skill update

- **WHEN** a new extraction is added and the worldview profile is regenerated
- **THEN** the Skill file is regenerated to incorporate the latest extraction data

### Requirement: Skill token budget

The Skill prompt SHALL NOT exceed 4000 tokens. When the content exceeds this limit, the recent dynamics layer SHALL be summarized to fit within budget.

#### Scenario: Skill exceeds token limit

- **WHEN** the generated Skill content exceeds 4000 tokens
- **THEN** the system summarizes the recent dynamics layer to bring the total within budget while preserving core identity and topic stances
