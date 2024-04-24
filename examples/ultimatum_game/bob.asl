concern__(X) :- offer(M)[subject(S),target(T)] & ((T=bob & X=(1-M)) | (X=(M))).

personality__: {[O:0.0,C:0.0,E:0.5,A:0.0,N:0.5], 0.0,1.0}.

others__: { alice: [ affective_link: 0.0 ] }.

!start.

+!start
<-
    //+offer(0.3)[subject(self),target(alice)];
    //.get_empathic_concern(X);
    //.print(X).
    !propose.

+!propose
<-
    //.estimate_offer(M);
    .send(alice,tell, offer(0.3)[subject(bob),target(alice)]).

+reject
<-
    -reject.

+accept
<-
    -accept.

