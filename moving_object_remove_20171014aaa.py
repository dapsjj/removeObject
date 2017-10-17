#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import cv2
import random
import numpy as np


class Generator:
    def __init__( self, back, body, noise, size, ratio ):
        self.back = back
        self.body = body
        self.size = size
        self.ratio = ratio

        self.data = [ 0 for i in range( size ) ]
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


class GenerateYCC:
    def __init__( self, back_yy, body_yy, noise_yy, size_yy, ratio_yy, back_cr, body_cr, noise_cr, size_cr, ratio_cr, back_cb, body_cb, noise_cb, size_cb, ratio_cb ):
        self.gen_yy = Generator( back_yy, body_yy, noise_yy, size_yy, ratio_yy )
        self.gen_cr = Generator( back_cr, body_cr, noise_cr, size_cr, ratio_cr )
        self.gen_cb = Generator( back_cb, body_cb, noise_cb, size_cb, ratio_cb )

    def get_data_ycc( self ):
        return [self.gen_yy.get_data(), self.gen_cr.get_data(), self.gen_cb.get_data()]

    def print_data_ycc( self ):
        print( 'pix_arr_yy' )
        self.gen_yy.print_data()
        print( 'pix_arr_cr' )
        self.gen_cr.print_data()
        print( 'pix_arr_cb' )
        self.gen_cb.print_data()


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
        if hist_arr_length < mask_upper_idx:
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

    def hist2med( hist_arr_src0, hist_arr_dst0, pix_count0, hist_arr_length0 ):
        half = int( ( pix_count0 + 1 ) / 2 )
        sum = 0
        for i in range( hist_arr_length0 ):
            sum += hist_arr_src0[i]
            hist_arr_dst0[i] = sum
        val = 0
        idx = -1
        for i in range( hist_arr_length0 ):
            if half <= hist_arr_dst0[i]:
                val = hist_arr_dst0[i]
                idx = i
                break
        return [val, idx]

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

        self.hist0_max_val = 0
        self.hist0_max_idx = -1
        self.hist1_max_val = 0
        self.hist1_max_idx = -1
        self.hist2_max_val = 0
        self.hist2_max_idx = -1
        self.hist3_max_val = 0
        self.hist3_max_idx = -1
        self.hist4_max_val = 0
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

        print( 'hist0_max_value\t' + str( self.hist0_max_val ) )
        print( 'hist0_max_idx\t' + str( self.hist0_max_idx ) )

        print( 'hist1_max_value\t' + str( self.hist1_max_val ) )
        print( 'hist1_max_idx\t' + str( self.hist1_max_idx ) )

        print( 'hist2_max_value\t' + str( self.hist2_max_val ) )
        print( 'hist2_max_idx\t' + str( self.hist2_max_idx ) )

        print( 'hist3_max_value\t' + str( self.hist3_max_val ) )
        print( 'hist3_max_idx\t' + str( self.hist3_max_idx ) )

        print( 'hist4_max_value\t' + str( self.hist4_max_val ) )
        print( 'hist4_max_idx\t' + str( self.hist4_max_idx ) )

        print( 'dst_pix\t', str( self.get_dst_pix() ) )

    def calc_hist_max( self ):

        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist1_arr, tap0 = self.tap0 )
        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist2_arr, tap0 = self.tap1 )
        HistMaxLib.calc_ave( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist3_arr, tap0 = self.tap2 )

        self.hist0_max_val, self.hist0_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist0_arr )
        self.hist1_max_val, self.hist1_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist1_arr )
        self.hist2_max_val, self.hist2_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist2_arr )
        self.hist3_max_val, self.hist3_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist3_arr )

        HistMaxLib.calc_mask( hist_arr_dst0 = self.hist4_arr, hist_max_idx0 = self.hist3_max_idx, win0 = self.win0 )

        HistMaxLib.calc_mul(  hist_arr_src0 = self.hist2_arr, hist_arr_src1 = self.hist4_arr, hist_arr_dst0 = self.hist5_arr )

        self.hist4_max_val, self.hist4_max_idx = HistMaxLib.calc_max( hist_arr_src0 = self.hist5_arr )


class HistMaxBodyYCC:
    def __init__( self, pix_arr_yy, pix_arr_cr, pix_arr_cb, pix_arr_length, pix_min_yy, pix_min_cr, pix_min_cb, hist_arr_length ):
        self.hist_max_yy = HistMaxBody( pix_arr = pix_arr_yy, pix_arr_length = pix_arr_length, pix_min = pix_min_yy, hist_arr_length = hist_arr_length )
        self.hist_max_cr = HistMaxBody( pix_arr = pix_arr_cr, pix_arr_length = pix_arr_length, pix_min = pix_min_cr, hist_arr_length = hist_arr_length )
        self.hist_max_cb = HistMaxBody( pix_arr = pix_arr_cb, pix_arr_length = pix_arr_length, pix_min = pix_min_cb, hist_arr_length = hist_arr_length )

        self.dst_pix_yy = 0
        self.dst_pix_cr = 0
        self.dst_pix_cb = 0

    def calc_hist_ycc( self ):
        self.hist_max_yy.calc_hist()
        self.hist_max_cr.calc_hist()
        self.hist_max_cb.calc_hist()

    def calc_hist_max_ycc( self ):
        self.hist_max_yy.calc_hist_max()
        self.hist_max_cr.calc_hist_max()
        self.hist_max_cb.calc_hist_max()

        self.dst_pix_yy = self.hist_max_yy.get_dst_pix()
        self.dst_pix_cr = self.hist_max_cr.get_dst_pix()
        self.dst_pix_cb = self.hist_max_cb.get_dst_pix()

    def dump( self ):
        # self.hist_max_yy.dump()
        # self.hist_max_cb.dump()
        # self.hist_max_cr.dump()

        print( 'pix_arr_yy\t' + str( self.dst_pix_yy ) )
        print( 'pix_arr_cr\t' + str( self.dst_pix_cr ) )
        print( 'pix_arr_cb\t' + str( self.dst_pix_cb ) )


class MedianBody:
    def __init__( self, pix_arr, pix_arr_length, pix_min, hist_arr_length ):
        self.pix_arr = pix_arr
        self.pix_arr_length = pix_arr_length
        self.pix_min = pix_min
        self.hist_arr_length = hist_arr_length

        self.hist0_arr = [ 0 for i in range( self.hist_arr_length ) ]
        self.hist1_arr = [ 0 for i in range( self.hist_arr_length ) ]

        self.med0_val = 0
        self.med0_idx = 0

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
        return self.med0_idx + self.pix_min

    def dump( self ):
        HistMaxLib.print_hist( self.hist0_arr, 'hist0' )
        HistMaxLib.print_hist( self.hist1_arr, 'hist1' )

        print( 'med0_val\t' + str( self.med0_val ) )
        print( 'med0_idx\t' + str( self.med0_idx ) )

        print( 'dst_pix\t', str( self.get_dst_pix() ) )

    def calc_med( self ):
        self.med0_val, self.med0_idx = HistMaxLib.hist2med( hist_arr_src0 = self.hist0_arr, hist_arr_dst0 = self.hist1_arr, pix_count0 = self.pix_arr_length, hist_arr_length0 = self.hist_arr_length )


class ImgProcessLib:
    def cvt_BGR2YyCrCb( b, g, r, delta ):
        yy = 0.114 * b + 0.587 * g + 0.299 * r
        cr = (r - yy) * 0.713 + delta
        cb = (b - yy) * 0.564 + delta

        if yy < 0:
            yy = 0
        elif 255 < yy:
            yy = 255
        if cr < 0:
            cr = 0
        elif 255 < cr:
            cr = 255
        if cb < 0:
            cb = 0
        elif 255 < cb:
            cb = 255

        return [ int( yy + 0.5 ), int( cr + 0.5 ), int( cb + 0.5 ) ]

    def cvt_YyCrCb2BGR( yy, cr, cb, delta ):
        b = yy + 1.773 * (cb - delta)
        g = yy - 0.714 * (cr - delta) - 0.344 * (cb - delta)
        r = yy + 1.403 * (cr - delta)

        if b < 0:
            b = 0
        elif 255 < b:
            b = 255
        if g < 0:
            g = 0
        elif 255 < g:
            g = 255
        if r < 0:
            r = 0
        elif 255 < r:
            r = 255

        return [ int( b + 0.5 ), int( g + 0.5 ), int( r + 0.5 ) ]


class YccFromFile:
    def __init__( self, dirpath, outpath, row_num, col_num, dumpXY ):
        self.dirpath = dirpath
        self.img_num = 0
        self.row_num = row_num
        self.col_num = col_num
        self.outpath = outpath

        self.img_src = []
        self.img_dst = [ [ [0, 0, 0] for j in range( col_num ) ] for i in range( row_num ) ]

        self.dumpXY = dumpXY

    def read_img( self ):
        file_arr = os.listdir( self.dirpath )
        self.img_num = len( file_arr )
        self.img_src = [ 0 for i in range( self.img_num ) ]
        for i in range( self.img_num ):
            filepath = self.dirpath + file_arr[i]
            img = cv2.imread( filepath, 3 )
            self.img_src[i] = img

    def calc_img_dst( self ):
        pix_arr_yy = [ 0 for k in range( self.img_num ) ]
        pix_arr_cr = [ 0 for k in range( self.img_num ) ]
        pix_arr_cb = [ 0 for k in range( self.img_num ) ]
        for row in range( self.row_num ):
            for col in range( self.col_num ):
                for k in range( self.img_num ):
                    b = self.img_src[k][row][col][0]
                    g = self.img_src[k][row][col][1]
                    r = self.img_src[k][row][col][2]
                    yy, cr, cb = ImgProcessLib.cvt_BGR2YyCrCb( b, g, r, 128 )
                    pix_arr_yy[k] = yy
                    pix_arr_cr[k] = cr
                    pix_arr_cb[k] = cb
                hmax_ycc = HistMaxBodyYCC( pix_arr_yy, pix_arr_cr, pix_arr_cb, self.img_num, 0, 0, 0, 256 )
                hmax_ycc.calc_hist_ycc()
                hmax_ycc.calc_hist_max_ycc()

                if ( self.dumpXY[0] == row ) and ( self.dumpXY[1] == col ):
                    print( 'dumpXY\t' + str( self.dumpXY[0] ) + ',' + str( self.dumpXY[1] ) )

                    print( 'pix_arr_yy' )
                    for k in range( self.img_num ):
                        print( pix_arr_yy[k] )
                    print( 'pix_arr_cr' )
                    for k in range( self.img_num ):
                        print( pix_arr_cr[k] )
                    print( 'pix_arr_cb' )
                    for k in range( self.img_num ):
                        print( pix_arr_cb[k] )

                    hmax_ycc.dump()

                yy = hmax_ycc.dst_pix_yy
                cr = hmax_ycc.dst_pix_cr
                cb = hmax_ycc.dst_pix_cb
                b, g, r = ImgProcessLib.cvt_YyCrCb2BGR( yy, cr, cb, 128 )
                self.img_dst[row][col][0] = b
                self.img_dst[row][col][1] = g
                self.img_dst[row][col][2] = r

    def write_img( self ):
        img = np.array( self.img_dst, dtype = np.uint8 )
        cv2.imwrite( self.outpath, img )


if __name__ == '__main__':
    argvs = sys.argv
    argc  = len( argvs )

    if argc == 2:
        mode = argvs[1]
    else:
        mode = 1

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

    random.seed(10)
    gen = Generator( back, body, noise, size, ratio )
    print( 'data' )
    gen.print_data()
    pix_arr = gen.get_data()

    hmax_body = HistMaxBody( pix_arr, size, 0, 256 )
    hmax_body.calc_hist()
    hmax_body.calc_hist_max()
    hmax_body.dump()

    med_body = MedianBody( pix_arr, size, 0, 256 )
    med_body.calc_hist()
    med_body.calc_med()
    med_body.dump()


