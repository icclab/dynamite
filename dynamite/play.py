__author__ = 'brnr'

import argparse
import os
import platform

#raise FileNotFoundError("random message")

first_list = [1]
second_list = [1,2,3]
#
# in_first = set(first_list)
# in_second = set(second_list)
#
# print(type(in_first))
#
# in_second_but_not_in_first = in_second - in_first
#
# result = first_list + list(in_second_but_not_in_first)
# print(result)  # Prints [1, 2, 2, 5, 9, 7]
# print(type(result))

#print(first_list + list(set(second_list) - set(first_list)))

a = set(['C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files'])
b = set(['C:\\Users\\brnr\\PycharmProjects\\dynamite', 'C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite', 'C:\\Users\\brnr\\PycharmProjects\\dynamite\\dynamite\\tests\\TEST_CONFIG_FOLDER\\service-files'])

print("A: ", a)
print("B: ", b)
print("A-B: ", a-b)
print("B-A: ", b-a)

print(list(a)+list(b-a))

