"""
Load scraped product items into DataFrame, write review urls into N text files.

Run example:
    $ python split_review_urls.py \
        --scraped-products $(pwd)/../output/products_.jl \
        --output-dir $(pwd)/../output
"""
import argparse
import json
import math
import os
from random import shuffle

import numpy as np
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--scraped-products',
        help='Path to scraped products.jl file.',
    )
    parser.add_argument(
        '--output-dir',
        help='Directory in which to place url part files.'
    )
    parser.add_argument(
        '--pieces',
        help='Number of URL files to produce.',
        default=10
    )
    return parser.parse_args()


def main():
    args = parse_args()

    with open(args.scraped_products) as f:
        rows = [json.loads(l) for l in f]

    df = pd.DataFrame(rows)

    # Filter out URLs for products that lack basic data or have no reviews.
    blx_nontrivial = np.all(df[['id', 'reviews_url', 'title']].notnull(), axis=1)
    blx_has_reviews = df['n_reviews'] > 0
    blx = blx_nontrivial & blx_has_reviews

    urls = df.loc[blx, 'reviews_url'].unique()
    urls = shuffle(urls)

    n = len(urls)
    step = int(math.ceil(float(n)/args.pieces))

    for n_part, bound in enumerate(range(0, n, step), start=1):
        file_name = os.path.join(
            args.output_dir,
            'review_urls_{:02d}.txt'.format(n_part)
        )

        with open(file_name, 'w') as f:
            piece = urls[bound:bound + step]
            f.write('\n'.join(piece))

    n_items = int(df.loc[blx, 'n_reviews'].sum())
    print("There are <={0} reviews to be scraped.".format(n_items))

if __name__ == "__main__":
    main()