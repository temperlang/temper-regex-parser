# Temper Regex Parser

A regular expression parser for the Temper programming language that converts regex pattern strings into `std/regex` AST nodes.

## Overview

This library parses regex pattern syntax and builds structured `RegexNode` objects that can be compiled into executable `Regex` instances. It extends the standard regex syntax with additional features like named captures and pattern slots, and it can write nodes back out as pattern text.

## Features

### Standard Regex Syntax
- **Character classes**: `[abc]`, `[^xyz]`, `[a-z]`, and shorthands inside them, including negated ones, as in `[a\d]` or `[^\S\n]`
- **Shorthands**: `\d` (digit), `\s` (space), `\w` (word character), and their negations `\D`, `\S`, `\W`. All three are ASCII only.
- **Escape sequences**:
  - `\n`, `\r`, `\t`, `\f`, `\v`, `\a` (bell), `\e` (escape), `\0` (null)
  - `\cX` (control character, as in `\cJ` for newline)
  - `\xNN`, `\uXXXX`, and `\u{X...}` (1 to 6 hex digits). A code point above U+FFFF can also be written as a `\uXXXX\uXXXX` surrogate pair.
  - `\` before any ASCII punctuation or a space matches that character
  - `\b` inside a character class is backspace
- **Repetition**: `*`, `+`, `?`, `{n}`, `{n,}`, `{n,m}`, each optionally followed by `?` to match as few as possible
- **Alternation**: `|`
- **Anchors**: `^` or `\A` (start), `$` or `\z` (end), `\b` (word boundary)
- **Special**: `.` (any character except newline), `()` (grouping)

### Extended Syntax
- **Named captures**: `(?name=pattern)` - capture groups with names, which must be an ASCII letter followed by ASCII letters or digits, and unique within the pattern. Spaces are allowed around the name, as in `(? name = pattern)`.
- **Non-capturing groups**: `(?:pattern)` - group without capturing
- **Pattern slots**: `(?$name)` - reference pre-defined patterns
- **Case-insensitive groups**: `(?i:pattern)` - match ASCII letters in either case
- **Extended groups**: `(?x:pattern)` - ignore whitespace and `#` comments, outside of character classes. Flags combine, as in `(?ix:...)`.
- **Comments**: `(?#text)` - ignored

### Edge Case Handling
- Empty character classes `[]` and `[^]`
- Leading/trailing dashes in character classes
- Escaped special characters
- Unicode support
- Error messages with the position of the problem

## Installation

Add this library to your Temper project's dependencies.

## Usage

### Basic Parsing

```temper
let { parse, compile } = import("temper-regex-parser");

// Parse a pattern into a RegexNode AST
let node = parse(raw"[a-z]+\d{2,4}") orelse panic();

// Compile directly to an executable Regex
let regex = compile(raw"\d{3}-\d{4}") orelse panic();
let match = regex.find("Call 555-1234") orelse panic();
```

### Named Captures

```temper
let regex = compile(raw"(?year=\d{4})-(?month=\d{2})-(?day=\d{2})") orelse panic();
let match = regex.find("Date: 2024-12-25") orelse panic();

let year = match.groups["year"] orelse panic();
console.log(year.value);  // "2024"
```

### Pattern Slots

Define reusable pattern components:

```temper
let { parseWith, compileWith } = import("temper-regex-parser");

let digitPair = parse(raw"\d{2}") orelse panic();
let slots = new Map([new Pair("dd", digitPair)]);

// Use (?$dd) to reference the slot
let regex = compileWith(raw"(?$dd)-(?$dd)-(?$dd)", slots) orelse panic();
```

Capture names in slots count toward uniqueness, so a slot that holds a capture can only be used once in a pattern.

### Formatting and Escaping

```temper
let { escape, format } = import("temper-regex-parser");

let text = format(parse(raw"\A\d+\z") orelse panic()) orelse panic();  // "^\d+$"
let literal = escape("1+1=2?");  // "1\+1=2\?"
```

## API Reference

### Functions

#### `parse(src: String): RegexNode throws Bubble`
Parse a regex pattern string into a RegexNode AST.

#### `compile(src: String): Regex throws Bubble`
Parse and compile a regex pattern string into an executable Regex.

#### `parseWith(src: String, slots: Mapped<String, RegexNode>): RegexNode throws Bubble`
Parse a pattern with pre-defined pattern slots.

#### `compileWith(src: String, slots: Mapped<String, RegexNode>): Regex throws Bubble`
Parse and compile a pattern with pre-defined pattern slots.

#### `parseError(src: String, slots: Mapped<String, RegexNode>): String?`
Returns why a pattern doesn't parse, such as `at position 2: unexpected ')'; unmatched closing parenthesis`, or null if it parses. The position counts code points. `slots` is optional and defaults to no slots.

#### `format(node: RegexNode): String throws Bubble`
Writes a node as pattern text that parses back to an equivalent node, such as `^\d+$`. Case-insensitive groups come out expanded, as in `[aA]`. Bubbles for nodes that don't come from `std/regex`, such as a `Special` defined elsewhere, and for invalid code points.

#### `escape(text: String): String`
Escapes text so it matches literally when put in a pattern, outside of a `(?x:...)` group.

### Parsed Trees

The parser simplifies as it goes, so a tree may not mirror the pattern's syntax:
- A class with a single character or shorthand is that node itself, so `a[b]c` parses to the same `CodePoints("abc")` as `abc`.
- A group or slot that isn't repeated merges into a surrounding node of the same kind, so `a(?:b.)c` is one `Sequence` of `ab`, `.`, and `c`, and `(?:a|b)|c` is one `Or` of three items.
- `(?i:...)` is expanded into classes, so `(?i:ab)` is the same tree as `[aA][bB]`.
- Negated shorthands in a class become an `Or` (`[a\D]`) or an explicit set of code points (`[^\S\n]`), since `std/regex` code sets can't hold them.

## Error Handling

All parsing functions use Temper's `Bubble` error handling, and stop at the first error. Call `parseError` with the same arguments to get the reason:

```temper
let { parse, parseError } = import("temper-regex-parser");

let pattern = raw"[unclosed";
let node = parse(pattern) orelse do {
  console.log(parseError(pattern) ?? "");  // "at position 9: missing closing ']'"
  panic()
};
```

## Testing

Run the test suite:

```bash
temper test
```

Tests cover:
- Character class edge cases
- Escape sequence handling
- Group and capture syntax
- Flag groups and comments
- Repetition operators
- Parser error cases and messages
- Unicode handling
- Formatting and escaping

## Known Limitations

- Lookahead, lookbehind, backreferences, `\B`, and Unicode property escapes like `\p{L}` are not supported.
- Only the `i` and `x` inline flags are supported, and only in the group form `(?i:...)`. `(?i)` on its own is not.
- `(?<name>...)` and Python-style `(?P...)` groups are rejected in favor of `(?name=...)`.
- Case-insensitive matching and the shorthands only cover ASCII.

## Development

Built with Temper and compiled to multiple target languages. The parser uses recursive descent and stops at the first error.
