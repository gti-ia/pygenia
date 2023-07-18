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


exp_data_sweden <- read.csv(file="Sweden_experiment_data.csv",head=TRUE, sep=";")
exp_data_sweden <- as.data.frame(exp_data_sweden)

exp_data_spanish <- read.csv(file="spanish.csv",head=TRUE, sep=";")
exp_data_spanish <- as.data.frame(exp_data_spanish)

exp_data_portugal <- read.csv(file="Portugal_experiment_data.csv",head=TRUE, sep=";")
exp_data_portugal <- as.data.frame(exp_data_portugal)

emotion = c("fea", "hap", "dis", "sle", "dis", "sur", "exc", "bor", "ang", "sad")
for (emotion in c("fea", "hap", "cal", "sle", "dis", "sur", "exc", "bor", "ang", "sad")){
  
  
  
  emotion_spanish <- as.data.frame(cbind(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]],PolarCoor(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]])))
  names(emotion_spanish) <- c("p","a","alfa")
  emotion_spanish <- na.omit(emotion_spanish)
  
  emotion_portugal <- as.data.frame(cbind(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]],PolarCoor(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]])))
  names(emotion_portugal) <- c("p","a","alfa")
  emotion_portugal <- na.omit(emotion_portugal)
  
  emotion_sweden <- as.data.frame(cbind(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]],PolarCoor(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]])))
  names(emotion_sweden) <- c("p","a","alfa")
  emotion_sweden <- na.omit(emotion_sweden)
  
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
    if (length(l) != 0) {
      return(limpiar(circular(s),t))
    }
    print(m*(180/pi))
    print(std*(180/pi))
    print(length(s))
    return(s)
  }
  
  
  times = 3
  print(emotion)
  print("Spanish")
  emotion_spanish = limpiar(circular(emotion_spanish$alfa*(pi/180)), times) *(180/pi)
  print("Portugal")
  emotion_portugal = limpiar(circular(emotion_portugal$alfa*(pi/180)), times)  *(180/pi)
  print("Swedish")
  emotion_sweden = limpiar(circular(emotion_sweden$alfa*(pi/180)), times)  *(180/pi)
  
  colores <- c("red", "blue", "green")
  
  pdf(paste0(emotion, "_density_distribution.pdf"), width = 10, height = 5)
  
  band = 10
  max_v = max(c(density(emotion_spanish,bw = band)$y, density(emotion_portugal,bw = band)$y, density(emotion_sweden,bw = band)$y))
  
  
  
  estimacion_densidad_anger <- density(emotion_spanish,bw = band)
  plot(estimacion_densidad_anger$x,estimacion_densidad_anger$y, type = "l", lwd = 2, lty = 1, col = "red",
       xlab = "Degrees", ylab = "Density", xlim = c(0, 360), ylim = c(0, max_v+0.001))
  
  estimacion_densidad <- density(emotion_portugal,bw = band)
  lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[2])
  
  estimacion_densidad <- density(emotion_sweden,bw = band)
  lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[3])
  
  legend("bottomright", legend = c("spanish", "portugal", "swedish"), col = colores, lty = 1, lwd = 2, bg = "transparent")
  dev.off()
  
  sweden_emotion <- as.data.frame(cbind(emotion_sweden,rep("sweden",times=length(emotion_sweden))))
  names(sweden_emotion) <- c("alfa",'count')
  portugal_emotion <- as.data.frame(cbind(emotion_portugal,rep("portugal",times=length(emotion_spanish))))
  names(portugal_emotion) <- c("alfa",'count')
  spanish_emotion <- as.data.frame(cbind(emotion_spanish,rep("spanish",times=length(emotion_spanish))))
  names(spanish_emotion) <- c("alfa",'count')
  emotion_test <- rbind(spanish_emotion,portugal_emotion,sweden_emotion)
  emotion_test$alfa = as.numeric(emotion_test$alfa)
  
  print(emotion)
  print(kruskal.test(alfa ~ count, data = emotion_test))
  print(pairwise.wilcox.test(x = emotion_test$alfa, g = emotion_test$count, p.adjust.method = "holm" ))
  
  print("Spanish Portugal")
  print(wilcox.test(emotion_spanish,emotion_portugal))
  print("Spanish Sweden")
  print(wilcox.test(emotion_spanish,emotion_sweden))
  print("Portugal sweden")
  print(wilcox.test(emotion_portugal,emotion_sweden))
}



for (emotion in c("fea", "hap", "cal", "sle", "dis", "sur", "exc", "bor", "ang", "sad")){
  
  
  
  emotion_spanish <- as.data.frame(cbind(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]],PolarCoor(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]])))
  names(emotion_spanish) <- c("p","a","alfa")
  emotion_spanish <- na.omit(emotion_spanish)
  
  emotion_portugal <- as.data.frame(cbind(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]],PolarCoor(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]])))
  names(emotion_portugal) <- c("p","a","alfa")
  emotion_portugal <- na.omit(emotion_portugal)
  
  emotion_sweden <- as.data.frame(cbind(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]],PolarCoor(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]])))
  names(emotion_sweden) <- c("p","a","alfa")
  emotion_sweden <- na.omit(emotion_sweden)
  
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
    if (length(l) != 0) {
      return(limpiar(circular(s),t))
    }
    print(m*(180/pi))
    print(std*(180/pi))
    print(length(s))
    return(s)
  }
  
  
  times = 3
  print(emotion)
  print("Spanish")
  emotion_spanish = limpiar(circular(emotion_spanish$alfa*(pi/180)), times) *(180/pi)
  print("Portugal")
  emotion_portugal = limpiar(circular(emotion_portugal$alfa*(pi/180)), times)  *(180/pi)
  print("Swedish")
  emotion_sweden = limpiar(circular(emotion_sweden$alfa*(pi/180)), times)  *(180/pi)
  
  colores <- c("red", "blue", "green")
  
  pdf(paste0(emotion, "_density_distribution.pdf"), width = 10, height = 5)
  
  band = 12
  max_v = max(c(density(emotion_spanish,bw = band)$y, density(emotion_portugal,bw = band)$y, density(emotion_sweden,bw = band)$y))
  
  
  
  estimacion_densidad_anger <- density(emotion_spanish,bw = band)
  plot(estimacion_densidad_anger$x,estimacion_densidad_anger$y, type = "l", lwd = 2, lty = 1, col = "red",
       xlab = "Degrees", ylab = "Density", xlim = c(0, 360), ylim = c(0, max_v+0.001))
  
  estimacion_densidad <- density(emotion_portugal,bw = band)
  lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[2])
  
  estimacion_densidad <- density(emotion_sweden,bw = band)
  lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[3])
  
  legend("bottomright", legend = c("spanish", "portugal", "swedish"), col = colores, lty = 1, lwd = 2, bg = "transparent")
  dev.off()
  
  sweden_emotion <- as.data.frame(cbind(emotion_sweden,rep("sweden",times=length(emotion_sweden))))
  names(sweden_emotion) <- c("alfa",'count')
  portugal_emotion <- as.data.frame(cbind(emotion_portugal,rep("portugal",times=length(emotion_spanish))))
  names(portugal_emotion) <- c("alfa",'count')
  spanish_emotion <- as.data.frame(cbind(emotion_spanish,rep("spanish",times=length(emotion_spanish))))
  names(spanish_emotion) <- c("alfa",'count')
  emotion_test <- rbind(spanish_emotion,portugal_emotion,sweden_emotion)
  emotion_test$alfa = as.numeric(emotion_test$alfa)
  
for (emotion in c("fea", "hap", "dis", "sle", "cal", "sur", "exc", "bor", "ang", "sad")){
  
  
  
  emotion_spanish <- as.data.frame(cbind(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]],PolarCoor(exp_data_spanish[[paste0(emotion,"_p")]],exp_data_spanish[[paste0(emotion,"_a")]])))
  names(emotion_spanish) <- c("p","a","alfa")
  emotion_spanish <- na.omit(emotion_spanish)
  
  emotion_portugal <- as.data.frame(cbind(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]],PolarCoor(exp_data_portugal[[paste0(emotion,"_p")]],exp_data_portugal[[paste0(emotion,"_a")]])))
  names(emotion_portugal) <- c("p","a","alfa")
  emotion_portugal <- na.omit(emotion_portugal)
  
  emotion_sweden <- as.data.frame(cbind(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]],PolarCoor(exp_data_sweden[[paste0(emotion,"_p")]],exp_data_sweden[[paste0(emotion,"_a")]])))
  names(emotion_sweden) <- c("p","a","alfa")
  emotion_sweden <- na.omit(emotion_sweden)
  
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
    if (length(l) != 0) {
      return(limpiar(circular(s),t))
    }
    return(s)
  }
  
  
  times = 3
  print(emotion)
  print("Spanish")
  emotion_spanish = limpiar(circular(emotion_spanish$alfa*(pi/180)), times) *(180/pi)
  print("Portugal")
  emotion_portugal = limpiar(circular(emotion_portugal$alfa*(pi/180)), times)  *(180/pi)
  print("Swedish")
  emotion_sweden = limpiar(circular(emotion_sweden$alfa*(pi/180)), times)  *(180/pi)
  
  print(shapiro.test(emotion_spanish))
  print(shapiro.test(emotion_portugal))
  print(shapiro.test(emotion_sweden))
}


}


