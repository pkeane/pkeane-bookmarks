# pkeane-bookmarks

A static bookmark viewer generated from a Chrome bookmarks HTML export.

## Usage

```bash
python3 generate.py <chrome_bookmarks.html> [-s STYLE] [-t TITLE]
```

Run `python3 generate.py --help` for full documentation.

### Examples

```bash
# Basic — prompts for style selection
python3 generate.py ~/Desktop/bookmarks.html

# Specify style and title
python3 generate.py ~/Desktop/bookmarks.html -s classic -t pkeane

# Multi-word title
python3 generate.py ~/Desktop/bookmarks.html -s ocean -t "peter keane"
```

## Output

- `bookmarks.jsonl` — one JSON record per bookmark with fields: `url`, `add_date`, `link_text`, `header_section`
- `index.html` — self-contained static page with sidebar navigation and live search

## Styles

Styles are defined in `styles.json`. Each style specifies a font pair and color palette. Available built-in styles:

| Name | Description |
|------|-------------|
| `classic` | Navy and orange — the original look |
| `midnight` | Dark mode with soft purple accents |
| `forest` | Deep greens with serif headings |
| `paper` | Warm sepia tones, newspaper feel |
| `ocean` | Deep blue with bright teal accents |

To add a new style, copy an existing entry in `styles.json` and edit the fields. The `name` should be a single word.

---

## Prompts used to build this project

This project was built interactively with [Claude Code](https://claude.ai/claude-code). Below are the prompts used, in order.

1. Please read the file at `/Users/pkeane/Desktop/bookmarks_3_19_26.html` and create a `bookmarks.jsonl` file that has a line of JSON for each bookmark with the fields: `url`, `add_date`, `link_text`, and `header_section`.

2. Please create a nice looking static HTML page using the data in `bookmarks.jsonl`; output it as `bookmarks.html`.

3. When I click a link in the sidebar the page scrolls to that header BUT the header itself is obscured by the top banner — change it so it scrolls down a bit farther.

4. I'd like to make this process repeatable — so I can supply a new file (which is an export of my Google Chrome bookmarks) and it will recreate `bookmarks.html` with the same looks and functionality but with new links.

5. Update the generate script so that the file it outputs is called `index.html`.

6. I do not see the `_TOP` section which is supposed to be at the top of the sidebar.

7. Use the more recent bookmarks source file — the one with `3_20_26` in the name.

8. I like having the Bookmarks Bar header, but please put that alphabetically in the list of headers. I have removed the `_TOP` header from the source file — there is now a section called `TOP` — please pin that to the top of the sidebar.

9. Now I'd like to clean up this project. I don't think we need the Flask app after all — our generate script does everything we need. Please delete unneeded files.

10. OK let's get this into GitHub.

11. Now I'd like the overall style to be configurable — having 4 or 5 different options for styling, each of which would define a set of fonts and a color palette. These options should live in a `styles.json` file (make sure it is human readable). When `generate.py` is run, the user will be prompted to select one of the preconfigured styles. Alternatively, the user can use a `-s` flag to indicate which style they'd like. Style names should be one word.

12. Now I'd like the title to be configurable. By default, instead of `pkeane bookmarks` the title should be `bookmarks`. The user can specify a string that should appear before `bookmarks` by using a `-t` flag. Please add a help section to `generate.py` that will be shown when the user types `generate.py --help` that explains how to select a style and provide a title.

13. Please create a `README.md` file that lists all of the prompts used to create this project.

14. Update `generate.py` to NOT include any links in a section called "private" (case-insensitive).

15. Please replace `README.md` to list all of the prompts used to create this project.
