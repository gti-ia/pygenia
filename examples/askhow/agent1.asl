!start.

me(100,2).

+!start : true
    <-
        .print("Preguntar Plan");
        .send(agent2,askHow,"+!hello");
        .print("Plan Añadido");
        .wait(5000);
        !hello;
        -me(100,2);
        !hello;
        +me(100,4);
        !hello
.

concern__(X):- me(100,2) & X = 1 | me(101,4) & X = 2 | me(103,1) & X = 4.