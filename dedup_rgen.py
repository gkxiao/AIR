#!/usr/bin/env python

import argparse, os, sys, textwrap

# rdkit optional: canonical-SMILES comparison (correct for aromatic/stereo/isotope
# variants); falls back to raw-string comparison when unavailable
try:
    from rdkit import Chem
    _RDKIT = True
except Exception:
    _RDKIT = False


def canon(smi):
    if _RDKIT:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None
        for a in mol.GetAtoms():
            a.SetAtomMapNum(0)
        return Chem.MolToSmiles(mol)
    return smi.strip()


def load_known(files):
    known = {}
    for fp in files:
        if not fp or not os.path.isfile(fp):
            continue
        with open(fp, encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('!') or line.startswith('SMILES'):
                    continue
                c = line.split()
                if len(c) < 1:
                    continue
                k = canon(c[0])
                if k:
                    known[k] = fp
    return known


def load_gen(fp):
    rows = []
    n_bad = 0
    with open(fp, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('SMILES'):
                continue
            c = line.split()
            if len(c) < 3:
                n_bad += 1
                continue
            rows.append([c[0], c[1], c[2]])
    return rows, n_bad


def main():
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''\
        Remove from r_gen.smi any structure already present in the given
        reference database(s) (ref.smi and/or test.smi).

        Comparison uses canonical SMILES (rdkit) so that equivalent writings
        (aromatic/Kekule, stereo, isotope labels) are recognized as identical.'''))
    ap.add_argument('-in', dest='in_file', default='r_gen.smi',
                    help='path to r_gen.smi\ndefault: r_gen.smi')
    ap.add_argument('-ref', dest='ref', default='',
                    help='path to ref.smi (optional)')
    ap.add_argument('-test', dest='test', default='',
                    help='path to test.smi (optional)')
    ap.add_argument('-out', dest='out_file', default='r_gen_dedup.smi',
                    help='output path\ndefault: r_gen_dedup.smi')
    args = ap.parse_args()

    if not args.ref and not args.test:
        sys.exit('Error: provide at least one of -ref / -test')
    if not os.path.isfile(args.in_file):
        sys.exit('Error: input file not found: ' + args.in_file)

    db_files = [f for f in (args.ref, args.test) if f]
    known = load_known(db_files)
    gen, n_bad = load_gen(args.in_file)
    if not gen:
        sys.exit('No rows read from ' + args.in_file)

    keep = []
    n_db_dup = 0
    n_in_dup = 0
    seen = set()
    for smi, mean, std in gen:
        k = canon(smi)
        if k is None:
            keep.append([smi, mean, std])   # unparseable: keep as-is
            continue
        if k in known:
            n_db_dup += 1
            continue
        if k in seen:                        # internal duplicates
            n_in_dup += 1
            continue
        seen.add(k)
        keep.append([smi, mean, std])

    with open(args.out_file, 'w', newline='', encoding='utf-8') as f:
        for smi, mean, std in keep:
            f.write('%s %s %s\r\n' % (smi, mean, std))

    print('input            : %d rows from %s' % (len(gen), args.in_file))
    print('database         : %s (%d unique structures)'
          % (' + '.join(os.path.basename(f) for f in db_files), len(known)))
    print('removed vs db    : %d' % n_db_dup)
    print('removed internal : %d' % n_in_dup)
    print('output           : %d rows -> %s' % (len(keep), args.out_file))
    if not _RDKIT:
        print('note: rdkit not found, fell back to raw-string comparison')


if __name__ == '__main__':
    main()
