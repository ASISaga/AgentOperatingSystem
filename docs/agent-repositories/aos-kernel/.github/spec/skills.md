Creating and adding skills

Create a subdirectory for your new skill. Each skill should have its own directory (for example, .github/skills/webapp-testing). Skill directory names should be lowercase, use hyphens for spaces, and typically match the name in the SKILL.md frontmatter.

For project skills, specific to a single repository, store your skill under .github/skills or .claude/skills.

For personal skills, shared across projects, store your skill under ~/.copilot/skills or ~/.claude/skills.

Create a SKILL.md file with your skill's instructions.

Note

Skill files must be named SKILL.md.

SKILL.md files are Markdown files with YAML frontmatter. In their simplest form, they include:

YAML frontmatter
name (required): A unique identifier for the skill. This must be lowercase, using hyphens for spaces.
description (required): A description of what the skill does, and when Copilot should use it.
license (optional): A description of the license that applies to this skill.
A Markdown body, with the instructions, examples and guidelines for Copilot to follow.
Optionally, add scripts, examples or other resources to your skill's directory. For example, if you were writing a skill for converting images between different formats, you might include a script for converting SVG images to PNG.