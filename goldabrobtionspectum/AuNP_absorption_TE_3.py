import meep as mp
import numpy as np
import matplotlib.pyplot as plt
#import PyMieScatt as ps
import math
from meep.materials import Au

r = 0.08  # radius of sphere

wvl_min = 0.4 #2*np.pi*r/10
wvl_max = 0.8 #2*np.pi*r/2

frq_min = 1/wvl_max
frq_max = 1/wvl_min
frq_cen = 0.5*(frq_min+frq_max)
dfrq = frq_max-frq_min
nfrq = 50

## at least 8 pixels per smallest wavelength, i.e. np.floor(8/wvl_min)
resolution = 200 #will modify it later on to set the resolution

dpml =wvl_max/2
dair =wvl_max/2

pml_layers = [mp.PML(thickness=dpml)]

symmetries = [mp.Mirror(mp.Y),
              mp.Mirror(mp.Z,phase=-1)]

s = 2*(dpml+dair+r)
cell_size = mp.Vector3(s,s,s)

# is_integrated=True necessary for any planewave source extending into PML
sources = [mp.Source(mp.GaussianSource(frq_cen,fwidth=dfrq,is_integrated=True),
                     center=mp.Vector3(-0.5*s+dpml),
                     size=mp.Vector3(0,s,s),
                     component=mp.Ez)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=pml_layers,
                    sources=sources,
                    k_point=mp.Vector3(),
                    default_material=mp.Medium(epsilon=1.7788),
                    symmetries=symmetries)

box_x1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(x=-r),size=mp.Vector3(0,2*r,2*r)))
box_x2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(x=+r),size=mp.Vector3(0,2*r,2*r)))
box_y1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(y=-r),size=mp.Vector3(2*r,0,2*r)))
box_y2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(y=+r),size=mp.Vector3(2*r,0,2*r)))
box_z1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(z=-r),size=mp.Vector3(2*r,2*r,0)))
box_z2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(z=+r),size=mp.Vector3(2*r,2*r,0)))

pt = mp.Vector3(0.5*s-dpml-0.5*r,0,0)
#sim.run(until_after_sources=mp.stop_when_fields_decayed(50,mp.Ez,pt,1e-2))
sim.run(until=10)

freqs = mp.get_flux_freqs(box_x1)
box_x1_data = sim.get_flux_data(box_x1)
box_x2_data = sim.get_flux_data(box_x2)
box_y1_data = sim.get_flux_data(box_y1)
box_y2_data = sim.get_flux_data(box_y2)
box_z1_data = sim.get_flux_data(box_z1)
box_z2_data = sim.get_flux_data(box_z2)

box_x1_flux0 = mp.get_fluxes(box_x1)

sim.reset_meep()

geometry = [mp.Sphere(material=Au,
                      center=mp.Vector3(),
                      radius=r)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=pml_layers,
                    sources=sources,
                    k_point=mp.Vector3(),
                    symmetries=symmetries,
                    geometry=geometry)

box_x1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(x=-r),size=mp.Vector3(0,2*r,2*r)))
box_x2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(x=+r),size=mp.Vector3(0,2*r,2*r)))
box_y1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(y=-r),size=mp.Vector3(2*r,0,2*r)))
box_y2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(y=+r),size=mp.Vector3(2*r,0,2*r)))
box_z1 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(z=-r),size=mp.Vector3(2*r,2*r,0)))
box_z2 = sim.add_flux(frq_cen, dfrq, nfrq, mp.FluxRegion(center=mp.Vector3(z=+r),size=mp.Vector3(2*r,2*r,0)))

#sim.load_minus_flux_data(box_x1, box_x1_data)
#sim.load_minus_flux_data(box_x2, box_x2_data)
#sim.load_minus_flux_data(box_y1, box_y1_data)
#sim.load_minus_flux_data(box_y2, box_y2_data)
#sim.load_minus_flux_data(box_z1, box_z1_data)
#sim.load_minus_flux_data(box_z2, box_z2_data)

pt = mp.Vector3(0.5*s-dpml-0.5*r,0,0)
#sim.run(until_after_sources=mp.stop_when_fields_decayed(50,mp.Ez,pt,1e-2))
sim.run(until=10)

box_x1_flux = mp.get_fluxes(box_x1)
box_x2_flux = mp.get_fluxes(box_x2)
box_y1_flux = mp.get_fluxes(box_y1)
box_y2_flux = mp.get_fluxes(box_y2)
box_z1_flux = mp.get_fluxes(box_z1)
box_z2_flux = mp.get_fluxes(box_z2)

scatt_flux = np.asarray(box_x1_flux)-np.asarray(box_x2_flux)+np.asarray(box_y1_flux)-np.asarray(box_y2_flux)+np.asarray(box_z1_flux)-np.asarray(box_z2_flux)
intensity = np.asarray(box_x1_flux0)/(2*r)**2
scatt_cross_section = np.divide(scatt_flux,intensity)
scatt_eff_meep = scatt_cross_section/(np.pi*r**2)

freqs = mp.get_flux_freqs(box_x1)

wavelengths = np.divide(1,freqs)
plt.figure()
plt.plot(wavelengths,scatt_eff_meep)
plt.show()
