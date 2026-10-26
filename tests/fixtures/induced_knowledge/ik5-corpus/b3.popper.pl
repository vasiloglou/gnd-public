wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,100).
wrong(A):- f_order_amount(A,B,C),f_order_flagged(A,B).
wrong(A):- f_order_amount(A,B,C),gt_t_amount(C,80).
