#!/usr/bin/env python

import os
import ctypes
import numpy

_cint = numpy.ctypeslib.load_library('libcint', os.path.abspath(os.path.join(__file__, '../../build')))
#_cint4 = ctypes.cdll.LoadLibrary('libcint.so.4')

from pyscf import gto, lib

mol = gto.M(atom='H 0 0 0; H .2 .5 .8; H 1.9 2.1 .1; H 2.0 .3 1.4',
            basis = {'H': gto.basis.parse('''
H    S
   1990.8000000              1.0000000
H    S
     80.8000000              0.0210870             -0.0045400              0.0000000     0.0000000
      3.3190000              0.3461290             -0.1703520              1.0000000     0.0000000
      0.9059000              0.0393780              0.1403820              0.0000000     1.0000000
H    P
      4.1330000              0.0868660#              0.0000000
      1.2000000              0.0000000#              0.5000000
      0.3827000              0.5010080#              1.0000000
H    D
      1.0970000              1.0000000
H    D
      2.1330000              0.1868660              0.0000000
      0.3827000              0.2010080              1.0000000
H    F
      0.7610000              1.0000000        
H    F
      1.1330000              0.3868660              1.0000000
      0.8827000              0.4010080              0.0000000
H    g
      1.1330000              0.3868660              0.0000000
      0.8827000              0.4010080              1.0000000
      ''')})

def make_cintopt(atm, bas, env, intor):
    c_atm = numpy.asarray(atm, dtype=numpy.int32, order='C')
    c_bas = numpy.asarray(bas, dtype=numpy.int32, order='C')
    c_env = numpy.asarray(env, dtype=numpy.double, order='C')
    natm = c_atm.shape[0]
    nbas = c_bas.shape[0]
    cintopt = lib.c_null_ptr()
    foptinit = getattr(_cint, intor+'_optimizer')
    foptinit(ctypes.byref(cintopt),
             c_atm.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(natm),
             c_bas.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(nbas),
             c_env.ctypes.data_as(ctypes.c_void_p))
    return cintopt

def run(intor, comp=1, suffix='_sph', thr=1e-9):
    if suffix == '_spinor':
        intor = intor = 'c%s'%intor
    else:
        intor = intor = 'c%s%s'%(intor,suffix)
    print(intor)
    fn1 = getattr(_cint, intor)
    #fn2 = getattr(_cint4, intor)
    #cintopt = make_cintopt(mol._atm, mol._bas, mol._env, intor)
    cintopt = lib.c_null_ptr()
    args = (mol._atm.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.natm),
            mol._bas.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.nbas),
            mol._env.ctypes.data_as(ctypes.c_void_p), cintopt)
    for i in range(mol.nbas):
        for j in range(mol.nbas):
            ref = mol.intor_by_shell(intor, [i,j], comp=comp)
            #fn2(ref.ctypes.data_as(ctypes.c_void_p),
            #   (ctypes.c_int*2)(i,j),
            #    mol._atm.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.natm),
            #    mol._bas.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.nbas),
            #    mol._env.ctypes.data_as(ctypes.c_void_p), lib.c_null_ptr())
            buf = numpy.empty_like(ref)
            fn1(buf.ctypes.data_as(ctypes.c_void_p),
               (ctypes.c_int*2)(i,j),
                mol._atm.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.natm),
                mol._bas.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(mol.nbas),
                mol._env.ctypes.data_as(ctypes.c_void_p))
            if numpy.linalg.norm(ref-buf) > thr:
                print(intor, '| nopt', i, j, numpy.linalg.norm(ref-buf))#, ref, buf
            #fn(buf.ctypes.data_as(ctypes.c_void_p),
            #   (ctypes.c_int*2)(i,j), *args)
            #if numpy.linalg.norm(ref-buf) > 1e-7:
            #    print('|', i, j, numpy.linalg.norm(ref-buf))

run('int1e_ovlp')
run('int1e_nuc')
run("int1e_ia01p"         , 3)
run("int1e_giao_irjxp"    , 3)
run("int1e_cg_irxp"       , 3)
run("int1e_giao_a11part"  , 9)
run("int1e_cg_a11part"    , 9)
run("int1e_a01gp"         , 9)
run("int1e_igkin"         , 3)
run("int1e_igovlp"        , 3)
run("int1e_ignuc"         , 3)
run("int1e_pnucp"         )
run("int1e_z"             )
run("int1e_zz"            )
run("int1e_r"             , 3)
run("int1e_r2"            )
run("int1e_rr"            , 9)
run("int1e_z_origj"       )
run("int1e_zz_origj"      )
run("int1e_r_origj"       , 3)
run("int1e_rr_origj"      , 9)
run("int1e_r2_origj"      )
run("int1e_r4_origj"      )
run("int1e_r2_origi"      )
run("int1e_r4_origi"      )
run("int1e_p4"            , thr=1e-8)
run("int1e_prinvxp"       , 3)
run("int1e_pnucxp"        , 3)
run("int1e_ipovlp"        , 3)
run("int1e_ipkin"         , 3)
run("int1e_ipnuc"         , 3)
run("int1e_iprinv"        , 3)
run("int1e_rinv"          )

run("int1e_srsr"          , suffix='_spinor')
run("int1e_sr"            , suffix='_spinor')
run("int1e_srsp"          , suffix='_spinor')
run("int1e_spsp"          , suffix='_spinor')
run("int1e_sp"            , suffix='_spinor')
run("int1e_spnucsp"       , suffix='_spinor')
run("int1e_srnucsr"       , suffix='_spinor')
run("int1e_govlp"         , 3, suffix='_spinor')
run("int1e_gnuc"          , 3, suffix='_spinor')
run("int1e_cg_sa10sa01"   , 9, suffix='_spinor')
run("int1e_cg_sa10sp"     , 3, suffix='_spinor')
run("int1e_cg_sa10nucsp"  , 3, suffix='_spinor')
run("int1e_giao_sa10sa01" , 9, suffix='_spinor')
run("int1e_giao_sa10sp"   , 3, suffix='_spinor')
run("int1e_giao_sa10nucsp", 3, suffix='_spinor')
run("int1e_sa01sp"        , 3, suffix='_spinor', thr=1e-8)
run("int1e_spgsp"         , 3, suffix='_spinor')
run("int1e_spgnucsp"      , 3, suffix='_spinor')
run("int1e_spgsa01"       , 9, suffix='_spinor')
run("int1e_ipspnucsp"     , 3, suffix='_spinor', thr=1e-8)
run("int1e_ipsprinvsp"    , 3, suffix='_spinor', thr=1e-8)
