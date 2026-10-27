dom_t_amount(V) :- f_order_amount(_,V).
thr_t_amount(10).
thr_t_amount(20).
thr_t_amount(30).
thr_t_amount(50).
thr_t_amount(90).
thr_t_amount(100).
thr_t_amount(150).
thr_t_amount(200).
gt_t_amount(X, C) :- dom_t_amount(X), thr_t_amount(C), X > C.
lt_t_amount(X, C) :- dom_t_amount(X), thr_t_amount(C), X < C.

#constant(t_amount, 10).
#constant(t_amount, 20).
#constant(t_amount, 30).
#constant(t_amount, 50).
#constant(t_amount, 90).
#constant(t_amount, 100).
#constant(t_amount, 150).
#constant(t_amount, 200).

#modeh(wrong).
#modeb(2, f_customer_blocked(var(t_customer))).
#modeb(2, f_order_amount(var(t_order), var(t_amount))).
#modeb(2, f_order_by(var(t_order), var(t_customer))).
#modeb(2, f_order_flagged(var(t_order))).
#modeb(1, gt_t_amount(var(t_amount), const(t_amount))).
#modeb(1, lt_t_amount(var(t_amount), const(t_amount))).
#maxv(4).

#pos(e1, {wrong}, {}, {
f_order_amount(1,50).
f_order_amount(2,150).
f_order_by(1,"c1").
f_order_by(2,"c2").
}).

#pos(e2, {wrong}, {}, {
f_customer_blocked("c3").
f_order_amount(3,200).
f_order_amount(4,20).
f_order_by(3,"c1").
f_order_by(4,"c3").
f_order_flagged(4).
}).

#pos(e3, {wrong}, {}, {
f_order_amount(8,10).
f_order_by(8,"c2").
f_order_flagged(8).
}).

#neg(e4, {wrong}, {}, {
f_order_amount(5,30).
f_order_amount(6,90).
f_order_by(5,"c1").
f_order_by(6,"c2").
}).

#neg(e5, {wrong}, {}, {
f_customer_blocked("c3").
f_order_amount(7,100).
f_order_by(7,"c3").
}).

#neg(e6, {wrong}, {}, {
f_customer_blocked("c1").
}).
