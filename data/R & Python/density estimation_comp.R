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

pdf("density_distribution_spanish_comp_norm.pdf", width = 10, height = 5)
t = 1

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
  
  print(emotion)
  
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
  emotion_spanish = limpiar(circular(emotion_spanish$alfa*(pi/180)), times) *(180/pi)
  emotion_portugal = limpiar(circular(emotion_portugal$alfa*(pi/180)), times)  *(180/pi)
  emotion_sweden = limpiar(circular(emotion_sweden$alfa*(pi/180)), times)  *(180/pi)
  
  colores <- c("red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "gray", "black")
  
  
  
  band = 10
  max_v = 1
  
  if (t == 1) {
    estimacion_densidad_anger <- density(emotion_spanish, bw = band)
    normalized_densities <- estimacion_densidad_anger$y / max(estimacion_densidad_anger$y)
    print(emotion)
    print(colores[1])
    plot(estimacion_densidad_anger$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = "red",
         xlab = "Degrees", ylab = "Density", xlim = c(0, 360), ylim = c(0, 0.03))
  } else {
    estimacion_densidad <- density(emotion_spanish, bw = band)
    normalized_densities <- estimacion_densidad$y / max(estimacion_densidad$y)
    print(emotion)
    print(colores[t])
    lines(estimacion_densidad$x, estimacion_densidad$y, type = "l", lwd = 2, lty = 1, col = colores[t])
  }
  t = t+1
  
  
  

}

legend("topright", legend = c("fea", "hap", "cal", "sle", "dis", "sur", "exc", "bor", "ang", "sad"), col = colores, lty = 1, lwd = 2, bg = "transparent")
dev.off()

