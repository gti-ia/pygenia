concern__(X) :- (response(R)[subject(S2),target(T2)] & T2=proposer & 
                (R=accept & X=1 | R=reject & X=0)) |
                (offer(M)[subject(S1),target(T1)] & 
                T=responder & X=M+0.3).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,1}.

others__: { responder: [ affective_link: 0.0 ] }.

max_threshold(0.5).

round(0).

max_round(50).

min_accepted_offer(0).

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
        !propose;
    }.

+!propose: max_threshold(T) & offer(O) & previuos_response(R) & min_accepted_offer(A)
<-
    -offer(O);
    .estimate_offer_ug(T,O,M,R,A);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    +offer(M)[subject(proposer),target(responder)];
    .print(M).

+!propose: max_threshold(T) & min_accepted_offer(A)
<-
    .estimate_offer_ug(T,0,M,"None",A);
    .send(responder,tell, offer(M)[subject(proposer),target(responder)]);
    +offer(M)[subject(proposer),target(responder)].
    

+response(R): offer(M) & R == reject
<-
    -+previuos_response(R);
    !start.

+response(R): offer(M) & R == accept
<-
    -min_accepted_offer(0);
    +min_accepted_offer(M);
    -+previuos_response(R);
    !start.


