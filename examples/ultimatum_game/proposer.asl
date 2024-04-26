concern__(X) :- offer(M)[subject(S1),target(T1)] & (
                        (T=responder & X=(M)) |
                        (response(R)[subject(S2),target(T2)] & T2=proposer & 
                        (R=accept & X=(1-M) | R=reject & X=(-(1-M))))
                ).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,1.0}.

others__: { responder: [ affective_link: 0.5 ] }.

max_threshold(0.5).

round(0).

max_round(10).

!start.

+!start: round(R) & 
         max_round(M) & 
         response(Q)
<-   
    
    if(R < M){
        -round(R);
        Y=R+1;
        +round(Y);
        -response(Q);
        //.print("round",Y);
        !propose;
    }.


+!start: round(R) & max_round(M)
<-
    if(R < M){
        -round(R);
        Y=R+1;
        +round(Y);
        //.print("round",Y);
        !propose;
    }.

+!propose: max_threshold(T) & offer(O)
<-
    -offer(O);
    .estimate_offer_ug(T,O,M);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    +offer(M)[subject(proposer),target(responder)].

+!propose: max_threshold(T)
<-
    .estimate_offer_ug(T,0,M);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    +offer(M)[subject(proposer),target(responder)].
    

+response(R)
<-
    !start.


