"""
修复 CSV 字段大小限制问题
必须在导入 google.adk 之前导入此模块
"""
import sys
import csv

# 增加 CSV 字段大小限制到最大值
# 解决 importlib_metadata.packages_distributions() 读取包元数据时的错误:
# _csv.Error: field larger than field limit (131072)
csv.field_size_limit(sys.maxsize)
