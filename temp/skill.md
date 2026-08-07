---
name: create-learn-cource
description: 'Authoring format for Global AI Learn courses: the folder layout and YAML front matter for course.md, module.md, page files and final-test.md, the question schema (single-choice, multiple-choice, true-false), the identifier rules, and the validation rules the loader enforces. Use whenever writing, converting or reviewing course content for the Global AI Community learning platform, in this repo or in a separate content repo.'
---

# Global AI Learn - course authoring format

Course content is plain Markdown with YAML front matter. The website loads it at startup with
`CourseContentLoader`, validates every file, and drops any course that produces a single
diagnostic. Get the format exactly right or the course will not appear in the catalog.

## When to use
- Writing a new course, module, lesson page or final test
- Converting a workshop, README or slide deck into a course
- Reviewing or fixing course content that fails to load

## Golden rules
1. **Every file starts with YAML front matter**, opened by `---` on line 1 and closed by `---` on
   its own line. Use **LF line endings** - the parser matches `---\n` literally, so CRLF files fail.
2. **All ids are slugs**: `^[a-z0-9]+(?:-[a-z0-9]+)*$`. Lowercase letters and digits, single hyphens
   between them. No spaces, underscores, capitals, or leading/trailing hyphens.
3. **One diagnostic drops the whole course.** A bad question id in module 4 removes the entire
   course from the catalog, not just that question.
4. **Order comes from the arrays**, not from the `order:` field. `modules:` in `course.md` and
   `pages:` in `module.md` define the sequence. Keep `order:` in sync as documentation.
5. **Publication, credits and the completion badge are not content.** They are set per course in
   `/admin/learn`. Never try to put them in front matter.

## Folder layout

Each course is a folder containing `course.md`. The loader scans the content root recursively for
`course.md`, so courses can sit at any depth.

```
<course-id>/
├── course.md                     # course manifest + intro prose
├── final-test.md                 # final exam questions
└── modules/
    ├── 01-<module-id>/
    │   ├── module.md             # module manifest + intro prose + check questions
    │   └── pages/
    │       ├── 01-<page-id>.md
    │       └── 02-<page-id>.md
    └── 02-<module-id>/
        └── ...
```

Numeric prefixes are optional but recommended so the folder listing reads in order. A folder or
file name matches an id when it either equals the id exactly, or is `<digits>-<id>`
(`03-build-server` matches id `build-server`, `3-build-server` also works, `mod-build-server` does not).

## course.md

```yaml
---
schemaVersion: 1                  # required, must be exactly 1
id: mcp-workshop                  # required, slug, must be unique per version
version: "1.0"                    # required, quote it so YAML keeps it a string
title: Build with the Model Context Protocol
summary: Build an MCP server, connect a client, and take the result into a browser.
durationMinutes: 115              # required, greater than zero
difficulty: Intermediate          # free text, shown on the catalog card
prerequisites:                    # optional, rendered as a checklist
  - Python 3.10 or newer
  - Git and a terminal
learningOutcomes:                 # optional, rendered as a tick list
  - Explain how MCP reduces integrations from M x N to M + N
  - Build an MCP server with tools, resources and prompts
image: /images/learn/mcp.jpg      # optional
modules: [setup, mcp-basics, build-server]   # required, ordered module ids
---

Intro prose in Markdown. This renders on the course overview page above the outcomes.
```

`id` + `version` must be unique across all courses. If two courses share both, **both copies are
dropped**. Bump `version` for a new revision of the same course.

## module.md

```yaml
---
id: build-server                  # required, must equal the id used in course.md modules:
title: Build an MCP server        # required
summary: Define typed tools and expose a resource and prompt.
order: 3                          # documentation only
pages: [server-capabilities]      # ordered page ids, must be unique
questions:                        # required, at least one
  - id: structured-output
    type: multiple-choice
    prompt: Which benefits come from returning a Pydantic model from a tool?
    options:
      - id: schema
        text: The SDK can generate an output schema
      - id: validation
        text: Returned data can be validated
      - id: secret-auth
        text: MCP automatically adds authentication
    correctOptionIds: [schema, validation]
    explanation: Typed models provide schema and validation. Authentication stays an application concern.
---

Optional module intro prose.
```

Every module needs at least one question. The questions become the module check the learner takes
after finishing the module's pages.

## Page files (`modules/<module>/pages/*.md`)

```yaml
---
id: server-capabilities           # required, must equal the id used in module.md pages:
title: Tools, resources, prompts, and errors
order: 1                          # documentation only
estimatedMinutes: 25              # required, greater than zero
---

The lesson body in Markdown. This is the whole lesson - there is no other body field.
```

## final-test.md

```yaml
---
title: MCP workshop final test    # required
questions:                        # required, at least one
  - id: final-scaling
    type: single-choice
    prompt: What integration shape does MCP provide for M hosts and N systems?
    options:
      - id: additive
        text: Approximately M + N implementations
      - id: multiplicative
        text: M x N custom adapters
    correctOptionIds: [additive]
---

Optional intro prose shown above the final test.
```

`final-test.md` sits next to `course.md` and is **required**. It has no `id` and no `schemaVersion`.

## Question schema

| Field | Rule |
|---|---|
| `id` | Required slug, unique within the file |
| `type` | One of `single-choice`, `multiple-choice`, `true-false` |
| `prompt` | Required, non-empty |
| `options` | At least 2, each with a slug `id` (unique within the question) and `text` |
| `correctOptionIds` | Non-empty, every entry must be an option id in the same question |
| `explanation` | Optional, shown to the learner after grading |

Extra type rules:
- `single-choice` and `true-false`: exactly **one** correct option id.
- `true-false`: exactly **two** options.
- `multiple-choice`: one or more correct option ids. Renders as checkboxes and shows the hint
  "One or more answers possible".

Grading is all-or-nothing: the learner must get **every** question right to pass a module check or
the final test. Write options that are clearly right or clearly wrong, not judgement calls.

## Markdown body

- The body is everything after the closing `---`.
- Rendered with Markdig **advanced extensions**: tables, fenced code blocks with language hints,
  task lists, footnotes, auto-links, definition lists.
- Output is **sanitized**. `<script>`, `on*` handlers and `javascript:` URLs are stripped, so raw
  HTML embeds, iframes and inline JS will not survive. Use Markdown.
- Do not repeat the page title as an `#` heading. The title from the front matter is already
  rendered as the page heading. Start body headings at `##`.

## Writing style

Course prose follows the house content style: friendly developer-to-developer, plain language,
second person. **No em dashes** - use a regular hyphen. Say "events" not "meetups", "chapters" not
"groups". Keep a lesson page to one idea and roughly the `estimatedMinutes` you declared.

## Common failures

| Diagnostic | Cause |
|---|---|
| `Document must start with YAML front matter.` | Missing `---`, a BOM, or CRLF line endings |
| `YAML front matter is not closed.` | No closing `---` on its own line |
| `Referenced module 'x' was not found.` | Folder name does not match the id, or `module.md` is missing |
| `Referenced page 'x' was not found.` | File name does not match the id, or it is not in `pages/` |
| `Module id must match reference 'x'.` | `id:` in `module.md` differs from the entry in `modules:` |
| `Invalid course id 'X'.` | Capitals, spaces or underscores in a slug |
| `Question 'x' has invalid correctOptionIds.` | Empty, or points at an option id that does not exist |
| `schemaVersion must be 1.` | Missing or wrong `schemaVersion` in `course.md` |
| `final-test.md was not found.` | Missing final test beside `course.md` |
| `Duplicate course id and version 'x:1.0'.` | Two courses share id + version, both are dropped |

## Validating

Drop the course folder into `GAIC.Website/CourseContent/` in the website repo, then either:

```bash
dotnet test GAIC.Website.Tests --filter CourseContentLoaderTests
```

or run the site and open `/admin/learn`, which lists every diagnostic with its source file. A
course that loads cleanly still needs to be published there before members can see it.
