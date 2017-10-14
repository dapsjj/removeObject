#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random


class Generator:
    def __init__( self, back, body, noise, size, ratio ):
        self.back = back
        self.body = body
        self.size = size
        self.ratio = ratio

        self.data = [0 for i in range( size )]
        for i in range( self.size ):
            if i < (size * ratio):
                offset = back
            else:
                offset = body
            self.data[i] = int( offset + noise * ( 0.5 - random.random() ) )

    def get_data( self ):
        return self.data

    def print_data( self ):
        for i in range( self.size ):
            print( self.data[i] )


class HistMaxLib:
    def calc_max( hist_arr_src0 ):
        hist_max_value = 0
        hist_max_idx = -1
        for i in range( len( hist_arr_src0 ) ):
            hist_val = hist_arr_src0[i]
            if hist_max_value < hist_val:
                hist_max_value = hist_val
                hist_max_idx = i
        return hist_max_value, hist_max_idx

    def calc_ave( hist_arr_src0, hist_arr_dst0, tap0 ):
        hist_arr_length = len( hist_arr_src0 )
        half = int( tap0 / 2 )

        for i in range( hist_arr_length ):
            sum = hist_arr_src0[i]
            cnt = 1
            for j in range( tap0 ):
                idx = i + j - half
                if idx < 0:
                    src_data = 0
                elif idx < hist_arr_length:
                    src_data = hist_arr_src0[idx]
                else:
                    src_data = 0
                sum += src_data
                cnt += 1
            hist_arr_dst0[i] = sum / cnt

    def calc_mask( hist_arr_dst0, hist_max_idx0, win0 ):
        mask_lower_idx = hist_max_idx0 - win0
        mask_upper_idx = hist_max_idx0 + win0 + 1
        hist_arr_length = len( hist_arr_dst0 )
        if mask_lower_idx < 0:
            mask_lower_idx = 0
        if mask_upper_idx > hist_arr_length:
            mask_upper_idx = hist_arr_length
        for i in range( hist_arr_length ):
            if i < mask_lower_idx:
                hist_arr_dst0[i] = 0
            elif i < mask_upper_idx:
                hist_arr_dst0[i] = 1
            else:
                hist_arr_dst0[i] = 0

    def calc_mul( hist_arr_src0, hist_arr_src1, hist_arr_dst0 ):
        for i in range( len( hist_arr_src0 ) ):
            hist_arr_dst0[i] = hist_arr_src0[i] * hist_arr_src1[i]

    def print_hist( hist_arr0, hist_name0 ):
        print( 'index\t'+ hist_name0 )
        for i in range( len( hist_arr0 ) ):
            print( str( i ) + '\t' + str( hist_arr0[i] ) )


class HistMaxBody:
    def __init__( self, pix_arr, pix_arr_length, pix_min, hist_arr_length ):
        self.pix_arr = pix_arr
        self.pix_arr_length = pix_arr_length
        self.pix_min = pix_min
        self.hist_arr_length = hist_arr_length

        self.hist0_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist1_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist2_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist3_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist4_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist5_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.tap0 = 5
        self.tap1 = 9
        self.tap2 = 21
        self.win0 = 20

        self.hist0_max_value = 0
        self.hist0_max_idx = -1
        self.hist1_max_value = 0
        self.hist1_max_idx = -1
        self.hist2_max_value = 0
        self.hist2_max_idx = -1
        self.hist3_max_value = 0
        self.hist3_max_idx = -1
        self.hist4_max_value = 0
        self.hist4_max_idx = -1

        self.clip_data()

    def clip_data( self ):
        for i in range( self.pix_arr_length ):
            pix_val = self.pix_arr[i]
            self.pix_arr[i] = pix_val - self.pix_min
            if pix_val < 0:
                self.pix_arr[i] = 0
            if self.hist_arr_length <= pix_val:
                self.pix_arr[i] = self.hist_arr_length - 1

    def calc_hist( self ):
        for i in range( self.pix_arr_length ):
            idx = int( self.pix_arr[i] )
            self.hist0_arr[idx] += 1

    def get_dst_pix( self ):
        return self.hist4_max_idx + self.pix_min

    def dump( self ):
        HistMaxLib.print_hist( self.hist0_arr, 'hist0' )
        HistMaxLib.print_hist( self.hist1_arr, 'hist1' )
        HistMaxLib.print_hist( self.hist2_arr, 'hist2' )
        HistMaxLib.print_hist( self.hist3_arr, 'hist3' )
        HistMaxLib.print_hist( self.hist4_arr, 'hist4' )
        HistMaxLib.print_hist( self.hist5_arr, 'hist5' )

        print( 'hist0_max_value\t' + str( self.hist0_max_value ) )
        print( 'hist0_max_idx\t' + str( self.hist0_max_idx ) )

        print( 'hist1_max_value\t' + str( self.hist1_max_value ) )
        print( 'hist1_max_idx\t' + str( self.hist1_max_idx ) )

        print( 'hist2_max_value\t' + str( self.hist2_max_value ) )
        print( 'hist2_max_idx\t' + str( self.hist2_max_idx ) )

        print( 'hist3_max_value\t' + str( self.hist3_max_value ) )
        print( 'hist3_max_idx\t' + str( self.hist3_max_idx ) )

        print( 'hist4_max_value\t' + str( self.hist4_max_value ) )
        print( 'hist4_max_idx\t' + str( self.hist4_max_idx ) )

        print( 'dst_pix\t', str( self.get_dst_pix() ) )

    def calc_hist_max( self ):

        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist1_arr, tap0 = self.tap0 )
        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist2_arr, tap0 = self.tap1 )
        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist3_arr, tap0 = self.tap2 )

        self.hist0_max_value, self.hist0_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist0_arr )
        self.hist1_max_value, self.hist1_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist1_arr )
        self.hist2_max_value, self.hist2_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist2_arr )
        self.hist3_max_value, self.hist3_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist3_arr )

        HistMaxLib.calc_mask( hist_arr_dst0 = self.hist4_arr, hist_max_idx0 = self.hist3_max_idx, win0 = self.win0 )

        HistMaxLib.calc_mul(  hist_arr_src0 = self.hist2_arr, hist_arr_src1 = self.hist4_arr, hist_arr_dst0 = self.hist5_arr )

        self.hist4_max_value, self.hist4_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist5_arr )


if __name__ == '__main__':
    argvs = sys.argv
    argc  = len( argvs )
    if argc == 2:
        mode = int( argvs[1] )
    else:
        mode = 0

    mode = 9
    print( 'mode\t' + str( mode ) )
    if mode == 1:
        back, body, noise, size, ratio = 185, 50, 10, 100, 0.8
    elif mode == 2:
        back, body, noise, size, ratio = 100, 200, 10, 100, 0.8
    elif mode == 3:
        back, body, noise, size, ratio = 100, 200, 10, 100, 0.2
    elif mode == 4:
        back, body, noise, size, ratio = 0, 255, 10, 100, 0.8
    elif mode == 5:
        back, body, noise, size, ratio = 0, 255, 10, 100, 0.2
    elif mode == 6:
        back, body, noise, size, ratio = 120, 130, 20, 100, 0.8
    elif mode == 7:
        back, body, noise, size, ratio = 120, 130, 20, 100, 0.2
    elif mode == 8:
        back, body, noise, size, ratio = 255, 0, 0, 100, 1.0
    elif mode == 9:
        back, body, noise, size, ratio = 128, 0, 0, 100, 1
    elif mode == 10:
        back, body, noise, size, ratio = 0, 0, 0, 100, 1
    else:
        back, body, noise, size, ratio = 185, 50, 0, 100, 0.8

    gen = Generator( back, body, noise, size, ratio )
    print( 'data' )
    gen.print_data()
    pix_arr = gen.get_data()

    hmax = HistMaxBody( pix_arr, size, 0, 256 )
    hmax.calc_hist()
    hmax.calc_hist_max()
    hmax.dump()

