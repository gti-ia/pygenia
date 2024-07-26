concern__(X):- me(3) & X = 0.4 | me(2) & X = 0.2 | me(1) & X = 0.6.

me(3).

!start.

+!start : me(3)
<-
    -me(3);
    +me(2);
    .print_afflb;
    .get_affst_pa(P,A);
    .print(P,A);
    !start.

+!start : me(2)
<-
    -me(2);
    +me(1).

