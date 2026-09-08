#!/usr/bin/env python

import argparse, csv, os, sys, textwrap

def smi2csv(in_file, out_file, prefix, start, pad):
    if not os.path.isfile(in_file):
        sys.exit('Error: input file not found: ' + in_file)

    if not out_file:
        out_file = os.path.splitext(in_file)[0] + '.csv'

    rows = []
    n_keep = 0
    n_skip = 0

    with open(in_file, 'r', newline='', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # skip table headers / comment lines
            if line.startswith('SMILES') or line.startswith('#'):
                continue
            cells = line.split()
            if len(cells) < 2:
                n_skip += 1
                continue

            smi = cells[0]
            pic50 = cells[1]

            # sequential index: first kept compound gets start, then start+1 ...
            idx = n_keep + start
            title = '%s_%0*d' % (prefix, pad, idx) if pad and pad > 0 else '%s_%d' % (prefix, idx)

            rows.append([smi, title, pic50])
            n_keep += 1

    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['SMILES', 'Title', 'pIC50'])
        w.writerows(rows)

    print('Done: %d compounds written to %s (skipped %d malformed lines)'
          % (n_keep, out_file, n_skip))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent('''\
        Convert a two-column .smi file (SMILES + pIC50) to a three-column CSV:
            SMILES, Title, pIC50
        Title is built from a user prefix and a sequential index, e.g.
        -prefix Cpd -> Cpd_1, Cpd_2, ...'''))
    parser.add_argument('-in', dest='in_file', default='ref.smi',
                        help='path to the input .smi file\ndefault: ref.smi')
    parser.add_argument('-out', dest='out_file', default='',
                        help='path to the output .csv file\ndefault: <input basename>.csv')
    parser.add_argument('-prefix', dest='prefix', default='Cpd',
                        help='prefix of the compound Title\ndefault: Cpd')
    parser.add_argument('-start', dest='start', type=int, default=1,
                        help='index of the first compound\ndefault: 1')
    parser.add_argument('-pad', dest='pad', type=int, default=0,
                        help='zero-padding width of the index, e.g. 3 -> Cpd_001\ndefault: 0 (no padding)')

    arg_dict = vars(parser.parse_args())
    smi2csv(**arg_dict)
