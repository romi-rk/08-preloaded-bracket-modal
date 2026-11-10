# Step 4: slip onset check. Same nonlinear shock model as step 3, lower shock levels.
# Hand estimate: slip starts near 17 to 25 g at 3 kN per bolt and near 3 g at 0.5 kN per bolt.
# A final joint U3 near zero means no permanent slip; a clearly nonzero value means the joint slipped.
# Units: mm, tonne, N, s, MPa.  Run in Abaqus/CAE: File > Run Script (set a work directory first).
# Axes: x along the length, y thickness (vertical), z across the width (lateral).
# The base shock is applied as a time varying acceleration (gravity load with an amplitude curve) on the
# model with a fixed base. The results are therefore motions relative to the base.
# Shock direction here is lateral (z), the direction where friction at the joint carries the load.
import math
from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh, regionToolset

L_TOT, T, W = 140.0, 6.0, 40.0
L_CLAMP = 40.0
HEAD_AREA = 100.0
BOLT_X = (10.0, 30.0)
ZC = W / 2.0
G = 9806.65                       # mm/s2
ALPHA = 19.96                     # Rayleigh mass damping: 2 percent at 79.4 Hz
PULSE = 0.005                     # s, half sine duration
T_END = 0.030                     # s, total shock step time

# (case, joint, preload per bolt N, mu, shock level in g)
CASES = [('O10', 'contact', 3000.0, 0.2, 10.0),
         ('O20', 'contact', 3000.0, 0.2, 20.0),
         ('O30', 'contact', 3000.0, 0.2, 30.0),
         ('O40', 'contact', 3000.0, 0.2, 40.0),
         ('L2', 'contact', 500.0, 0.2, 2.0),
         ('L4', 'contact', 500.0, 0.2, 4.0),
         ('L8', 'contact', 500.0, 0.2, 8.0)]


def yedges_of(p):
    out = []
    for e in p.edges:
        v = e.getVertices()
        c0 = p.vertices[v[0]].pointOn[0]
        c1 = p.vertices[v[1]].pointOn[0]
        if abs(c0[0] - c1[0]) < 1e-6 and abs(c0[2] - c1[2]) < 1e-6:
            out.append(e)
    return tuple(out)


def run_case(case, joint, F, mu, glevel):
    m = mdb.Model(name=case)
    mat = m.Material(name='Aluminium')
    mat.Elastic(table=((71000.0, 0.33),))
    mat.Density(table=((2.77e-9,),))
    mat.Damping(alpha=ALPHA)
    m.HomogeneousSolidSection(name='Sec', material='Aluminium', thickness=None)
    brick = mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD)

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
    p.SectionAssignment(region=regionToolset.Region(cells=p.cells), sectionName='Sec')
    p.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
    p.seedEdgeByNumber(edges=yedges_of(p), number=2, constraint=FIXED)
    p.setMeshControls(regions=p.cells, elemShape=HEX, technique=STRUCTURED)
    p.setElementType(regions=(p.cells,), elemTypes=(brick,))
    p.generateMesh()

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
    print('%s: NODES %d (limit 1000)' % (case, nodes))
    if nodes > 1000:
        return None

    a = m.rootAssembly
    inst = a.Instance(name='Bracket1', part=p, dependent=ON)
    bi = a.Instance(name='Block1', part=b, dependent=ON)
    a.translate(instanceList=('Block1',), vector=(0.0, 0.0, -10.0))

    rp = a.ReferencePoint(point=(L_TOT, T / 2, ZC))
    a.Set(referencePoints=(a.referencePoints[rp.id],), name='RP_tip')
    a.engineeringFeatures.PointMassInertia(name='TipMass', region=a.sets['RP_tip'], mass=5.0e-4, alpha=0.0, composite=0.0)
    a.Surface(side1Faces=inst.faces.findAt(((L_TOT, T / 2, ZC),)), name='EndFace')
    m.Coupling(name='TipCoupling', controlPoint=a.sets['RP_tip'], surface=a.surfaces['EndFace'],
               influenceRadius=WHOLE_SURFACE, couplingType=DISTRIBUTING, weightingMethod=UNIFORM,
               localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

    a.Set(faces=bi.faces.getByBoundingBox(xMin=-11.0, xMax=41.0, yMin=-10.01, yMax=-9.99, zMin=-11.0, zMax=51.0), name='BlockBottom')
    m.EncastreBC(name='FixBlock', createStepName='Initial', region=a.sets['BlockBottom'])
    a.Surface(side1Faces=bi.faces.getByBoundingBox(xMin=-11.0, xMax=41.0, yMin=-0.01, yMax=0.01, zMin=-11.0, zMax=51.0), name='BlockTop')
    a.Surface(side1Faces=inst.faces.getByBoundingBox(xMin=-1.0, xMax=L_CLAMP + 1.0, yMin=-0.01, yMax=0.01, zMin=-1.0, zMax=W + 1.0), name='BracketBottom')

    if joint == 'tie':
        m.Tie(name='TieJoint', main=a.surfaces['BlockTop'], secondary=a.surfaces['BracketBottom'],
              adjust=OFF, positionToleranceMethod=COMPUTED, tieRotations=ON, thickness=ON)
        m.FrequencyStep(name='Modal', previous='Initial', numEigen=6, eigensolver=LANCZOS)
    else:
        cp = m.ContactProperty('Fric')
        cp.TangentialBehavior(formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF,
                              pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((mu,),),
                              shearStressLimit=None, maximumElasticSlip=FRACTION, fraction=0.005, elasticSlipStiffness=None)
        cp.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
        m.SurfaceToSurfaceContactStd(name='Joint', createStepName='Initial', main=a.surfaces['BlockTop'],
                                     secondary=a.surfaces['BracketBottom'], sliding=FINITE, thickness=ON,
                                     interactionProperty='Fric', adjustMethod=NONE, initialClearance=OMIT,
                                     datumAxis=None, clearanceRegion=None)
        m.StaticStep(name='Preload', previous='Initial', initialInc=0.1, minInc=1e-6, maxInc=1.0,
                     stabilizationMagnitude=2e-4, stabilizationMethod=DISSIPATED_ENERGY_FRACTION)
        for i, xb in enumerate(BOLT_X):
            name = 'Head%d' % (i + 1)
            a.Surface(side1Faces=inst.faces.getByBoundingBox(xMin=xb - 5.1, xMax=xb + 5.1, yMin=T - 0.1, yMax=T + 0.1,
                                                              zMin=ZC - 5.1, zMax=ZC + 5.1), name=name)
            m.Pressure(name=name, createStepName='Preload', region=a.surfaces[name], distributionType=UNIFORM,
                       field='', magnitude=F / HEAD_AREA, amplitude=UNSET)
        # half sine base shock in z, 5 ms, then free decay
        npts = int(round(PULSE / 1e-4))
        data = [(0.0, 0.0)]
        for k in range(1, npts + 1):
            t = k * 1e-4
            data.append((t, math.sin(math.pi * t / PULSE)))
        data.append((T_END, 0.0))
        m.TabularAmplitude(name='HalfSine', timeSpan=STEP, data=tuple(data))
        m.ImplicitDynamicsStep(name='Shock', previous='Preload', timePeriod=T_END, maxNumInc=3000,
                               initialInc=1e-4, minInc=1e-9, maxInc=1e-4, application=MODERATE_DISSIPATION, nlgeom=ON)
        m.Gravity(name='Shake', createStepName='Shock', comp3=-G * glevel, amplitude='HalfSine',
                  distributionType=UNIFORM, field='')
        a.Set(nodes=inst.nodes.getByBoundingSphere(center=(20.0, 0.0, ZC), radius=0.5), name='SlipNode')
        m.HistoryOutputRequest(name='HTip', createStepName='Shock', region=a.sets['RP_tip'], variables=('U3', 'A3'),
                               timeInterval=1e-4)
        m.HistoryOutputRequest(name='HSlip', createStepName='Shock', region=a.sets['SlipNode'], variables=('U3',),
                               timeInterval=1e-4)

    job = mdb.Job(name='Step4_' + case, model=case)
    job.submit(consistencyChecking=OFF)
    job.waitForCompletion()
    if job.status != COMPLETED:
        print('%s: job did not complete, see %s.msg and %s.sta in the work directory' % (case, job.name, job.name))
        return None
    odb = session.openOdb(name=job.name + '.odb')
    if joint == 'tie':
        frames = odb.steps['Modal'].frames
        res = 'modes: ' + ', '.join('%.1f' % frames[i].frequency for i in range(1, len(frames)))
    else:
        tip = None
        slip = None
        for hr in odb.steps['Shock'].historyRegions.values():
            if 'A3' in hr.historyOutputs.keys():
                tip = hr
            elif 'U3' in hr.historyOutputs.keys():
                slip = hr
        tu = [d[1] for d in tip.historyOutputs['U3'].data]
        ta = [d[1] for d in tip.historyOutputs['A3'].data]
        su = [d[1] for d in slip.historyOutputs['U3'].data]
        res = ('peak tip U3 %.3f mm, peak tip accel %.0f g, peak joint U3 %.4f mm, final joint U3 %.4f mm' %
               (max(abs(v) for v in tu), max(abs(v) for v in ta) / G, max(abs(v) for v in su), su[-1]))
    odb.close()
    return res


lines = []
for (case, joint, F, mu, gl) in CASES:
    r = run_case(case, joint, F, mu, gl)
    if r is None:
        r = 'FAILED'
    line = '%s  joint=%s  F=%.0f N  mu=%.1f  shock=%.0f g  %s' % (case, joint, F, mu, gl, r)
    lines.append(line)
    print(line)

print('==== SUMMARY ====')
for ln in lines:
    print(ln)
f = open('step4_results.txt', 'w')
f.write('\n'.join(lines) + '\n')
f.close()
