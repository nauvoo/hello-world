#find duplicates
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
location = input("Input the name of the file without quotes: ")
file = pd.read_excel(location)
print("########################################")
print ("File has been succesfully imported!")
print("#################################fit.xlsx#######")
print("The length of file (lines) is:", len(file))
print("########################################")
print(("Preview of 2 lines", file.head(n=2)))
df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))


#Desktop/Python/test.xlsx
