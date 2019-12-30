import os
from math import isclose
from copy import deepcopy
orig_filename = 'Mesh2_OnlyQua.obj'
gen_filename = 'Mesh2_OnlyQua_finished_3.obj'
out_filename = 'out.obj'
directory =  r'\\DATACHEWER\shareZ\2019_12_27_FinalLadaMesh\FinalMesh2_OnlyQuad'
orig_fullpath = os.path.join(directory, orig_filename)
gen_fullpath = os.path.join(directory, gen_filename)
out_fullpath = os.path.join(directory, out_filename)


orig_vertices = []
orig_faces = []

with open (orig_fullpath, "r") as f:
    for line in f:
        cline = line.strip().split()
        if cline[0] == 'v':
            numlist = [float(i) for i in cline[1::]]
            orig_vertices.append(numlist)
        elif cline[0] == 'f':
            numlist = [int(i)-1 for i in cline[1::]]
            orig_faces.append(numlist)


gen_vertices = []
gen_faces = []
gen_faces_out = []
with open (gen_fullpath, "r") as f:
    for line in f:
        cline = line.strip().split()
        if cline[0] == 'v':
            numlist = [float(i) for i in cline[1::]]
            gen_vertices.append(numlist)
        elif cline[0] == 'f':
            numlist = [int(i)-1 for i in cline[1::]]
            gen_faces.append(numlist)

    empty69 = [[0.0, 0.0, -1.0]] * 69
    gen_vertices[1418:1418] = empty69
    for face in gen_faces:
        for id in range(len(face)):
            if face[id] > 1417:
                face[id] = face[id] + 69

    gen_faces_out = deepcopy(gen_faces)

for v in range(len(orig_vertices)):
    if orig_vertices[v][0] == 0.0 and orig_vertices[v][1] == 0.0 and orig_vertices[v][2] == -1.0:
        print("-1 lii")
        continue
    for v2 in range(len(gen_vertices)):
        if isclose(orig_vertices[v][0], gen_vertices[v2][0], abs_tol = 0.001) and isclose(orig_vertices[v][1], gen_vertices[v2][1], abs_tol = 0.001) and isclose(orig_vertices[v][2], gen_vertices[v2][2], abs_tol = 0.001):
            print("girdi")
            for f in range(len(gen_faces)):
                for id in range(len(gen_faces[f])):
                    if gen_faces[f][id] == v2:
                        gen_faces_out[f][id] = v
                        break
            break




for v in range(len(orig_vertices)):
    gen_vertices[v] = orig_vertices[v]


with open(out_fullpath, 'a') as f:

    for v in gen_vertices:
        line = "v " + str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + '\n'
        f.write(line)


    for face in gen_faces_out:
        line = "f "
        for id in face:
            line = line + str(id+1) + " "
        line = line + '\n'

        f.write(line)

