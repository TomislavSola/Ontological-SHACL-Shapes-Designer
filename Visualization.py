import matplotlib.pyplot as plt
import pickle
import os
from collections import OrderedDict

bundle_dir = os.path.dirname(os.path.abspath(__file__))

with open(bundle_dir+"\\plotDictionary.pkl", "rb") as tf:
    pyshacl_plot_dict = pickle.load(tf)


pyshacl_plot_dict = OrderedDict(sorted(pyshacl_plot_dict.items()))

print(pyshacl_plot_dict)

pyshacl_x= list(pyshacl_plot_dict.keys())

print(f"Violations from {min(pyshacl_x)} upto {max(pyshacl_x)}")

pyshacl_y = list(pyshacl_plot_dict.values())

print(f"Time from {min(pyshacl_y)} upto {max(pyshacl_y)}")

#dict copied from the c# benchmark main console output
dotnet_plot_dict = {
  2:0.001,
  93:0.027,
  186:0.056,
  10:0.005,
  257:0.058,
  33:0.007,
  461:0.107,
  207:0.064,
  18:0.005,
  147:0.032,
  438:0.105,
  967:0.132,
  32:0.006,
  1271:0.196,
  312:0.099,
  0:0.001,
  9:0.002,
  8:0.003,
  21:0.006,
  36:0.008,
  29:0.007,
  34:0.008,
  832:0.179,
  1918:0.459,
  3056:0.512,
  48:0.008,
  4733:0.846,
  1698:0.525}

dotnet_plot_dict = OrderedDict(sorted(dotnet_plot_dict.items()))

print(dotnet_plot_dict)

dotnet_x= list(dotnet_plot_dict.keys())
dotnet_y= list(dotnet_plot_dict.values())

#dict copied from the java benchmark main console output
apache_plot_dict = {
  0: 0,
  832: 0.008,
  257: 0.005,
  2: 0.001,
  967: 0.012,
  8: 0,
  9: 0,
  10: 0.001,
  461: 0.005,
  207: 0.005,
  18: 0,
  147: 0.001,
  21: 0,
  93: 0.005,
  29: 0,
  32: 0.001,
  33: 0.001,
  34: 0,
  1698: 0.01,
  36: 0,
  3056: 0.024,
  48: 0.001,
  438: 0.008,
  1271: 0.011,
  312: 0.002,
  186: 0.006,
  4733: 0.032,
  1918: 0.023
}

apache_plot_dict = OrderedDict(sorted(apache_plot_dict.items()))

print(apache_plot_dict)

apache_x= list(apache_plot_dict.keys())
apache_y= list(apache_plot_dict.values())

# plotting the data
plt.plot(pyshacl_x, pyshacl_y,c='r',label='pySHACL')
plt.plot(dotnet_x, dotnet_y,c='g',label='dotNetRDF')
plt.plot(apache_x, apache_y,c='b',label='Apache Jena')

# Adding the title
plt.title("Durchschnittliche Laufzeit als Funktion der Anzahl gefundener Violations")
plt.legend()

# Adding the labels
plt.ylabel("Durchschnittliche Laufzeit [s]")
plt.xlabel("Anzahl gefundener Violations")

#plt.savefig(bundle_dir+"\\benchmark_runtimes.pdf")

plt.show()
