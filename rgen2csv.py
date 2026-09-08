#!/usr/bin/env python

import argparse, csv, os, sys

def rgen2csv(in_file, out_file, prefix, start, pad):
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

    with_title = bool(prefix)
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if with_title:
            w.writerow(['SMILES', 'Title', 'mean_pred_pic50', 'std'])
            for i, r in enumerate(rows):
                n = i + start
                title = '%s_%0*d' % (prefix, pad, n) if pad and pad > 0 else '%s_%d' % (prefix, n)
                w.writerow([r[0], title, r[1], r[2]])
        else:
            w.writerow(['SMILES', 'mean_pred_pic50', 'std'])
            w.writerows(rows)

    print('Done: %d rows written to %s (skipped %d malformed lines)'
          % (len(rows), out_file, n_skip))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Convert three-column r_gen.smi (SMILES mean std) to a CSV.\n'
                    'Without -prefix : SMILES,mean_pred_pic50,std\n'
                    'With    -prefix : SMILES,Title,mean_pred_pic50,std\n'
                    '                  (Title = {prefix}_{n}, e.g. FW_1, FW_2 ...)')
    parser.add_argument('-in', dest='in_file', default='r_gen.smi',
                        help='path to the input r_gen.smi\ndefault: r_gen.smi')
    parser.add_argument('-out', dest='out_file', default='',
                        help='path to the output csv\ndefault: <input basename>.csv')
    parser.add_argument('-prefix', dest='prefix', default='',
                        help='prefix of the compound Title; omit to keep 3 columns')
    parser.add_argument('-start', dest='start', type=int, default=1,
                        help='index of the first compound\ndefault: 1')
    parser.add_argument('-pad', dest='pad', type=int, default=0,
                        help='zero-padding width of the index, e.g. 3 -> FW_001\ndefault: 0 (no padding)')
    args = parser.parse_args()
    rgen2csv(args.in_file, args.out_file, args.prefix, args.start, args.pad)
