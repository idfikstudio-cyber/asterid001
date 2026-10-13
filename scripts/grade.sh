# usage: grade filter applied to [in] producing [out]; needs inputs keymask.png(1) vigmask.png(2) scaled to frame
GRADE_BASE="colorbalance=rs=-0.02:bs=0.03:rm=-0.01:bm=0.005:rh=0.01:bh=-0.01,curves=all='0/0.035 0.18/0.16 0.5/0.54 0.82/0.87 1/0.985',eq=brightness=0.025:contrast=1.05:saturation=1.12:gamma=1.05"
