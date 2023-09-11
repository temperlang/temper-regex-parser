# Regex Match Test

Match compile-time constant regexes against strings.

Compile-time constant regexes used only for matching can be converted by
backends directly into the backend representation. We don't need to keep our
own representation around at all.

Compile-time transformation isn't yet implemented, but the same behavior is
supported at runtime as well. Once both are supported, we should test both.

    let { ... } = import("std/regex");

## Test Case 1

### Structurally built regex patterns

Beyond plans for a macro to parse our own regex dialect at compile-time, you
can also build regexes structurally. The macro parser builds these objects.

    // Equivalent to: let regex = /(?:ab)+c/;
    let regex = new Sequence([
      oneOrMore(new CodeSet([new CodePoints("ab")])),
      new CodePoints("c"),
    ]).compiled();
    let full = entire(regex.data).compiled();

### Matching regex objects against strings

Here we test only Boolean matches. We will test found strings and captures in
the future.

    let strings = [
      // Positive found and matches
      "abc",
      "ac",
      "bbabac",
      // Negative found and matches
      "ab",
      "dc",
      // Positive found, negative matches
      "acc",
      "cbc",
    ];
    // TODO(tjp, regex): Use forEach when we have that instead of abusing map.
    strings.map { (string): Int;;
      console.log("found ${string}: ${regex.found(string).toString()}");
      console.log("matches ${string}: ${full.found(string).toString()}");
      0
    }

### Expected results

```log
found abc: true
matches abc: true
found ac: true
matches ac: true
found bbabac: true
matches bbabac: true
found ab: false
matches ab: false
found dc: false
matches dc: false
found acc: true
matches acc: false
found cbc: true
matches cbc: false
```

## Test Case 2: Match details

### Match found

We can also get detailed match information. Different backends have different
capabilities. For example, .NET can report all repeated groups for a given
capture, but some remember only one, so support only what's common here.

    // Equivalent to: /a+ (?intro = b+) c ((?option1 = d) | (?alphaOption2 = e))+/
    let catcher = new Sequence([
      oneOrMore(new CodePoints("a")),
      { name: "intro", item: oneOrMore(new CodePoints("b")) },
      new CodePoints("c"),
      oneOrMore(
        new Or([
          { name: "option1", item: new CodePoints("d") },
          { name: "alphaOption2", item: new CodePoints("e") },
        ])
      ),
    ]).compiled();

Now capture and print everything out.

Also, use supplemental plane code point to start out, and leave a suffix.

    let groups = catcher.find("🌍aaabbceef");
    groups.toList().map { (entry): Int;;
      let { name, value, codePointsBegin } = entry.value;
      console.log(
        "match group '${name}': '${value}' at ${codePointsBegin.toString()}"
      );
      0
    }

Map iteration order is defined to be the order in which names appear in the pattern, so this list is reliable.

```log
match group 'full': 'aaabbcee' at 1
match group 'intro': 'bb' at 4
match group 'option1': '' at -1
match group 'alphaOption2': 'e' at 8
```

We can also do replacement.

Note that callbacks are supported in at least dotnet, java, js, and python. They
also more naturally adapt to custom types.

    // let replaced = catcher.replace<Result>("🌍aaabbceef") { (result);; ... }
    let replaced = catcher.replace("🌍aaabbceef") { (groups);;
      // Can we compile-time convert callbacks to simple template as applicable?
      "-${groups["option1"].value}${groups["alphaOption2"].value}-"
    };
    console.log("replaced: ${replaced}");
    // Also check a no-match case.
    let notReplaced = catcher.replace("nope") { (groups);; "hi" };
    console.log("not replaced: ${notReplaced}");

```log
replaced: 🌍-e-f
not replaced: nope
```

### No match

And when we have no match, can use `orelse` for a default result.

    let noMatch = catcher.find("not here")["full"].value orelse "sorry";
    console.log("No match says ${noMatch}");

```log
No match says sorry
```

## Additional Tests

At some point, we should port the randomized property testing of regexes from
Kotlin to Temper, but for now, here are a few hand-designed tests of additional
features.

This still doesn't test everything, but it tests at least some things.

Also, to keep code smaller, we don't always precompile regexes here. This also
results in testing that the shortcut inefficient compile-on-the-fly also works.

### Or options

    let or = new Or([new CodePoints("ab"), new CodePoints("bc")]);
    let option1 = "ab";
    let option2 = "bc";
    let optionNone = "cb";
    console.log("or option 1: ${or.found(option1).toString()}");
    console.log("or option 2: ${or.found(option2).toString()}");
    console.log("or option none: ${or.found(optionNone).toString()}");

```log
or option 1: true
or option 2: true
or option none: false
```

### String begin

    let begin = new Sequence([Begin, new CodePoints("a")]);
    let beginsWithATrue = "ab";
    let beginsWithAFalse = "bab";
    console.log("begin true: ${begin.found(beginsWithATrue).toString()}");
    console.log("begin false: ${begin.found(beginsWithAFalse).toString()}");

```log
begin true: true
begin false: false
```

### Negated set implies supplementary code range

These are tricky in JS, at least for V8 and SpiderMonkey.

    let negatedBasic = entire(
      new Sequence([
        // Having this extra item in the sequence makes a difference for causing
        // the tricky behavior in JS that we work around in our translation.
        new CodePoints("a"),
        {
          items: [new CodeRange("a".codePoints.read(), "c".codePoints.read())],
          negated: true,
        },
      ])
    ).compiled();
    let nbTrue = "a🌍";
    let nbFalse = "ac";
    console.log("negated basic true: ${negatedBasic.found(nbTrue).toString()}");
    console.log("negated basic false: ${
      negatedBasic.found(nbFalse).toString()
    }");

```log
negated basic true: true
negated basic false: false
```
