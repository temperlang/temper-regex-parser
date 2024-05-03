# Temper Regex Parser

    export let name = "temper-regex-parser";
    export let version = "0.2.0";

## Metadata

    export let authors = "Temper Contributors";
    export let description = "Parser for the Temper regex dialect";
    export let homepage = "https://temperlang.dev/";
    export let license = "Apache-2.0";
    export let repository = "https://github.com/temperlang/temper-regex-parser";

## Imports

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
