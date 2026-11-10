# Step 1: reduced bracket model, rigid clamp, modal analysis (cross check).
# Units: mm, tonne, N, MPa.  Run in Abaqus/CAE: File > Run Script.
# Geometry: x along the length (0 = clamped end), y across the 40 mm width, z = thickness (bending direction).
from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh, os, regionToolset

L_TOT, W, T, L_CLAMP = 140.0, 40.0, 6.0, 40.0
SEED = 5.0

m = mdb.Model(name='BracketModal')

# part: 140 x 40 x 6 block, split at x = 40 so the clamped footprint is its own cell
s = m.ConstrainedSketch(name='profile', sheetSize=400.0)
s.rectangle(point1=(0.0, -W / 2), point2=(L_TOT, W / 2))
p = m.Part(name='Bracket', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=s, depth=T)
dp = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=L_CLAMP)
p.PartitionCellByDatumPlane(datumPlane=p.datums[dp.id], cells=p.cells)

# material: aluminium as in the Ansys model
mat = m.Material(name='Aluminium')
mat.Elastic(table=((71000.0, 0.33),))
mat.Density(table=((2.77e-9,),))
m.HomogeneousSolidSection(name='Sec', material='Aluminium', thickness=None)
p.SectionAssignment(region=regionToolset.Region(cells=p.cells), sectionName='Sec')

# mesh: about 5 mm, two elements through the thickness, incompatible mode bricks
p.seedPart(size=SEED, deviationFactor=0.1, minSizeFactor=0.1)
zedges = p.edges.findAt(((0.0, -W / 2, T / 2),), ((L_CLAMP, -W / 2, T / 2),), ((L_TOT, -W / 2, T / 2),),
                        ((0.0, W / 2, T / 2),), ((L_CLAMP, W / 2, T / 2),), ((L_TOT, W / 2, T / 2),))
p.seedEdgeByNumber(edges=zedges, number=2, constraint=FIXED)
p.setMeshControls(regions=p.cells, elemShape=HEX, technique=STRUCTURED)
p.setElementType(regions=(p.cells,), elemTypes=(mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD),))
p.generateMesh()
print('NODES: %d   ELEMENTS: %d   (Learning Edition limit is 1000 nodes)' % (len(p.nodes), len(p.elements)))

# assembly
a = m.rootAssembly
inst = a.Instance(name='Bracket1', part=p, dependent=ON)

# 0.5 kg tip mass on a reference point at the end face centre, coupled to the end face
rp = a.ReferencePoint(point=(L_TOT, 0.0, T / 2))
a.Set(referencePoints=(a.referencePoints[rp.id],), name='RP_tip')
a.engineeringFeatures.PointMassInertia(name='TipMass', region=a.sets['RP_tip'], mass=5.0e-4, alpha=0.0, composite=0.0)
endf = inst.faces.findAt(((L_TOT, 0.0, T / 2),))
a.Surface(side1Faces=endf, name='EndFace')
m.Coupling(name='TipCoupling', controlPoint=a.sets['RP_tip'], surface=a.surfaces['EndFace'],
           influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, weightingMethod=UNIFORM,
           localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

# rigid clamp: bottom face of the clamped footprint (x = 0 to 40) fixed
cf = inst.faces.getByBoundingBox(xMin=-1.0, xMax=L_CLAMP + 1.0, yMin=-W, yMax=W, zMin=-0.01, zMax=0.01)
a.Set(faces=cf, name='ClampFace')
m.EncastreBC(name='Clamp', createStepName='Initial', region=a.sets['ClampFace'])

# modal step and job
m.FrequencyStep(name='Modal', previous='Initial', numEigen=6, eigensolver=LANCZOS)
job = mdb.Job(name='Step1_fixed_clamp', model='BracketModal', description='fixed clamp modal')
job.submit(consistencyChecking=OFF)
job.waitForCompletion()

odb = session.openOdb(name=job.name + '.odb')
print('Modes of the fixed clamp model (Ansys bonded: 83.71 and 471.27 Hz, frictional: 78.31 and 321.3 Hz):')
frames = odb.steps['Modal'].frames
for i in range(1, len(frames)):
    print('  mode %d   %.2f Hz' % (frames[i].mode, frames[i].frequency))
