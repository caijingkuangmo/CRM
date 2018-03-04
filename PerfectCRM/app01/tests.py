# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.

# import re
#
# r = re.findall('\w+','sdfgsdf255')
# print(r)







def func1():
    print 1
    return False

def func2():
    print 2
    return True


li = [func1() or func2()]
print li[0]

