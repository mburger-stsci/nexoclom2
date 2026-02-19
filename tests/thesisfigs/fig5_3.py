from nexoclom2.solarsystem import IoTorus
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


torus = IoTorus()

fig, ax = plt.subplots()
ax.plot(torus.M, torus.n_e, color='blue')
ax.set_xlabel('Distance from Jupiter (R$_J$)')

ax.set_ylabel('Electron Density (cm$^{-3}$)', color='blue', fontsize='large')
ax.tick_params(axis='y', labelcolor='blue', )
ax.yaxis.get_major_formatter().set_scientific(False)

ax1 = ax.twinx()
ax1.plot(torus.M, torus.T_e, color='red')
ax1.set_ylabel('Electron Temperature (eV)', color='red', fontsize='large')
ax1.tick_params(axis='y', labelcolor='red')

plt.pause(1)
plt.savefig('Fig5_3.png')
