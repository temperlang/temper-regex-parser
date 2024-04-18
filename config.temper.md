# Temper Regex Parser

    export let name = "temper-regex-parser";
    export let version = "0.1.0";

We keep tests in a separate module right now, and we don't import tests from
prod code, so import both explicitly from config.

    import(".");
    import("./tests");

## Backend Config

### Java

Use same core packaging plans as temper-core and std.

    export let javaGroup = "dev.temperlang";
    export let javaArtifact = "temper-regex-parser";
    export let javaPackage = "temper.regex_parser";
