# Character Creation Guide

To add a new character to your game, simply create a new Markdown file in the `Characters/` directory.

## File Format (`.md`)
The generator parses standard Markdown headers (`#` and `##`) to identify data.

### Example: `Characters/MyHero.md`
```markdown
# Name
MyHero @Handle

## Image
MyHero.png

## Image Prompt
(Optional) A detailed description of the character for AI generation.
"Portrait of a cyberpunk hacker, neon lights, rain..."

## Role
The description of their role or class.

## Quote
"Reference quote here."

## Personal Quest
Describe their main motivation.

## Key Entity
**Key Ally:** Name of ally.

## Abilities
- Hacking
- Stealth
- Pistols

## Core Personality
- Traits
- Goes
- Here

## Stress Response
- Specific reaction to stress.

## Equipment
- Deck
- Datapad

## Background
A longer paragraph describing their history and backstory.
```

## Key Sections

| Section | Description |
| :--- | :--- |
| **# Name** | The character's name. Optionally add `@Handle` for their player/alias. |
| **## Image** | Filename of the portrait. Must be in `images/` directory. If missing, the system tries to generate it. |
| **## Image Prompt** | **New!** Specific instructions for the AI image generator. If omitted, the system builds a prompt from Role and Background. |
| **## Abilities** | List of skills or powers (bullet points). |
| **## Background** | Full text biography. |

[Return to Home](../README.md)
