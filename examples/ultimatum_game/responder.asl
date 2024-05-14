concern__(X) :- offer(M) & X=M.

min_threshold(0.2).

desired(0.5).

+offer(X): min_threshold(T)
<-
if (X > T){
    .send(proposer,tell, response(accept)[subject(responder),target(proposer),interaction_value(0.05)]);
    .print("propose accepted");
}else{
    .send(proposer,tell, response(reject)[subject(responder),target(proposer),interaction_value(-0.05)]);
    .print("propose rejected");
}.