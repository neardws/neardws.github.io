---
name: interview-spec
version: 1.0.0
description: Interview user in-depth to create a detailed spec. Use when user says "build a spec", "help me spec", "spec interview", or wants detailed requirements gathering through Q&A.
triggers:
  - "build a spec"
  - "help me spec"
  - "spec interview"
  - "interview me about"
  - "gather requirements"
---

# Interview Spec Skill

Deep-dive interview skill that uses follow-up questions to gather comprehensive requirements and generate detailed specifications.

## How It Works

This skill leverages Claude's `AskUserQuestion` tool (the same one used in Plan mode) to conduct an in-depth interview about your project or idea.

## Usage

Simply say:
- "Build me a spec for [your idea]"
- "Help me spec out [feature/project]"
- "Interview me about [topic]"

## Interview Process

The AI will ask detailed questions about:
- 🎯 **Goals & Objectives** - What are you trying to achieve?
- 🛠️ **Technical Implementation** - Architecture, stack, constraints
- 🎨 **UI & UX** - User flows, design preferences
- ⚖️ **Tradeoffs** - Performance vs features, time vs quality
- 🚧 **Concerns & Risks** - Edge cases, potential issues
- 📊 **Success Criteria** - How will you measure success?

## Output

After the interview is complete, the skill will:
1. Generate a comprehensive `spec.md` file
2. Include all discussed requirements
3. Organize by categories
4. Add implementation notes

## Example

```
User: Build me a spec for a task management app

AI: I'll interview you to create a detailed spec. Let me start with some questions...

Q1: What's the primary use case - personal productivity, team collaboration, or both?
Q2: Do you need integrations with existing tools (calendar, email, etc.)?
Q3: What's your preferred tech stack?
...
```

## Credits

Based on the viral skill shared by [@dannypostma](https://x.com/dannypostma) and adapted by [@hboon](https://x.com/hboon).

---

## Instructions for AI

Use the `AskUser` or `AskUserQuestionTool` user tool for questions.

Follow the user instructions and interview me in detail using the question tool about literally anything: technical implementation, UI & UX, concerns, tradeoffs, etc. but make sure the questions are not obvious. Be very in-depth and continue interviewing me continually until it's complete. Then, write the spec to a file.

<instructions>$ARGUMENTS</instructions>
