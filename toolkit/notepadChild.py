#! /usr/bin/env python3

import subprocess

print("hello world")

endProcess = subprocess.run(["notepad.exe"])

print(endProcess)
print("goodbye cruel world")
