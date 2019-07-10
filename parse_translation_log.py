#!/usr/bin/env python
# encoding: utf-8
"""
@author: Wang Qiang
@contact: wangqiangneu@gmail.com
@file: parse_translation_log.py
@time: 2018/8/8 9:56
@desc: Read translation log, e.g. S-<id> source sequence ...
"""
import argparse
import re

def get_args():
    parser = argparse.ArgumentParser('Parse Translation Log')
    parser.add_argument('-i', '--input', required=True, help='translation log path')
    parser.add_argument('--tgt_lang', default=None, help='target language')
    parser.add_argument('--detoken', action='store_true', default='true', help='detoken translation hypothesis')
    args = parser.parse_args()
    if args.detoken:
        assert args.tgt_lang is not None, 'you want to detoken, so --tgt_lang must be set'
    return args

class Response(object):

    def __init__(self):
        self.id = 0
        self.src = ''
        self.ref = ''
        self.hypo = ''
        self.log_sum = 0.0
        self.word_log_prob = []
        self.align = []


def gen_response(f):
    while True:
        line = f.readline().strip()
        if len(line) == 0:
            break
        match = re.match('S-(\d+)\s(.+)', line)
        if match:
            response = Response()
            response.id = int(match.group(1))
            response.src = match.group(2)

            line = f.readline()
            match = re.match('T-(\d+)\s(.+)', line)
            assert match, 'not found T'
            assert response.id == int(match.group(1)), 'wrong sentence id at T'
            response.ref = match.group(2)

            line = f.readline()
            match = re.match('H-(\d+)\s(.+)', line)
            assert match, 'not found H'
            assert response.id == int(match.group(1)), 'wrong sentence id at H'
            response.log_sum, response.hypo = match.group(2).split('\t')

            line = f.readline()
            match = re.match('P-(\d+)\s(.+)', line)
            assert match, 'not found P'
            assert response.id == int(match.group(1)), 'wrong sentence id at P'
            response.word_log_prob = [float(p) for p in match.group(2).split(' ')]

            line = f.readline()
            match = re.match('A-(\d+)\s(.+)', line)
            assert match, 'not found A'
            assert response.id == int(match.group(1)), 'wrong sentence id at A'
            response.align = [int(a) for a in match.group(2).split(' ')]

            yield response


def main(args):

    with open(args.input, 'r', encoding='utf-8') as f:
        # (id, response)
        responses = [r for r in gen_response(f)]
        responses = sorted(responses, key=lambda x: x.id)

    with open(args.input + '.trans', 'w', encoding='utf-8') as f:
        md = None
        if args.detoken:
            try:
                from sacremoses import MosesDetokenizer
            except ImportError:
                raise ImportError('sacremoses is not installed. '
                                  'To install sacremoses, use pip install -U sacremoses')
            md = MosesDetokenizer(lang=args.tgt_lang)
        for r in responses:
            hypo = r.hypo
            if md is not None:
                hypo = md.detokenize(r.hypo.split(), return_str=True)
            print(hypo, file=f)


if __name__ == "__main__":
    args = get_args()
    main(args)

