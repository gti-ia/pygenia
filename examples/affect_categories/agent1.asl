concern__ (X) :- weather(cloudy) & X=0.5 | weather(sunny) & X=1 .

!start.

+!start
<-
+weather(sunny);
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

@p1[affect__(happy)]
+!happy_emotion
<-
.print("Great! I am happy").

@p2[affect__(sad)]
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