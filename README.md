# Temper Regex Parser

A regular expression parser for the Temper programming language that converts regex pattern strings into `std/regex` AST nodes.

## Overview

This library parses regex pattern syntax and builds structured `RegexNode` objects that can be compiled into executable `Regex` instances. It extends the standard regex syntax with additional features like named captures and pattern slots.

## Features

### Standard Regex Syntax
- **Character classes**: `[abc]`, `[^xyz]`, `[a-z]`
- **Escape sequences**: `\d`, `\w`, `\s`, `\n`, `\t`, `\\`, `\/`, `\e` (escape), `\cX` (control character), and `\` before any ASCII punctuation or a space
- **Repetition**: `*`, `+`, `?`, `{n}`, `{n,}`, `{n,m}`
- **Alternation**: `|`
- **Anchors**: `^` or `\A` (start), `$` or `\z` (end), `\b` (word boundary)
- **Special**: `.` (any character), `()` (grouping)

### Extended Syntax
- **Named captures**: `(?name=pattern)` - capture groups with names, which must be an ASCII letter followed by ASCII letters or digits, and unique within the pattern
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
- Proper error reporting with position information

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
let match = regex.find("Call 555-1234");
```

### Named Captures

```temper
let regex = compile(raw"(?year=\d{4})-(?month=\d{2})-(?day=\d{2})") orelse panic();
let match = regex.find("Date: 2024-12-25");

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

#### `parseError(src: String, slots: Mapped<String, RegexNode> = empty): String?`
Returns why a pattern doesn't parse, such as `at position 2: unexpected ')'; unmatched closing parenthesis`, or null if it parses. The position counts code points.

#### `format(node: RegexNode): String throws Bubble`
Writes a node as pattern text that parses back to an equivalent node, such as `^\d+$`. Case-insensitive groups come out expanded, as in `[aA]`.

#### `escape(text: String): String`
Escapes text so it matches literally when put in a pattern, outside of a `(?x:...)` group.

## Error Handling

All parsing functions use Temper's `Bubble` error handling. Call `parseError` with the same arguments to get the reason:

```temper
let result = parse(raw"[unclosed") orelse do {
  console.log("Parse failed");
  return;
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
- Repetition operators
- Parser error cases
- Unicode handling

## Known Limitations

- Nested named captures are not currently supported (e.g., `(?outer=(?inner=...))`).

## Development

Built with Temper and compiled to multiple target languages. The parser uses recursive descent and stops at the first error.
