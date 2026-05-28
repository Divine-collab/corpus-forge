# Prompt Engineering Playbook for Quiz and Flashcard Generation

This playbook is for **Layer 2** of Corpus Forge: improving Gemini prompts so quiz and flashcard generation becomes more grounded, less hallucination-prone, and easier to evaluate.

## Goal

We want the AI to:

- stay inside the source document
- avoid invented facts
- generate consistent output formats
- produce usable quizzes and flashcards on the first try
- make it easy to compare prompt versions over time

## What changed in the app

The app now supports a `prompt_version` field for:

- `POST /generate_quiz`
- `POST /generate_flashcards`

Supported versions right now:

- `v1` — baseline prompt
- `v2` — improved evidence-first prompt

If no version is supplied, the app uses `v2`.

## Prompt versions

### `v1` — baseline

This is the old style prompt.

**Strengths**

- simple
- easy to understand
- good as a baseline for comparison

**Weaknesses**

- more likely to drift outside the source
- weaker guardrails against hallucination
- less explicit quality control

### `v2` — evidence-first

This is the improved prompt.

**Strengths**

- explicitly tells Gemini to use only supported facts
- asks for distinct questions/cards
- includes a quality checklist
- reduces unsupported additions
- improves output consistency

**Recommended default:** use `v2` for normal runs.

## Recommended iteration process

Use this cycle for both quizzes and flashcards:

1. **Start with `v1`** as your baseline.
2. **Run the same document** with the same settings.
3. **Inspect the output** for hallucinations, duplication, format errors, and weak coverage.
4. **Move to `v2`** and run the exact same document again.
5. **Compare the results** side by side.
6. **Decide whether the prompt improved** on:
   - factual grounding
   - format reliability
   - question quality
   - answer quality
7. **Keep the better version** as the default.
8. If needed, design a new `v3` and repeat.

## Evaluation rubric

Score each generated result from 1 to 5:

| Criterion | What to check |
|---|---|
| Groundedness | Are all facts supported by the document? |
| Hallucination rate | Did the model invent anything? |
| Format correctness | Did it follow the expected output format exactly? |
| Coverage | Does it cover the important ideas, not just one section? |
| Uniqueness | Are the questions/cards distinct? |
| Usefulness | Would a student actually learn from it? |

## Comparison template

Use this table for each experiment:

| Experiment | Document | Prompt version | Hallucinations | Format errors | Coverage | Notes |
|---|---|---:|---:|---:|---:|---|
| Quiz-01 | `sample.md` | v1 | 2 | 1 | 3 | Baseline prompt was too loose |
| Quiz-02 | `sample.md` | v2 | 0 | 0 | 4 | Much more grounded |
| Flashcard-01 | `sample.md` | v1 | 1 | 0 | 3 | Some cards were too generic |
| Flashcard-02 | `sample.md` | v2 | 0 | 0 | 4 | Better topical focus |

## What to record for each run

For every prompt version, keep these fields:

- prompt version
- document name
- number of questions/cards requested
- raw model output
- how many hallucinations you found
- whether the format was valid
- whether the parser succeeded
- your final rating

## How to think about better prompts

When a version performs poorly, ask:

- Did we tell the model to use only the document?
- Did we make the output format too vague?
- Did we ask for too many items from too little source material?
- Did we ask for diversity without defining it?
- Did the prompt leave room for the model to improvise?

Then improve one thing at a time.

## Suggested next version ideas

If you want a `v3`, consider one of these directions:

- **structured output**: ask for JSON so parsing is more reliable
- **section-aware prompts**: ask the model to cover different parts of the document
- **self-check prompts**: ask the model to verify each item before returning
- **difficulty control**: let the user choose easy / medium / hard questions
- **citation hints**: ask the model to reference the part of the document used for each item

## Practical rule

Change only one prompt aspect per experiment.

For example, change:

- one version to be more strict about document grounding
- another version to require better formatting
- another version to improve coverage

That way, you can tell **what actually helped**.

## Suggested default workflow for the app

- Use `v2` for normal use
- Keep `v1` as the baseline comparison
- Save results in your notes or journal after each run
- Compare outputs on the same document with the same request size

## Final advice

Good prompt engineering is not just about writing a longer prompt. It is about making the model’s job more precise, more constrained, and easier to verify.

If the output is wrong, do not immediately add more words. First ask:

- What kind of mistake is it?
- Is it a grounding problem?
- Is it a format problem?
- Is it a coverage problem?
- Is it a parsing problem?

That answer tells you what the next version should change.
