concern__(X) :- weather(cloudy) & X=0.5 | weather(sunny) & X=1 .

personality__: {[O:0.0,C:0.0,E:1.0,A:0.0,N:0.1], 0.6}.

others__: { lily: [ affective_link: 0.9 ],
        barney: [ affective_link: -0.5 ] }.

!start.

+!start
<-
+weather(sunny)[subject(lily), target(self),affective_relevant];
!express_emotion;
-weather(sunny);
+weather(cloudy)[subject(lily), target(self),affective_relevant];
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