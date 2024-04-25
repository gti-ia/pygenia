threshold(0.2).

desired(0.5).

+offer(X): threshold(T)
<-

if (X > T){
    .send(proposer,tell, response(accept));
    .print("proposer accept");
}else{
    .send(proposer,tell, response(reject)[subject(responder),target(proposer)]);
    .print("proposer reject");
}.