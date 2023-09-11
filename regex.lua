
local regex = require('temper-regex-parser/runtime')

local re = regex.compile('ab')

local found = re:found('abcd')

print(found)
