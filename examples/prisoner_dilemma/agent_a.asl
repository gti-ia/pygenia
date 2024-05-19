concern__(X) :- 
    (
        (my_outcome(N) & X = N)
        |
        (other_outcome(N) & X = N)
    ).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,0.5}.

others__: { agent_b: [ affective_link: 0.5 ] }.

accumulated_years(0).

other_accumulated_years(0).

+!ask <-
    .get_pleasure(P);
    .get_empathic_pleasure(E);
    .send(officer,tell,decision(cooperate));
    -+my_decision(cooperate);
    .print("decicion:",P,E).

+decision(cooperate): my_decision(cooperate) & accumulated_years(Y)
<-
    +my_outcome(0.8);
    -my_outcome(_);
    +other_outcome(0.8);
    -other_outcome(_);
    N = Y+1; 
    -+accumulated_years(N).

+decision(cooperate): my_decision(betray) 
<-
    +my_outcome(1);
    -my_outcome(_);
    +other_outcome(0);
    -other_outcome(_).

+decision(betray): my_decision(cooperate) & accumulated_years(Y)
<-
    +my_outcome(0);
    -my_outcome(_);
    +other_outcome(1);
    -other_outcome(_);
    N = Y+3; 
    -+accumulated_years(N).

+decision(betray): my_decision(betray) & accumulated_years(Y)
<-
    +my_outcome(0.4);
    -my_outcome(_);
    +other_outcome(0.4);
    -other_outcome(_);
    N = Y+2; 
    -+accumulated_years(N).
