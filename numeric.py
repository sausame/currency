#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Numeric:

    # Constants of Chinese links to Arabic
    CN_NUM = {
        u'〇' : 0, u'一' : 1, u'二' : 2, u'三' : 3, u'四' : 4, u'五' : 5, u'六' : 6, u'七' : 7, u'八' : 8, u'九' : 9, u'零' : 0,
        u'壹' : 1, u'贰' : 2, u'叁' : 3, u'肆' : 4, u'伍' : 5, u'陆' : 6, u'柒' : 7, u'捌' : 8, u'玖' : 9, u'貮' : 2, u'两' : 2,
    }

    CN_UNIT = {
        u'十' : 10,
        u'拾' : 10,
        u'百' : 100,
        u'佰' : 100,
        u'千' : 1000,
        u'仟' : 1000,
        u'万' : 10000,
        u'萬' : 10000,
        u'亿' : 100000000,
        u'億' : 100000000,
        u'兆' : 1000000000000,
    }

    @staticmethod
    def _chinese2arabic(cn):

        unit = 0   # current
        ldig = []  # digest

        count = 0

        for cndig in reversed(cn):

            if cndig in Numeric.CN_UNIT:

                unit = Numeric.CN_UNIT.get(cndig)

                if unit == 10000 or unit == 100000000:
                    ldig.append(unit)
                    unit = 1

            elif cndig in Numeric.CN_NUM:

                dig = Numeric.CN_NUM.get(cndig)

                if unit:
                    dig *= unit
                    unit = 0

                ldig.append(dig)

            else:
                break

            count += 1

        if unit == 10:
            ldig.append(10)

        if len(ldig) is 0:
            return None, count

        val, tmp = 0, 0

        for x in reversed(ldig):

            if x == 10000 or x == 100000000:

                val += tmp * x
                tmp = 0

            else:
                tmp += x

        val += tmp

        return val, count

    @staticmethod
    def chinese2arabic(cn):

        res = ''
        pos = len(cn)

        while pos >= 0:

            x, count = Numeric._chinese2arabic(cn[:pos])

            if x is not None:
                res = u'{}{}'.format(x, res)
                pos -= count
            else:
                pos -= 1

                if pos >= 0:
                    res = u'{}{}'.format(cn[pos], res)

        return res

