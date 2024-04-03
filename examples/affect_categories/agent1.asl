concern__(X) :- weather(cloudy) & X=0.5 | weather(sunny) & X=1 .

personality__: {[O:0.1,C:0.2,E:0.3,A:0.4,N:0.5], 0.6}.

others__: { lily: [ affective_link: 0.9 ],
        barney: [ affective_link: -0.5 ] }.

!start.

+!start
<-
+weather(sunny)[subject(lily), target(barney)];
!express_emotion;
-weather(sunny);
+weather(cloudy);
!express_emotion.

+weather(X)
<-
.print("The weather is ", X).

+!express_emotion
<-
!happy_emotion;
!sad_emotion;
!angry_emotion;
!help.

@p1[affect__(felicidad)]
+!happy_emotion
<-
.print("Great! I am happy").

@p2[affect__(tristeza, sorpresa)]
+!sad_emotion
<-
.print("Too bad. I am sad").

@p3[affect__(angry)]
+!angry_emotion
<-
.print("I'm getting angry").

@p4[affect__(sad, angry)]
+!help
<-
.print("Sorry, can you help me?").