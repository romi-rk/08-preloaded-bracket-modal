# Step 2: reduced bracket with frictional contact to a base block, bolt clamp force as head pressure,
# then a prestressed modal analysis. Runs six cases that mirror the Ansys runs R1 to R6.
# Units: mm, tonne, N, MPa.  Run in Abaqus/CAE: File > Run Script (set a work directory first).
# Axes: x along the length (0 = clamped end), y = thickness and bending direction (vertical, as in Ansys),
#       z = across the 40 mm width (lateral).
# Simplifications: no bolt holes and no bolts (the clamp force acts as pressure on the head footprint),
#       the base block is a coarse aluminium solid fixed at its bottom face. This keeps the model under 1000 nodes.
from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh, regionToolset

L_TOT, T, W = 140.0, 6.0, 40.0      # bracket length, thickness, width
L_CLAMP = 40.0
HEAD_AREA = 100.0                   # mm2, 10 x 10 patch under each bolt head
BOLT_X = (10.0, 30.0)
ZC = W / 2.0                        # centre line of the width

# case name, preload per bolt (N), friction coefficient, Ansys f1 and f2 (Hz) for the comparison
CASES = [('R1', 1000.0, 0.2, 78.39, 323.9),
         ('R2', 3000.0, 0.2, 78.44, 325.6),
         ('R3', 6000.0, 0.2, 78.57, 327.4),
         ('R4', 8000.0, 0.2, 78.58, 328.1),
         ('R5', 3000.0, 0.1, 78.17, 286.8),
         ('R6', 3000.0, 0.3, 78.64, 346.2)]


def zedges_of(p):
    """edges that run in the y (thickness) direction"""
    out = []
    for e in p.edges:
        v = e.getVertices()
        c0 = p.vertices[v[0]].pointOn[0]
        c1 = p.vertices[v[1]].pointOn[0]
        if abs(c0[0] - c1[0]) < 1e-6 and abs(c0[2] - c1[2]) < 1e-6:
            out.append(e)
    return tuple(out)


def build_and_run(case, F, mu):
    m = mdb.Model(name=case)
    mat = m.Material(name='Aluminium')
    mat.Elastic(table=((71000.0, 0.33),))
    mat.Density(table=((2.77e-9,),))
    m.HomogeneousSolidSection(name='Sec', material='Aluminium', thickness=None)
    brick = mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD)

    # bracket, partitioned on a 5 mm grid so the head patches and the clamp edge are faces
    s = m.ConstrainedSketch(name='prof', sheetSize=400.0)
    s.rectangle(point1=(0.0, 0.0), point2=(L_TOT, T))
    p = m.Part(name='Bracket', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidExtrude(sketch=s, depth=W)
    for x in (5.0, 15.0, 25.0, 35.0, 40.0):
        dp = p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=x)
        p.PartitionCellByDatumPlane(datumPlane=p.datums[dp.id], cells=p.cells)
    for z in (ZC - 5.0, ZC + 5.0):
        dp = p.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=z)
        p.PartitionCellByDatumPlane(datumPlane=p.datums[dp.id], cells=p.cells)
    print('Bracket cells after partitioning: %d (expected 18)' % len(p.cells))
    p.SectionAssignment(region=regionToolset.Region(cells=p.cells), sectionName='Sec')
    p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
    p.seedEdgeByNumber(edges=zedges_of(p), number=2, constraint=FIXED)
    p.setMeshControls(regions=p.cells, elemShape=HEX, technique=STRUCTURED)
    p.setElementType(regions=(p.cells,), elemTypes=(brick,))
    p.generateMesh()

    # base block, 50 x 10 x 60 mm, very coarse
    bs = m.ConstrainedSketch(name='blk', sheetSize=400.0)
    bs.rectangle(point1=(-10.0, -10.0), point2=(40.0, 0.0))
    b = m.Part(name='Block', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    b.BaseSolidExtrude(sketch=bs, depth=60.0)
    b.SectionAssignment(region=regionToolset.Region(cells=b.cells), sectionName='Sec')
    b.seedPart(size=30.0, deviationFactor=0.1, minSizeFactor=0.1)
    b.setMeshControls(regions=b.cells, elemShape=HEX, technique=STRUCTURED)
    b.setElementType(regions=(b.cells,), elemTypes=(brick,))
    b.generateMesh()
    nodes = len(p.nodes) + len(b.nodes)
    print('%s: NODES %d (bracket %d, block %d), limit 1000' % (case, nodes, len(p.nodes), len(b.nodes)))
    if nodes > 1000:
        print('Too many nodes, stopping this case.')
        return None

    # assembly: block centred under the bracket width
    a = m.rootAssembly
    inst = a.Instance(name='Bracket1', part=p, dependent=ON)
    bi = a.Instance(name='Block1', part=b, dependent=ON)
    a.translate(instanceList=('Block1',), vector=(0.0, 0.0, -10.0))

    # tip mass on a reference point at the end face centre
    rp = a.ReferencePoint(point=(L_TOT, T / 2, ZC))
    a.Set(referencePoints=(a.referencePoints[rp.id],), name='RP_tip')
    a.engineeringFeatures.PointMassInertia(name='TipMass', region=a.sets['RP_tip'], mass=5.0e-4, alpha=0.0, composite=0.0)
    a.Surface(side1Faces=inst.faces.findAt(((L_TOT, T / 2, ZC),)), name='EndFace')
    m.Coupling(name='TipCoupling', controlPoint=a.sets['RP_tip'], surface=a.surfaces['EndFace'],
               influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, weightingMethod=UNIFORM,
               localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

    # base block fixed at its bottom face
    a.Set(faces=bi.faces.getByBoundingBox(xMin=-11.0, xMax=41.0, yMin=-10.01, yMax=-9.99, zMin=-11.0, zMax=51.0), name='BlockBottom')
    m.EncastreBC(name='FixBlock', createStepName='Initial', region=a.sets['BlockBottom'])

    # friction contact between block top (master) and the bracket footprint x = 0 to 40 (slave)
    a.Surface(side1Faces=bi.faces.getByBoundingBox(xMin=-11.0, xMax=41.0, yMin=-0.01, yMax=0.01, zMin=-11.0, zMax=51.0), name='BlockTop')
    a.Surface(side1Faces=inst.faces.getByBoundingBox(xMin=-1.0, xMax=L_CLAMP + 1.0, yMin=-0.01, yMax=0.01, zMin=-1.0, zMax=W + 1.0), name='BracketBottom')
    cp = m.ContactProperty('Fric')
    cp.TangentialBehavior(formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF,
                          pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((mu,),),
                          shearStressLimit=None, maximumElasticSlip=FRACTION, fraction=0.005, elasticSlipStiffness=None)
    cp.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
    m.SurfaceToSurfaceContactStd(name='Joint', createStepName='Initial', main=a.surfaces['BlockTop'],
                                 secondary=a.surfaces['BracketBottom'], sliding=SMALL, thickness=ON,
                                 interactionProperty='Fric', adjustMethod=NONE, initialClearance=OMIT,
                                 datumAxis=None, clearanceRegion=None)

    # preload step: head pressure = F / 100 mm2 on each bolt head footprint
    m.StaticStep(name='Preload', previous='Initial', initialInc=0.1, minInc=1e-6, maxInc=1.0,
                 stabilizationMagnitude=2e-4, stabilizationMethod=DISSIPATED_ENERGY_FRACTION)
    for i, xb in enumerate(BOLT_X):
        name = 'Head%d' % (i + 1)
        a.Surface(side1Faces=inst.faces.getByBoundingBox(xMin=xb - 5.1, xMax=xb + 5.1, yMin=T - 0.1, yMax=T + 0.1,
                                                          zMin=ZC - 5.1, zMax=ZC + 5.1), name=name)
        m.Pressure(name=name, createStepName='Preload', region=a.surfaces[name], distributionType=UNIFORM,
                   field='', magnitude=F / HEAD_AREA, amplitude=UNSET)

    # prestressed modal step (contact status frozen at the end of the preload step)
    m.FrequencyStep(name='Modal', previous='Preload', numEigen=6, eigensolver=LANCZOS)
    job = mdb.Job(name='Step2_' + case, model=case)
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    if job.status != COMPLETED:
        print('%s: job did not complete, check the .msg and .sta files in the work directory' % case)
        return None
    odb = session.openOdb(name=job.name + '.odb')
    frames = odb.steps['Modal'].frames
    freqs = [frames[i].frequency for i in range(1, len(frames))]
    odb.close()
    return freqs


lines = []
for (case, F, mu, a1, a2) in CASES:
    freqs = build_and_run(case, F, mu)
    if freqs is None:
        lines.append('%s  F=%.0f N  mu=%.1f  FAILED' % (case, F, mu))
    else:
        lines.append('%s  F=%.0f N  mu=%.1f  modes: %s   (Ansys f1 %.2f, f2 %.1f)' %
                     (case, F, mu, ', '.join('%.1f' % f for f in freqs), a1, a2))
    print(lines[-1])

print('==== SUMMARY ====')
for ln in lines:
    print(ln)
f = open('step2_results.txt', 'w')
f.write('\n'.join(lines) + '\n')
f.close()
