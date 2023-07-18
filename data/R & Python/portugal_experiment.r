library(foreign)
library(corrplot)
library(corrr)
library(psych)
library(xtable)
library(stats)
library(modeest)
library(tsoutliers)
library(circular)
library(tidyverse)
library(circlize)
library(circular)
library(plotrix)
library(gmp)
library(Rmpfr)
library(Bessel)
library(bpDir)
library(TwoCircles)

if (!requireNamespace("Cairo", quietly = TRUE)) {
  install.packages("Cairo")
}

library(Cairo)
PolarCoor <- function(x,y){
  res = integer(length(x))
  for(i in 1:length(x)){
    if(x[i] == 0){
      if(y[i] < 0){
        res[i] = 270
      }else if(y[i] == 0){
        res[i] = NaN
      }else{
        res[i] = 90
      }
    }else if(y[i] == 0){
      if(x[i] < 0){
        res[i] = 180
      }else(0)
    }else if(x[i] < 0){
      res[i] = (atan(y[i]/x[i])*180/pi)+180
    }else if(y[i] < 0){
      res[i] = (atan(y[i]/x[i])*180/pi)+360
    }else{
      res[i] = atan(y[i]/x[i])*180/pi
    }
  }
  return(res)
}

getwd()

exp_data <- read.csv(file="Portugal_experiment_data.csv",head=TRUE, sep=";")
exp_data <- as.data.frame(exp_data)

fear <- as.data.frame(cbind(exp_data$fea_p,exp_data$fea_a,PolarCoor(exp_data$fea_p,exp_data$fea_a)))
names(fear) <- c("p","a","alfa")
fear <- na.omit(fear)

surprise <- as.data.frame(cbind(exp_data$sur_p,exp_data$sur_a,PolarCoor(exp_data$sur_p,exp_data$sur_a)))
names(surprise) <- c("p","a","alfa")
surprise <- na.omit(surprise)

disgust <- as.data.frame(cbind(exp_data$dis_p,exp_data$dis_a,PolarCoor(exp_data$dis_p,exp_data$dis_a)))
names(disgust) <- c("p","a","alfa")
disgust <- na.omit(disgust)

anger <- as.data.frame(cbind(exp_data$ang_p,exp_data$ang_a,PolarCoor(exp_data$ang_p,exp_data$ang_a)))
names(anger) <- c("p","a","alfa")
anger <- na.omit(anger)

boredom <- as.data.frame(cbind(exp_data$bor_p,exp_data$bor_a,PolarCoor(exp_data$bor_p,exp_data$bor_a)))
names(boredom) <- c("p","a","alfa")
boredom <- na.omit(boredom)

sleepiness <- as.data.frame(cbind(exp_data$sle_p,exp_data$sle_a,PolarCoor(exp_data$sle_p,exp_data$sle_a)))
names(sleepiness) <- c("p","a","alfa")
sleepiness <- na.omit(sleepiness)

sadness <- as.data.frame(cbind(exp_data$sad_p,exp_data$sad_a,PolarCoor(exp_data$sad_p,exp_data$sad_a)))
names(sadness) <- c("p","a","alfa")
sadness <- na.omit(sadness)

excitement <- as.data.frame(cbind(exp_data$exc_p,exp_data$exc_a,PolarCoor(exp_data$exc_p,exp_data$exc_a)))
names(excitement) <- c("p","a","alfa")
excitement <- na.omit(excitement)

calm <- as.data.frame(cbind(exp_data$cal_p,exp_data$cal_a,PolarCoor(exp_data$cal_p,exp_data$cal_a)))
names(calm) <- c("p","a","alfa")
calm <- na.omit(calm)

happiness <- as.data.frame(cbind(exp_data$hap_p,exp_data$hap_a,PolarCoor(exp_data$hap_p,exp_data$hap_a)))
names(happiness) <- c("p","a","alfa")
happiness <- na.omit(happiness)

g_fear <- circular(fear$alfa*(pi/180))
g_surprise <- circular(surprise$alfa*(pi/180))
g_disgust <- circular(disgust$alfa*(pi/180))
g_anger <- circular(anger$alfa*(pi/180))
g_boredom <- circular(boredom$alfa*(pi/180))
g_boredom <- g_boredom[-c(41)]
g_sleepiness <- circular(sleepiness$alfa*(pi/180))
g_sadness <- circular(sadness$alfa*(pi/180))
g_excitement <- circular(excitement$alfa*(pi/180))
g_calm <- circular(calm$alfa*(pi/180))
g_happiness <- circular(happiness$alfa*(pi/180))

pre_mean <- c(mean(g_fear),
              mean(g_surprise),
              mean(g_disgust),
              mean(g_anger),
              mean(g_boredom),
              mean(g_sleepiness),
              mean(g_sadness),
              mean(g_excitement),
              mean(g_calm),
              mean(g_happiness))

pre_sd <- c(sd(g_fear),
            sd(g_surprise),
            sd(g_disgust),
            sd(g_anger),
            sd(g_boredom),
            sd(g_sleepiness),
            sd(g_sadness),
            sd(g_excitement),
            sd(g_calm),
            sd(g_happiness))

#devtools::install_github("SMAC-Group/TwoCircles")

pdf("portugal/portugal_fear_boxplot.pdf")
CircularBoxplot(g_fear)
dev.off()
pdf("portugal/portugal_anger_boxplot.pdf")
CircularBoxplot(g_anger)
dev.off()
pdf("portugal/portugal_disgust_boxplot.pdf")
CircularBoxplot(g_disgust)
dev.off()
pdf("portugal/portugal_sadness_boxplot.pdf")
CircularBoxplot(g_sadness)
dev.off()
pdf("portugal/portugal_boredom_boxplot.pdf")
CircularBoxplot(g_boredom)
dev.off()
pdf("portugal/portugal_sleepiness_boxplot.pdf")
CircularBoxplot(g_sleepiness)
dev.off()
pdf("portugal/portugal_calm_boxplot.pdf")
CircularBoxplot(g_calm)
dev.off()
pdf("portugal/portugal_happiness_boxplot.pdf")
CircularBoxplot(g_happiness)
dev.off()
pdf("portugal/portugal_excitement_boxplot.pdf")
CircularBoxplot(g_excitement)
dev.off()
pdf("portugal/portugal_surprise_boxplot.pdf")
CircularBoxplot(g_surprise)
dev.off()

describe(g_surprise)

c_surprise <- circular(subset(g_surprise,subset=g_surprise<=(125*pi/180) & g_surprise>=(18*pi/180)))
c_sleepiness <- circular(subset(g_sleepiness,subset=g_sleepiness<=(300*pi/180) & g_sleepiness>=(225*pi/180)))
c_sadness <- circular(subset(g_sadness,subset=g_sadness<=(240*pi/180) & g_sadness>=(160*pi/180)))
c_happiness <- circular(subset(g_happiness,subset=g_happiness<=(63*pi/180) & g_happiness>=(16*pi/180)))
c_fear <- circular(subset(g_fear,subset=g_fear<=(246*pi/180) & g_fear>=(60*pi/180)))
c_excitement <- circular(subset(g_excitement,subset=g_excitement<=(73*pi/180) & g_excitement>=(45*pi/180)))
c_disgust <- circular(subset(g_disgust,subset=g_disgust<=(315*pi/180) & g_disgust>=(120*pi/180)))
c_calm <- circular(subset(g_calm,subset=g_calm<=(45*pi/180) | g_calm>=(180*pi/180)))
c_boredom <- circular(subset(g_boredom,subset=g_boredom<=(300*pi/180) & g_boredom>=(180*pi/180)))
#c_anger <- circular(subset(g_anger,subset=g_anger<=(165*pi/180) & g_anger>=(118*pi/180)))
c_anger = g_anger
CircularBoxplot(c_fear)
CircularBoxplot(c_anger)
CircularBoxplot(c_disgust)
CircularBoxplot(c_sadness)
#c_boredom <- c_boredom[-c(6)]
CircularBoxplot(c_boredom)
CircularBoxplot(c_sleepiness)
CircularBoxplot(c_calm)
CircularBoxplot(c_happiness)
CircularBoxplot(c_excitement)
CircularBoxplot(c_surprise)


describe(c_surprise)

clean_mean <- c(mean(c_fear),
                mean(c_surprise),
                mean(c_disgust),
                mean(c_anger),
                mean(c_boredom),
                mean(c_sleepiness),
                mean(c_sadness),
                mean(c_excitement),
                mean(c_calm),
                mean(c_happiness))


clean_sd <- c(sd(c_fear),
              sd(c_surprise),
              sd(c_disgust),
              sd(c_anger),
              sd(c_boredom),
              sd(c_sleepiness),
              sd(c_sadness),
              sd(c_excitement),
              sd(c_calm),
              sd(c_happiness))


#von mises distribution

positive_means <- c()
for(x in clean_mean){
  if(x < 0){
    x = x + 2*pi
  }
  positive_means <- append(positive_means,x,length(positive_means))
}
positive_means <- append(positive_means,0,0)
positive_means <- append(positive_means,6.28,length(positive_means))
positive_means <- round(positive_means,2)

positive_means*180/pi
clean_sd*180/pi

plot(NA,xlim=c(-0,2*pi), ylim=c(0,3),xaxt = "n", yaxt='n',xlab="", ylab="")
Axis(side=1, at=positive_means,
     las=2)


x<-seq(0, 2*pi, 0.02)
s <- sum(sin(c_excitement))
c <- sum(cos(c_excitement))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_excitement - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_excitement)), kappa),type="b", lwd=1,lty=1,pch=4,col="red",from=0, to=2*pi,xaxt = "n", yaxt='n',xlab="", ylab="",add=TRUE)

s <- sum(sin(c_anger))
c <- sum(cos(c_anger))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_anger - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_anger)), kappa),type="b", pch=8, col="grey",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_fear))
c <- sum(cos(c_fear))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_fear - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_fear)), kappa),type="b", pch=9,col="darkorange",from=0, to=2*pi,add=TRUE)

s <- sum(sin(g_disgust))
c <- sum(cos(g_disgust))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(g_disgust - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(g_disgust)), kappa),type="b", lwd=1, lty=1, pch=1 ,col="pink2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_sadness))
c <- sum(cos(c_sadness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_sadness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_sadness)), kappa),type="b", pch=6, col="cyan2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_boredom))
c <- sum(cos(c_boredom))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_boredom - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_boredom)), kappa),type="b", lwd=1, col="blueviolet",lty=1,pch=0,from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_sleepiness))
c <- sum(cos(c_sleepiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_sleepiness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_sleepiness)), kappa),type="b", pch=15, col="darkgoldenrod3",from=0, to=2*pi,add=TRUE)

s <- sum(sin(g_calm))
c <- sum(cos(g_calm))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(g_calm - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(g_calm)), kappa),type="b", lwd=1, col="#6495ED",pch=3,lty=1,from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_happiness))
c <- sum(cos(c_happiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_happiness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_happiness)), kappa),type="b", pch=19, lwd=1, col="green2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c_surprise))
c <- sum(cos(c_surprise))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_surprise - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c_surprise)), kappa),type="b",pch=2, lwd=1, col="blue",lty=1,from=0, to=2*pi,add=TRUE)








seq_x<-seq(0, 2*pi, 0.01)


s <- sum(sin(c_surprise))
c <- sum(cos(c_surprise))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_surprise - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_surprise)), kappa)

s <- sum(sin(c_happiness))
c <- sum(cos(c_happiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_happiness - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_happiness)), kappa)

s <- sum(sin(g_calm))
c <- sum(cos(g_calm))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_calm - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(g_calm)), kappa)

s <- sum(sin(c_sleepiness))
c <- sum(cos(c_sleepiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_sleepiness - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))

#pvonmises(circular(245*pi/180), mu=circular(mean(c_sleepiness)), kappa)


s <- sum(sin(c_boredom))
c <- sum(cos(c_boredom))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_boredom - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir+2*pi
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_boredom)), kappa)

s <- sum(sin(c_sadness))
c <- sum(cos(c_sadness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_sadness - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_sadness)), kappa)

s <- sum(sin(g_disgust))
c <- sum(cos(g_disgust))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_disgust - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_disgust)), kappa)

s <- sum(sin(c_fear))
c <- sum(cos(c_fear))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_fear - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_fear)), kappa)

s <- sum(sin(c_anger))
c <- sum(cos(c_anger))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_anger - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))
#pvonmises(circular(245*pi/180), mu=circular(mean(c_anger)), kappa)

s <- sum(sin(c_excitement))
c <- sum(cos(c_excitement))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c_excitement - mean.dir)))
Z <- 2 * pi * BesselI(kappa,0)
x <- 245*pi/180
loc <- mean.dir
a <- (exp(kappa*cos(seq_x - loc)))/Z
((exp(kappa*cos(x - loc))/Z)-min(a))/(max(a)-min(a))






m_fear <- as.data.frame(cbind(fear$p,fear$a,fear$alfa*(pi/180)))
names(m_fear) <- c("p","a","alfa")
m_fear <- subset(m_fear,subset=m_fear$alfa<=(246*pi/180) & m_fear$alfa>=(60*pi/180))

m_surprise <- as.data.frame(cbind(surprise$p,surprise$a,surprise$alfa*(pi/180)))
names(m_surprise) <- c("p","a","alfa")
m_surprise <- subset(m_surprise,subset=m_surprise$alfa<=(125*pi/180) & m_surprise$alfa>=(18*pi/180))

m_sleepiness <- as.data.frame(cbind(sleepiness$p,sleepiness$a,sleepiness$alfa*(pi/180)))
names(m_sleepiness) <- c("p","a","alfa")
m_sleepiness <- subset(m_sleepiness,subset=m_sleepiness$alfa<=(300*pi/180) & m_sleepiness$alfa>=(225*pi/180))

m_sadness <- as.data.frame(cbind(sadness$p,sadness$a,sadness$alfa*(pi/180)))
names(m_sadness) <- c("p","a","alfa")
m_sadness <- subset(m_sadness,subset=m_sadness$alfa<=(240*pi/180) & m_sadness$alfa>=(160*pi/180))

m_happiness <- as.data.frame(cbind(happiness$p,happiness$a,happiness$alfa*(pi/180)))
names(m_happiness) <- c("p","a","alfa")
m_happiness <- subset(m_happiness,subset=m_happiness$alfa<=(63*pi/180) & m_happiness$alfa>=(16*pi/180))

m_excitement <- as.data.frame(cbind(excitement$p,excitement$a,excitement$alfa*(pi/180)))
names(m_excitement) <- c("p","a","alfa")
m_excitement <- subset(m_excitement,subset=m_excitement$alfa<=(73*pi/180) & m_excitement$alfa>=(45*pi/180))

m_disgust <- as.data.frame(cbind(disgust$p,disgust$a,disgust$alfa*(pi/180)))
names(m_disgust) <- c("p","a","alfa")
m_disgust <- subset(m_disgust,subset=m_disgust$alfa<=(315*pi/180) & m_disgust$alfa>=(120*pi/180))

m_calm <- as.data.frame(cbind(calm$p,calm$a,calm$alfa*(pi/180)))
names(m_calm) <- c("p","a","alfa")
m_calm <- subset(m_calm,subset=m_calm$alfa<=(45*pi/180) | m_calm$alfa>=(180*pi/180))

m_boredom <- as.data.frame(cbind(boredom$p,boredom$a,boredom$alfa*(pi/180)))
names(m_boredom) <- c("p","a","alfa")
m_boredom <- subset(m_boredom,subset=m_boredom$alfa<=(300*pi/180) & m_boredom$alfa>=(180*pi/180))

m_anger <- as.data.frame(cbind(anger$p,anger$a,anger$alfa*(pi/180)))
names(m_anger) <- c("p","a","alfa")

PolarCoor(mean(m_fear$p),mean(m_fear$a))*pi/180
PolarCoor(mean(m_surprise$p),mean(m_surprise$a))*pi/180
PolarCoor(mean(m_sleepiness$p),mean(m_sleepiness$a))*pi/180
PolarCoor(mean(m_sadness$p),mean(m_sadness$a))*pi/180
PolarCoor(mean(m_happiness$p),mean(m_happiness$a))*pi/180
PolarCoor(mean(m_excitement$p),mean(m_excitement$a))*pi/180
PolarCoor(mean(m_disgust$p),mean(m_disgust$a))*pi/180
PolarCoor(mean(m_calm$p),mean(m_calm$a))*pi/180
PolarCoor(mean(m_boredom$p),mean(m_boredom$a))*pi/180
PolarCoor(mean(anger$p),mean(anger$a))*pi/180

x <- matrix(c(1,1,-1,-1),ncol=2,byrow=TRUE)
plot(x,col="white")

x <- c(mean(m_fear$p)/3,mean(m_surprise$p)/3,mean(m_disgust$p)/3,mean(m_anger$p)/3,mean(m_boredom$p)/3,mean(m_sleepiness$p)/3,
       mean(m_sadness$p)/3,mean(m_excitement$p)/3,mean(m_calm$p)/3,mean(m_happiness$p)/3)
y <- c(mean(m_fear$a)/3,mean(m_surprise$a)/3,mean(m_disgust$a)/3,mean(m_anger$a)/3,mean(m_boredom$a)/3,mean(m_sleepiness$a)/3,
       mean(m_sadness$a)/3,mean(m_excitement$a)/3,mean(m_calm$a)/3,mean(m_happiness$a)/3)

plot(x,y,xlab="Pleasure",pch=19,ylab="Arousal",xlim=c(-1,1),ylim=c(-1,1),cex.lab=1.3,cex.axis=1.3)
abline(h = 0, v = 0, col = "black")
text(x,y,labels=c("Fear","Surprise","Disgust","Angry","Boredom",
                  "Sleepy","Sad","Excited","Calm","Happy"),cex=1.3,adj = c(0.5,-1))


r_names <- c("Angry","Bored",
             "Sleepy","Sad","Excited","Calm","Happy")

sx <- c(sd(m_fear$p)/3,sd(m_surprise$p)/3,sd(m_disgust$p)/3,sd(m_anger$p)/3,sd(m_boredom$p)/3,sd(m_sleepiness$p)/3,
        sd(m_sadness$p)/3,sd(m_excitement$p)/3,sd(m_calm$p)/3,sd(m_happiness$p)/3)
sy <- c(sd(m_fear$a)/3,sd(m_surprise$a)/3,sd(m_disgust$a)/3,sd(m_anger$a)/3,sd(m_boredom$a)/3,sd(m_sleepiness$a)/3,
        sd(m_sadness$a)/3,sd(m_excitement$a)/3,sd(m_calm$a)/3,sd(m_happiness$a)/3)



limpiar = function(var, t){
  s = c()
  l = c()
  for (el in var) {
    m = mean(var)
    if (m < 0){
      m = m + 2*pi
    }
    std = sd(var)
    
    v0 = ((m - t*std) %% (2*pi))
    v1 = ((m + t*std) %% (2*pi))
    
    if (m - t * std < 0) {
      if (((el < v0) & el > v1) | ((el > v0) & el < v1)){
        l = c(l,el)} else { s = c(s, el)}
    }
    else if (m + t * std > 2*pi){
      if (((el < v0) & el > v1) | ((el > v0) & el < v1)){
        l = c(l,el)} else { s = c(s, el)}
    }
    else{
      if ((el < v0) | (el > v1)){ 
        l = c(l,el)} else { s = c(s, el)}
    }
  }
  print(m*(180/pi))
  print(std*(180/pi))
  print(length(s))
  print(l)
  if (length(l) != 0) {
    return(limpiar(circular(s),t))
  }
  return(circular(s))
}

times = 3
c1_anger = limpiar(g_anger, times)
c1_boredom = limpiar(g_boredom, times)
c1_calm = limpiar(g_calm, times)
c1_disgust = limpiar(g_disgust, times)
c1_excitement = limpiar(g_excitement, times)
c1_fear = limpiar(g_fear, times)
c1_happiness = limpiar(g_happiness, times)
c1_sleepiness = limpiar(g_sleepiness, times)
c1_surprise = limpiar(g_surprise, times)
c1_sadness = limpiar(g_sadness, times)



library(ggplot2)

# Emociones
emociones <- c("anger", "sleepiness", "surprise", "calm", "happiness", "boredom", "disgust", "excitement", "sadness", "fear")

# Iterar sobre cada emoción
for (emocion in emociones) {
  pdf(paste0("portugal/portugal_", emocion, "_hist.pdf"))  # Guardar el gráfico en un archivo PDF
  p <- ggplot() +
    geom_histogram(data = data.frame(grados = get(paste0("c1_", emocion)) * (180/pi)), aes(x = grados),
                   fill = 'grey', color = 'black', binwidth = 15) + 
    coord_polar(start = 3*pi/2, direction = -1) +
    scale_x_continuous("", limits = c(0, 2*pi * (180/pi)),
                       breaks = c(0, 90, 180, 270), labels = c("0", "90", "180", "270")) +
    scale_y_continuous("", expand = c(0, 0), position = "right") + 
    theme_minimal()
  
  # Mostrar el gráfico
  print(p)
  dev.off()  # Cerrar el archivo PDF
}


pdf("portugal/portugal_fear_cleaned_boxplot.pdf")
CircularBoxplot(c1_fear)
dev.off()
pdf("portugal/portugal_anger_cleaned_boxplot.pdf")
CircularBoxplot(c1_anger)
dev.off()
pdf("portugal/portugal_disgust_cleaned_boxplot.pdf")
CircularBoxplot(c1_disgust)
dev.off()
pdf("portugal/portugal_sadness_cleaned_boxplot.pdf")
CircularBoxplot(c1_sadness)
dev.off()
pdf("portugal/portugal_boredom_cleaned_boxplot.pdf")
CircularBoxplot(c1_boredom)
dev.off()
pdf("portugal/portugal_sleepiness_cleaned_boxplot.pdf")
CircularBoxplot(c1_sleepiness)
dev.off()
pdf("portugal/portugal_calm_cleaned_boxplot.pdf")
CircularBoxplot(c1_calm)
dev.off()
pdf("portugal/portugal_happiness_cleaned_boxplot.pdf")
CircularBoxplot(c1_happiness)
dev.off()
pdf("portugal/portugal_excitement_cleaned_boxplot.pdf")
CircularBoxplot(c1_excitement)
dev.off()
pdf("portugal/portugal_surprise_cleaned_boxplot.pdf")
CircularBoxplot(c1_surprise)
dev.off()


# VON MISES DATA CLEANED

positive_means <- c()
for(x in clean_mean){
  if(x < 0){
    x = x + 2*pi
  }
  positive_means <- append(positive_means,x,length(positive_means))
}
positive_means <- append(positive_means,0,0)
positive_means <- append(positive_means,6.28,length(positive_means))
positive_means <- round(positive_means,2)

positive_means*180/pi
clean_sd*180/pi

plot(NA,xlim=c(-0,2*pi), ylim=c(0,3),xaxt = "n", yaxt='n',xlab="", ylab="")
Axis(side=1, at=positive_means,
     las=2)


x<-seq(0, 2*pi, 0.02)
s <- sum(sin(c1_excitement))
c <- sum(cos(c1_excitement))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_excitement - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_excitement)), kappa),type="b", lwd=1,lty=1,pch=4,col="red",from=0, to=2*pi,xaxt = "n", yaxt='n',xlab="", ylab="",add=TRUE)

s <- sum(sin(c1_anger))
c <- sum(cos(c1_anger))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_anger - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_anger)), kappa),type="b", pch=8, col="grey",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_fear))
c <- sum(cos(c1_fear))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_fear - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_fear)), kappa),type="b", pch=9,col="darkorange",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_disgust))
c <- sum(cos(c1_disgust))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_disgust - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_disgust)), kappa),type="b", lwd=1, lty=1, pch=1 ,col="pink2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_sadness))
c <- sum(cos(c1_sadness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_sadness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_sadness)), kappa),type="b", pch=6, col="cyan2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_boredom))
c <- sum(cos(c1_boredom))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_boredom - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_boredom)), kappa),type="b", lwd=1, col="blueviolet",lty=1,pch=0,from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_sleepiness))
c <- sum(cos(c1_sleepiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_sleepiness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_sleepiness)), kappa),type="b", pch=15, col="darkgoldenrod3",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_calm))
c <- sum(cos(c1_calm))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_calm - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_calm)), kappa),type="b", lwd=1, col="#6495ED",pch=3,lty=1,from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_happiness))
c <- sum(cos(c1_happiness))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_happiness - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_happiness)), kappa),type="b", pch=19, lwd=1, col="green2",from=0, to=2*pi,add=TRUE)

s <- sum(sin(c1_surprise))
c <- sum(cos(c1_surprise))
mean.dir <- atan2(s, c)
kappa <- A1inv(mean(cos(c1_surprise - mean.dir)))

plot(function(x) dvonmises(circular(x), mu=circular(mean(c1_surprise)), kappa),type="b",pch=2, lwd=1, col="blue",lty=1,from=0, to=2*pi,add=TRUE)



# MATRIX

m_fear <- as.data.frame(cbind(fear$p,fear$a,fear$alfa*(pi/180)))
names(m_fear) <- c("p","a","alfa")
m_fear <- subset(m_fear, alfa %in% c1_fear)

m_surprise <- as.data.frame(cbind(surprise$p,surprise$a,surprise$alfa*(pi/180)))
names(m_surprise) <- c("p","a","alfa")
m_surprise <- subset(m_surprise,alfa %in% c1_surprise)

m_sleepiness <- as.data.frame(cbind(sleepiness$p,sleepiness$a,sleepiness$alfa*(pi/180)))
names(m_sleepiness) <- c("p","a","alfa")
m_sleepiness <- subset(m_sleepiness,alfa %in% c1_sleepiness)

m_sadness <- as.data.frame(cbind(sadness$p,sadness$a,sadness$alfa*(pi/180)))
names(m_sadness) <- c("p","a","alfa")
m_sadness <- subset(m_sadness, alfa %in% c1_sadness)

m_happiness <- as.data.frame(cbind(happiness$p,happiness$a,happiness$alfa*(pi/180)))
names(m_happiness) <- c("p","a","alfa")
m_happiness <- subset(m_happiness,alfa %in% c1_happiness)

m_excitement <- as.data.frame(cbind(excitement$p,excitement$a,excitement$alfa*(pi/180)))
names(m_excitement) <- c("p","a","alfa")
m_excitement <- subset(m_excitement,alfa %in% c1_excitement)

m_disgust <- as.data.frame(cbind(disgust$p,disgust$a,disgust$alfa*(pi/180)))
names(m_disgust) <- c("p","a","alfa")
m_disgust <- subset(m_disgust, alfa %in% c1_disgust)

m_calm <- as.data.frame(cbind(calm$p,calm$a,calm$alfa*(pi/180)))
names(m_calm) <- c("p","a","alfa")
m_calm <- subset(m_calm, alfa %in% c1_calm)

m_boredom <- as.data.frame(cbind(boredom$p,boredom$a,boredom$alfa*(pi/180)))
names(m_boredom) <- c("p","a","alfa")
m_boredom <- subset(m_boredom, alfa %in% c1_boredom)

m_anger <- as.data.frame(cbind(anger$p,anger$a,anger$alfa*(pi/180)))
names(m_anger) <- c("p","a","alfa")
m_anger <- subset(m_anger, alfa %in% c1_anger)

x <- matrix(c(1,1,-1,-1),ncol=2,byrow=TRUE)
plot(x,col="white")

x <- c(mean(m_fear$p)/3,mean(m_surprise$p)/3,mean(m_disgust$p)/3,mean(m_anger$p)/3,mean(m_boredom$p)/3,mean(m_sleepiness$p)/3,
       mean(m_sadness$p)/3,mean(m_excitement$p)/3,mean(m_calm$p)/3,mean(m_happiness$p)/3)
y <- c(mean(m_fear$a)/3,mean(m_surprise$a)/3,mean(m_disgust$a)/3,mean(m_anger$a)/3,mean(m_boredom$a)/3,mean(m_sleepiness$a)/3,
       mean(m_sadness$a)/3,mean(m_excitement$a)/3,mean(m_calm$a)/3,mean(m_happiness$a)/3)

plot(x,y,xlab="Pleasure",pch=19,ylab="Arousal",xlim=c(-1,1),ylim=c(-1,1),cex.lab=1.3,cex.axis=1.3)
abline(h = 0, v = 0, col = "black")
text(x,y,labels=c("Fear","Surprise","Disgust","Angry","Boredom",
                  "Sleepy","Sad","Excited","Calm","Happy"),cex=1.3,adj = c(0.5,-1))


r_names <- c("Angry","Bored",
             "Sleepy","Sad","Excited","Calm","Happy")

sx <- c(sd(m_fear$p)/3,sd(m_surprise$p)/3,sd(m_disgust$p)/3,sd(m_anger$p)/3,sd(m_boredom$p)/3,sd(m_sleepiness$p)/3,
        sd(m_sadness$p)/3,sd(m_excitement$p)/3,sd(m_calm$p)/3,sd(m_happiness$p)/3)
sy <- c(sd(m_fear$a)/3,sd(m_surprise$a)/3,sd(m_disgust$a)/3,sd(m_anger$a)/3,sd(m_boredom$a)/3,sd(m_sleepiness$a)/3,
        sd(m_sadness$a)/3,sd(m_excitement$a)/3,sd(m_calm$a)/3,sd(m_happiness$a)/3)


# NORMALIDAD

valores = c(c1_anger, c1_boredom, c1_calm, c1_disgust, c1_excitement, c1_fear, c1_happiness, c1_sadness, c1_sleepiness, c1_surprise)
nombres = c(rep("anger",length(c1_anger)), rep("boredom",length(c1_boredom)),rep("calm",length(c1_calm)),rep("disgust",length(c1_disgust)),rep("excitement",length(c1_excitement)),rep("fear",length(c1_fear)), rep("happiness",length(c1_happiness)),rep("sadness",length(c1_sadness)),rep("sleepiness",length(c1_sleepiness)), rep("surprise",length(c1_surprise)))
dataframe <- data.frame(valores = unlist(valores), variables = nombres, stringsAsFactors = FALSE)

for (em in unique(dataframe$variables)){
  data2 = subset(dataframe, variables == em)
  resultado_kuiper <- kuiper.test(circular(data2$valores))
  print(resultado_kuiper)
}

for (em in unique(dataframe$variables)){
  data2 = subset(dataframe, variables == em)
  resultado_reyleigh <- rayleigh.test(circular(data2$valores))
  print(resultado_reyleigh)
}

# DEFERENCIA MEDIAS

matriz_resultados <- matrix(NA, nrow = length(unique(dataframe$variables)), ncol = length(unique(dataframe$variables)))
variables_unicas <- unique(dataframe$variables)
for (i in 1:length(variables_unicas)){
  for (j in 1:length(variables_unicas)){
    if (variables_unicas[i] != variables_unicas[j]){
      data2 <- subset(dataframe, variables == variables_unicas[i])
      data3 <- subset(dataframe, variables == variables_unicas[j])
      resultado_wilcox <- wilcox.test(data2$valores, data3$valores)
      matriz_resultados[i, j] <- resultado_wilcox$p.value
    }
  }
}

colnames(matriz_resultados) = variables_unicas
print(matriz_resultados)
View(matriz_resultados>0.05)

# ANOVA
model = aov.circular(circular(dataframe$valores), dataframe$variables)
model$p.value

# The Wallraff test of angular distances between two or more groups
wallraff.test(circular(dataframe$valores), dataframe$variables)

library(rstatix)
View(tukey_hsd(dataframe, valores ~ variables))

limpiar_lineal = function(var, t){
  s = c()
  l = c()
  for (el in var) {
    m = mean(var)
    if (m < 0){
      m = m + 2*pi
    }
    std = sd(var)
    
    v0 = ((m - t*std) %% (2*pi))
    v1 = ((m + t*std) %% (2*pi))
    
    if (m - t * std < 0) {
      if (((el < v0) & el > v1) | ((el > v0) & el < v1)){
        l = c(l,el)} else { s = c(s, el)}
    }
    else if (m + t * std > 2*pi){
      if (((el < v0) & el > v1) | ((el > v0) & el < v1)){
        l = c(l,el)} else { s = c(s, el)}
    }
    else{
      if ((el < v0) | (el > v1)){ 
        l = c(l,el)} else { s = c(s, el)}
    }
  }
  print(m)
  print(std)
  print(l)
  return(s*(180 / pi))
}

times = 3
c1_anger = limpiar_lineal(g_anger, times)
c1_boredom = limpiar_lineal(g_boredom, times)
c1_calm = limpiar_lineal(g_calm, times)
c1_disgust = limpiar_lineal(g_disgust, times)
c1_excitement = limpiar_lineal(g_excitement, times)
c1_fear = limpiar_lineal(g_fear, times)
c1_happiness = limpiar_lineal(g_happiness, times)
c1_sleepiness = limpiar_lineal(g_sleepiness, times)
c1_surprise = limpiar_lineal(g_surprise, times)
c1_sadness = limpiar_lineal(g_sadness, times)

estimacion_densidad = density(c1_anger)
indice_x_100 <- which.min(abs(estimacion_densidad$x - 100))
densidad_x_100 <- estimacion_densidad$y[indice_x_100]
print(densidad_x_100)

# Define los nombres de las emociones y sus colores correspondientes
emociones <- c("Anger", "Boredom", "Calm", "Disgust", "Excitement", "Happiness", "Sadness", "Sleepiness", "Surprise", "Fear")
colores <- c("red", "blue", "green", "purple", "orange", "pink", "gray", "brown", "cyan", "magenta")

# Estimar la densidad para c1_anger
estimacion_densidad_anger <- density(c1_anger)
pdf("portugal/portugal_density_distribution.pdf", width = 10, height = 5)
plot(estimacion_densidad_anger$x,estimacion_densidad_anger$y, type = "l", lwd = 2, lty = 1, col = "red",
     xlab = "Degrees", ylab = "Density", xlim = c(0, 360), ylim = c(0, 0.07))

# Estimar la densidad para las otras emociones y agregar líneas
for (i in 2:length(emociones)) {
  estimacion_densidad <- density(get(paste0("c1_", tolower(emociones[i]))))
  lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[i])
}

# Agrega la leyenda transparente en la esquina inferior derecha
legend("bottomright", legend = emociones, col = colores, lty = 1, lwd = 2, bg = "transparent")

# Añadir título al gráfico
title(main = "Density Estimation Portugal Model", font.main = 2)

dev.off()

# NORMALIZADO
normalize <- function(data) {
  min_val = min(data)
  max_val = max(data)
  return((data - min_val) / (max_val - min_val))
}


# Define los nombres de las emociones y sus colores correspondientes
emociones <- c("Anger", "Boredom", "Calm", "Disgust", "Excitement", "Happiness", "Sadness", "Sleepiness", "Surprise", "Fear")
colores <- c("red", "blue", "green", "purple", "orange", "pink", "gray", "brown", "cyan", "magenta")

# Estimar la densidad para c1_anger
pdf("portugal/portugal_density_distribution_normalized.pdf", width = 10, height = 5)
estimacion_densidad_anger <- density(c1_anger)
plot(estimacion_densidad_anger$x, normalize(estimacion_densidad_anger$y), type = "l", lwd = 2, lty = 1, col = "red",
     xlab = "Degrees", ylab = "Density", xlim = c(0, 360), ylim = c(0, 1))

# Estimar la densidad para las otras emociones y agregar líneas
for (i in 2:length(emociones)) {
  estimacion_densidad <- density(get(paste0("c1_", tolower(emociones[i]))))
  lines(estimacion_densidad$x, normalize(estimacion_densidad$y), type = "l", lwd = 2, lty = 1, col = colores[i])
}

# Agrega la leyenda transparente en la esquina inferior derecha
legend("bottomright", legend = emociones, col = colores, lty = 1, lwd = 2, bg = "transparent")

# Añadir título al gráfico
title(main = "Density Estimation Portugal Model", font.main = 2)
dev.off()
