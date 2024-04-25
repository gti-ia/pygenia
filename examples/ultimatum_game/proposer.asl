concern__(X) :- offer(M)[subject(S1),target(T1)] & (
                        ((T=responder & X=(M)) | X=(1-M)) |
                        (response(R)[subject(S2),target(T2)] & T2=proposer & 
                        (R=accept & X=(1-M) | R=reject & X=(-(1-M))))
                ).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,1.0}.

others__: { responder: [ affective_link: 0.5 ] }.

max_threshold(0.5).

round(0).

max_round(10).

!start.

+!start: round(R) & max_round(M)
<-
    if(R < M){
        //.print(R);
        -round(R);
        Y=R+1;
        +round(Y);
        !propose;
    }.

+!propose: max_threshold(T) & offer(O)
<-
    .estimate_offer_ug(T,M,O);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    -offer(O)[subject(proposer),target(responder)];
    +offer(M)[subject(proposer),target(responder)].

+!propose: max_threshold(T)
<-
    .estimate_offer_ug(T,M,0.2);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    +offer(M)[subject(proposer),target(responder)].

+response(R)
<-
    //.print(R);
    -response(R);
    !start.


