concern__ (X) :- tiempo(nublado) & X=0.5 | tiempo(soleado) & X=1 .

!start.

+!start
<-
+tiempo(soleado);
!express_emotion;
-tiempo(soleado);
+tiempo(nublado);
!express_emotion.

+tiempo(X)
<-
.print("El tiempo esta", X).

+!express_emotion
<-
!happy_emotion;
!sad_emotion.

@p1[affect__(happy)]
+!happy_emotion
<-
.print("Great! I am happy").

@p2[affect__(sad)]
+!sad_emotion
<-
.print("Too bad. I am sad").