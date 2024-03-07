# P4 tutorial

This tutorial is based on a number of tools developed as part of the P4 foundation and the NGSDN tutorial repos.

The tutorial consists of two task: 

* *Basic Forwarding with P4*: this tutorial will allow you to exercise your P4 language knowledge and understand some key characteristics of the language. 
* *P4 network calculator*: This tutorial will get you to work with the control plane of the P4 language.

## Toolchain

The tooling for this tutorial will be based on Docker images maintained by the P4 foundation. We will will basically utilize two main docker containers. The `p4c` container contains all the compiler binaries, required to compile P4 programs. In this tutorial we will be using the open-soruce P4C compiler, maintained by the P4 foundation. The `stratum_bmv2` conrtainer contains a modified version of the Mininet framework and add support for the P4 Behavioural Model v2 switch, a reference implementation of the P4 switch specifications. 

In order to simplify the P4 development, we provide you with a Makefile that automates some several tasks. The action that you can execute are:

- _make p4-build_: This action will compile the file p4src/main.p4 in the respective exercise window and generate
  the required switch pipeline files in the folder `p4src/build`, i.e.,
 the  p4src/build/bmv2.json (The specification file for the switch), and
 ithep4src/build/p4info.txt (Required to generate the p4 bindinds., and
  p4src/build/p4info.txt ()) files.
- _make proto-build_: Generate the python bindings to run a GRPC client that can connect to the P4 switch. The binding are required to run the `util/simple_controller.py`, a Python executable that allows you to inject custom flows into a running P4 switch. 
- *make start, make stop, make restart*: You can use these Makefile actions to control the mininet network. 
- *make mn-cli*: This action will open a mininet terminal so that you can run mininet commands. In order to exit from the terminal, you should use the shortcut Ctrl+D. If you type exit, this will stop the whole Mininet instance and you will have to restart. 
- *make mn-logs*: This action will display the mininet log. This is only for debugging purposses. 

## Next steps ...

Now that you became familiar with the toolchain of this tutorial you can start working on the first exercise. Just open the exercise1/README.md to figure out what you have to. 