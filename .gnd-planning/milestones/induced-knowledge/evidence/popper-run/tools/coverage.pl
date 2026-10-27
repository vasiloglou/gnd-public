% coverage.pl -- compute, per learned clause, the example ids it covers.
% Usage: swipl -q coverage.pl -- BK EXS PROGRAM
% Prints one JSON object per line: {"clause": K, "covered": [ids in exs order]}.
:- initialization(main, main).
:- style_check(-discontiguous).
:- dynamic wrong/1, pos/1, neg/1.

main :-
    current_prolog_flag(argv, [Bk, Exs, Prog]),
    load_files(Bk, [silent(true)]),
    load_files(Exs, [silent(true)]),
    read_clauses(Prog, Clauses),
    forall(nth0(K, Clauses, C), report(K, C)).

read_clauses(File, Clauses) :-
    setup_call_cleanup(open(File, read, S),
                       read_all(S, Clauses),
                       close(S)).
read_all(S, Cs) :-
    read_term(S, T, []),
    (   T == end_of_file -> Cs = []
    ;   Cs = [T|Rest], read_all(S, Rest) ).

report(K, Clause) :-
    retractall(wrong(_)),
    assertz(Clause),
    findall(Id, ((pos(wrong(Id)) ; neg(wrong(Id))), once(wrong(Id))), Ids),
    maplist([I, Q]>>format(atom(Q), '"~w"', [I]), Ids, Qs),
    atomic_list_concat(Qs, ',', Body),
    format('{"clause": ~w, "covered": [~w]}~n', [K, Body]).
