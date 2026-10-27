dom_t_amount(V) :- f_refund_amount(_,V).
thr_t_amount(35).
thr_t_amount(40).
thr_t_amount(55).
thr_t_amount(60).
thr_t_amount(75).
thr_t_amount(80).
thr_t_amount(90).
thr_t_amount(95).
thr_t_amount(120).
thr_t_amount(140).
thr_t_amount(180).
thr_t_amount(230).
thr_t_amount(260).
thr_t_amount(310).
thr_t_amount(450).
thr_t_amount(500).
thr_t_amount(640).
thr_t_amount(750).
thr_t_amount(1200).
thr_t_amount(1500).
gt_t_amount(X, C) :- dom_t_amount(X), thr_t_amount(C), X > C.
lt_t_amount(X, C) :- dom_t_amount(X), thr_t_amount(C), X < C.

#constant(t_amount, 35).
#constant(t_amount, 40).
#constant(t_amount, 55).
#constant(t_amount, 60).
#constant(t_amount, 75).
#constant(t_amount, 80).
#constant(t_amount, 90).
#constant(t_amount, 95).
#constant(t_amount, 120).
#constant(t_amount, 140).
#constant(t_amount, 180).
#constant(t_amount, 230).
#constant(t_amount, 260).
#constant(t_amount, 310).
#constant(t_amount, 450).
#constant(t_amount, 500).
#constant(t_amount, 640).
#constant(t_amount, 750).
#constant(t_amount, 1200).
#constant(t_amount, 1500).

#modeh(wrong).
#modeb(2, f_refund_amount(var(t_refund), var(t_amount))).
#modeb(2, f_refund_by(var(t_refund), var(t_customer))).
#modeb(2, f_refund_channel(var(t_refund), var(t_channel))).
#modeb(1, gt_t_amount(var(t_amount), const(t_amount))).
#modeb(1, lt_t_amount(var(t_amount), const(t_amount))).
#maxv(4).

#neg(e1, {wrong}, {}, {
f_refund_amount(101,40).
f_refund_amount(102,120).
f_refund_amount(103,75).
f_refund_by(101,"c-anna").
f_refund_by(102,"c-ben").
f_refund_by(103,"c-cara").
f_refund_channel(101,"card").
f_refund_channel(102,"card").
f_refund_channel(103,"cash").
}).

#neg(e2, {wrong}, {}, {
f_refund_amount(201,500).
f_refund_amount(202,60).
f_refund_amount(203,230).
f_refund_by(201,"c-dev").
f_refund_by(202,"c-eli").
f_refund_by(203,"c-fay").
f_refund_channel(201,"card").
f_refund_channel(202,"voucher").
f_refund_channel(203,"card").
}).

#neg(e3, {wrong}, {}, {
f_refund_amount(301,310).
f_refund_amount(302,90).
f_refund_by(301,"c-gus").
f_refund_by(302,"c-hana").
f_refund_channel(301,"cash").
f_refund_channel(302,"card").
}).

#neg(e4, {wrong}, {}, {
f_refund_amount(401,450).
f_refund_amount(402,35).
f_refund_amount(403,180).
f_refund_by(401,"c-ivo").
f_refund_by(402,"c-jo").
f_refund_by(403,"c-kim").
f_refund_channel(401,"card").
f_refund_channel(402,"card").
f_refund_channel(403,"voucher").
}).

#pos(e5, {wrong}, {}, {
f_refund_amount(501,1200).
f_refund_amount(502,80).
f_refund_by(501,"c-lea").
f_refund_by(502,"c-max").
f_refund_channel(501,"cash").
f_refund_channel(502,"card").
}).

#pos(e6, {wrong}, {}, {
f_refund_amount(601,750).
f_refund_amount(602,140).
f_refund_amount(603,55).
f_refund_by(601,"c-nia").
f_refund_by(602,"c-oli").
f_refund_by(603,"c-pia").
f_refund_channel(601,"card").
f_refund_channel(602,"card").
f_refund_channel(603,"cash").
}).

#pos(e7, {wrong}, {}, {
f_refund_amount(701,1500).
f_refund_amount(702,260).
f_refund_by(701,"c-quin").
f_refund_by(702,"c-rae").
f_refund_channel(701,"card").
f_refund_channel(702,"voucher").
}).

#pos(e8, {wrong}, {}, {
f_refund_amount(801,640).
f_refund_amount(802,95).
f_refund_by(801,"c-sam").
f_refund_by(802,"c-tia").
f_refund_channel(801,"cash").
f_refund_channel(802,"card").
}).
