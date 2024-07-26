concern__(X) :- 
    (
        decision(D)[target(T)] & T = agent_b & 
        (D = betray & X=0)
        |
        (D = cooperate & X=1)
    )
    |
    (
        sentence(S) &
        (S == 0 & X=1) 
        |
        (S == 1 & X = 0.8)
        |
        (S == 2 & X = 0.4)
        |
        (S == 3 & X = 0)
    ).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,0.5}.

others__: { agent_b: [ affective_link: 0.5 ] }.

accumulated_years(0).

other_accumulated_years(0).

+!ask <-
    -decision(_);
    -sentence(_);
    .get_pleasure(P);
    .get_empathic_pleasure(E);
    .send(officer,tell,decision(cooperate));
    +decision(cooperate)[subject(agent_a), target(agent_b)];
    .print("decision:",P,E).

+decision(cooperate): my_decision(cooperate) & accumulated_years(Y)
<-
    sentence(1);
    N = Y+1; 
    -+accumulated_years(N).

+decision(cooperate): my_decision(betray) 
<-
    sentence(0).

+decision(betray): my_decision(cooperate) & accumulated_years(Y)
<-
    sentence(3);
    N = Y+3; 
    -+accumulated_years(N).

+decision(betray): my_decision(betray) & accumulated_years(Y)
<-
    sentence(2);
    N = Y+2; 
    -+accumulated_years(N).
