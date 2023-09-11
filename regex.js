
import("temper-regex-parser/runtime.js").then((regex) => {
    const re = regex.compile('[a-z]+');
    const got = re.find('abc');
    for (const [k, v] of got) {
        console.log(k, v.value);
    }
    console.log(got);
});
