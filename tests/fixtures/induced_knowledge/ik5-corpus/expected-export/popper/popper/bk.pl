f_customer_blocked('n2','c3').
f_customer_blocked('p2','c3').
f_customer_blocked('v1','c1').
f_order_amount('n1',1,50).
f_order_amount('n1',2,150).
f_order_amount('n2',3,200).
f_order_amount('n2',4,20).
f_order_amount('n3',8,10).
f_order_amount('p1',5,30).
f_order_amount('p1',6,90).
f_order_amount('p2',7,100).
f_order_by('n1',1,'c1').
f_order_by('n1',2,'c2').
f_order_by('n2',3,'c1').
f_order_by('n2',4,'c3').
f_order_by('n3',8,'c2').
f_order_by('p1',5,'c1').
f_order_by('p1',6,'c2').
f_order_by('p2',7,'c3').
f_order_flagged('n2',4).
f_order_flagged('n3',8).
gt_t_amount__10(A) :- integer(A), A > 10.
gt_t_amount__20(A) :- integer(A), A > 20.
gt_t_amount__30(A) :- integer(A), A > 30.
gt_t_amount__50(A) :- integer(A), A > 50.
gt_t_amount__90(A) :- integer(A), A > 90.
gt_t_amount__100(A) :- integer(A), A > 100.
gt_t_amount__150(A) :- integer(A), A > 150.
gt_t_amount__200(A) :- integer(A), A > 200.
lt_t_amount__10(A) :- integer(A), A < 10.
lt_t_amount__20(A) :- integer(A), A < 20.
lt_t_amount__30(A) :- integer(A), A < 30.
lt_t_amount__50(A) :- integer(A), A < 50.
lt_t_amount__90(A) :- integer(A), A < 90.
lt_t_amount__100(A) :- integer(A), A < 100.
lt_t_amount__150(A) :- integer(A), A < 150.
lt_t_amount__200(A) :- integer(A), A < 200.
