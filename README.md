## Iface Watch : A Deluge plugin to monitor a network interface for IP changes ##

Author: bendikro <bro.devel+ifacewatch@gmail.com>


License: GPLv3

## Building the plugin ##

```
#!bash

$ python setup.py bdist_egg
```


## Changelog ##

v1.2 - 2015-11-13

* Moved interface checking to background thread

v1.1 - 2015-09-27

* Added library ifcfg to support FreeBSD and OSX

v1.0 - 2015-09-27

* Support for unix hosts with pyiface

(Tested with Deluge 1.3.11)
