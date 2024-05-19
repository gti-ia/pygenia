!start.

max_round(10).

+!start: round(R) & max_round(M)
<-
    if(R < M){
        .wait(2000);
        -round(R);
        Y=R+1;
        +round(Y);
        .print("starting round", Y,"...");
        .send(agent_a, achieve, ask);
        .send(agent_b, achieve, ask);
    }.

+!start 
<-
    .wait(8000);
    .print("starting round", 1,"...");
    +round(1);
    .send(agent_a, achieve, ask);
    .send(agent_b, achieve, ask). 

+decision(_): decision(A)[source(agent_a)] & decision(B)[source(agent_b)]
<-
    .print(A,B);
    -decision(A)[source(agent_a)];
    -decision(B)[source(agent_b)];
    .send(agent_a, tell, decision(B)[subject(agent_b), target(agent_a)]);
    .send(agent_b, tell, decision(A)[subject(agent_a), target(agent_b)]);
    !start.

