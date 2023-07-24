import sys
import json
from initiatorInterface import *

args = sys.argv


def test():
    init = initiation("0xFe4cc19ea6472582028641B2633d3adBB7685C69", "Ergo")


if len(args) >= 1:
    if args[1] == "test":
        test()
