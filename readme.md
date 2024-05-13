# Mend
Mend is a language based on Scratch, with influence from Lua
<br>
Yeah, that's it

<br>

### Current language version: 1.0
#### "The 'Functions Work Now' Update"
**Changelog**
* (not sure) Functions should now work and the `return` keyword actually has usage, however function arguments still do not work(I don't wanna touch that right now)

* (new feature) '?' can be used at the end of lines to get debug information(currently limited).

* (new feature) '//', ';', and '#' can now be used for comments in addition to '--'.

* (change) The `get` keyword has been upgraded, you can now do `get mut [var]` and `get immut [var]` to assign it as that type (`get [var]` is the same as `get mut [var]`).

* (change) Removed the usage of the `get` keyword when declaring variables, as it's redundant now.

* (bugfix) Loops now work correctly, previously they ran the code inside of them one more than the specified amount.

* (bugfix) Fixed all errors so that they completely stop the entire program instead of per interpreter instance.

* (back-end) The `make_comment` function for the lexer has been generalized for any one-line comment using any symbol(s).

* (back-end) Functions have been abstracted into a class.

<br><br>

**This repository is licensed under the MIT license**<br>
So, I would of course prefer if you didn't steal my work as your own,<br>
but you can do whatever you want with the code as long as you use the same license


<br><br><br>

~~The name is a funny joke because it's based off of Scratch and mend is the opposite of scratch haha really funny my friends call me a comedian sometimes~~