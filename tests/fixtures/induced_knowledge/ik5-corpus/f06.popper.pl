wrong(A):- f_order_by(A,B,C),aggregate_all(count,f_order_amount(A,B,D),N),N > 1.
