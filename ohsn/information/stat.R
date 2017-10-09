install.packages("latex2exp")

library(ggplot2)
library(reshape)
library(stargazer)
library(sm)
library(poweRlaw)
library(latex2exp)

# Reference http://shinyapps.org/apps/RGraphCompendium/index.php
# Font: https://cran.r-project.org/web/packages/svglite/vignettes/fonts.html 

#----------------------data--------------------
filepath = '/home/wt/Code/ohsn/ohsn/information/data/fed-tweet.csv'
filepath = '/home/wt/Code/ohsn/ohsn/information/data/yg-sample.csv'
alldata <-  read.csv(filepath, sep = "\t")
data <- alldata
which(data$rtc == -1)
data <- data[data$rtc > -1,]
data <- data[data$fvc > -1,]
data['dif'] <- data$fvc - data$rtc

ed <- data
yg <- data

# long = melt(data, 'tid', method)

stargazer(data)

cor.test(data$fvc, data$rtc)

#----------------------function--------------------------------
powerlaw <- function(d, xlab){
  m1 = displ$new(d)
  est = estimate_xmin(m1)
  m1$setXmin(est)
  plot(m1, ylab="CDF", xlab=xlab)
  lines(m1, lty=2)
}


#------------------plot distribution-------------------------------
par(mfrow=c(2,1))
hist(data$rtc, breaks = max(data$rtc)+1)
plot(density(data$rtc), log='xy')
hist(data$fvc, breaks = max(data$fvc)+1)
plot(density(data$fvc), log='xy')

hist(ed$dif, breaks = max(ed$dif), xlim=c(-10, 10))
hist(yg$dif, breaks = max(yg$dif), xlim=c(-10, 10))
plot(density(ed$dif))
plot(density(yg$dif))


ggplot(yg,aes(x=rtc,y=fvc)) + geom_bin2d(bins=100)
ggcorrplot(ed,aes(x=rtc,y=fvc))

ggplot(long, aes(x=value+1, colour=variable)) + geom_density() + scale_x_continuous(trans='log10') + scale_y_continuous(trans='log10') 
ggplot(long, aes(x=value+1, colour=variable)) + geom_histogram(binwidth=.1, alpha=.5, position="identity") 
+ scale_x_continuous(trans='log10') + scale_y_continuous(trans='log10') 


sm.density.compare(long$value, long$variable)
legend("topright", levels(long$variable), fill=2+(0:nlevels(long$variable)))



#-----------------power law----------------
data = yg
m_na = displ$new(data$rtc+1)
m_us = displ$new(data$fvc+1)
# est_na = estimate_xmin(m_na)
# est_us = estimate_xmin(m_us)
# m_na$setXmin(est_na)
# m_us$setXmin(est_us)

par(mar=c(5,6,3,1)+.1, font = 2, family = "serif", font.lab =4, font.axis=2.5)
plot(m_na, ylab=TeX('CDF'), xlab=TeX('$k_{t}$'), col=4, cex.lab=2, cex.axis = 1.5)
# lines(m_na, lwd=3, col=4)
## Don t create a new plot, just store the output
d = plot(m_us, draw=FALSE)
points(d$x, d$y, col=2, pch=2)
# lines(m_us, col=2, type="l", lty=2, lwd=3)
legend("topright", c('RT','Like'), 
       lty=c(NA,NA), # gives the legend appropriate symbols (lines)
       pch=c(1,2),
       col=c(4,2), lwd=c(3,3), cex=2, bty = "n") # gives the legend lines the correct color and width



#------------------user stat---------------------
a = aggregate(rtc ~ uid, yg, mean)
b = aggregate(fvc ~ uid, yg, mean)

stargazer(b)

m_na = conpl$new(a$rtc+1)
m_us = conpl$new(b$fvc+1)


plot(m_na, ylab=TeX('$CDF$'), xlab=TeX('$\\bar{k_{u}}$'), col=4, cex.lab=2, cex.axis = 1.5)
# lines(m_na, lwd=3, col=4)
## Don t create a new plot, just store the output
d = plot(m_us, draw=FALSE)
points(d$x, d$y, col=2)
# lines(m_us, col=2, type="l", lty=2, lwd=3)
legend("topright", c('RT','Like'), 
       lty=c(NA,NA), # gives the legend appropriate symbols (lines)
       pch=c(1,2),
       col=c(4,2), lwd=c(3,3), cex=2, bty = "n") # gives the legend lines the correct color and width



a = aggregate(dif ~ uid, ed, mean)
b = aggregate(dif ~ uid, yg, mean)

hist(yg$dif, main = "", xlab = TeX('$c_{like} - c_{RT}$') , ylab = TeX('N_t'), cex.lab=3.5, cex.axis = 2)
hist(b$dif, main = "", xlab = TeX('$\\bar{c_{like} - c_{RT}}$') , ylab = TeX('N_u'), cex.lab=3.5, cex.axis = 2)

plot(density(a$dif))
plot(density(b$dif))

#--------------test power law
data("moby", package="poweRlaw")
m_pl = displ$new(moby)
est = estimate_xmin(m_pl)
m_pl$setXmin(est)



#------------------date ---------------------
dates <- as.Date(yg$date)
hist(dates, "months", format = "%b %y", freq=TRUE)


