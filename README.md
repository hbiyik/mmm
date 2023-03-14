What is mmm?

mm is a tool to inspect and manipulate the memory mapped devices from the linux/android user space?
Practically it means that you can manipulate or view your SOCs registers values from the linux userspace without kernel in the way.
To manipulate the regiters you need a catalog which are located under libmmm/devices/. Currently only allwinner A33 is supported but it can be extended as necessary.

Be aware that this tool can easily break your linux kernel, or even damage your hardware if you do not know what you are manipualting. In case of view only it should be safe.
It is currently quite expertimantal, may crash anytime.