library(readxl)

pdf("sweden/sweden_set1_barplot.pdf", width = 6, height = 8)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/sweden/words_analysis_sweden.xlsx", 
                                    sheet = "Set 1")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg = words_analysis_sweden$Label, las = 2,ylim = c(-50, 50))
dev.off()


pdf("sweden/sweden_set2_barplot.pdf", width = 6, height = 8)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/sweden/words_analysis_sweden.xlsx", 
                                    sheet = "Set 2")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg= words_analysis_sweden$Label,las=2,ylim = c(-50, 50))
dev.off()

pdf("sweden/sweden_set3_barplot.pdf", width = 6, height = 8)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/sweden/words_analysis_sweden.xlsx", 
                                    sheet = "Set 3")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg= words_analysis_sweden$Label,las=2,ylim = c(-50, 50))
dev.off()

pdf("sweden/sweden_set4_barplot.pdf", width = 6, height = 8)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/sweden/words_analysis_sweden.xlsx", 
                                    sheet = "Set 4")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg= words_analysis_sweden$Label,las=2,ylim = c(-50, 50))
dev.off()
getwd()


library(readxl)

pdf("portugal/set1_barplot.pdf")
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/portugal/words_analysis.xlsx", 
                                    sheet = "Set 1")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg = words_analysis_sweden$Label, las = 2,ylim = c(-50, 50),cex.lab = 1.2)
dev.off()

pdf("portugal/set2_barplot.pdf",width = 5, height = 5)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/portugal/words_analysis.xlsx", 
                                    sheet = "Set 2")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg = words_analysis_sweden$Label, las = 2,ylim = c(-50, 50))
dev.off()

pdf("portugal/set3_barplot.pdf", width = 5, height = 5)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/portugal/words_analysis.xlsx", 
                                    sheet = "Set 3")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg = words_analysis_sweden$Label, las = 2,ylim = c(-50, 50),cex.lab = 4)
dev.off()

pdf("portugal/set4_barplot.pdf", width = 5, height = 5)
par(mar = c(8, 6, 4, 2))  # Ajustar los márgenes para evitar que las etiquetas se corten
words_analysis_sweden <- read_excel("C:/Users/jordi/Downloads/Emotion_experiment/Emotion_experiment/portugal/words_analysis.xlsx", 
                                    sheet = "Set 4")
barplot(words_analysis_sweden$`Degree of acceptance`, names.arg = words_analysis_sweden$Label, las = 2,ylim = c(-50, 50))
dev.off()