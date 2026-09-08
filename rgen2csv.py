#!/usr/bin/env python

import argparse, csv, os, sys

def rgen2csv(in_file, out_file):
    if not os.path.isfile(in_file):
        sys.exit('Error: input file not found: ' + in_file)
    if not out_file:
        out_file = os.path.splitext(in_file)[0] + '.csv'

    rows, n_skip = [], 0
    with open(in_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('SMILES'):
                continue
            cells = line.split()
            if len(cells) < 3:
                n_skip += 1
                continue
            rows.append([cells[0], cells[1], cells[2]])

    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['SMILES', 'mean_pred_pic50', 'std'])
        w.writerows(rows)

    print('Done: %d rows written to %s (skipped %d malformed lines)'
          % (len(rows), out_file, n_skip))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert three-column r_gen.smi (SMILES mean std) to r_gen.csv\n'
                    'with header: SMILES,mean_pred_pic50,std')
    parser.add_argument('-in', dest='in_file', default='r_gen.smi',
                        help='path to the input r_gen.smi\ndefault: r_gen.smi')
    parser.add_argument('-out', dest='out_file', default='',
                        help='path to the output csv\ndefault: <input basename>.csv')
    args = parser.parse_args()
    rgen2csv(args.in_file, args.out_file)
