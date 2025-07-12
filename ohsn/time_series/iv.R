install.packages('AER')
install.packages('lmtest')
install.packages("psych")

library(AER)
library(lmtest)
library(psych)

## data stat
data = read.csv('/home/wt/Code/ohsn/ohsn/time_series/data.csv')
summary(data)
length(which(data$attr==0))
length(which(data$attr==1))
describe(data)
cor(data)





data("CigarettesSW")
CigarettesSW
CigarettesSW$rprice <- with(CigarettesSW, price/cpi)
CigarettesSW$rincome <- with(CigarettesSW, income/population/cpi)
CigarettesSW$tdiff <- with(CigarettesSW, (taxs - tax)/cpi)

## model 
fm <- ivreg(log(packs) ~ log(rprice) + log(rincome) | log(rincome) + tdiff + I(tax/cpi),
            data = CigarettesSW, subset = year == "1995")
summary(fm)

## ANOVA
fm2 <- ivreg(log(packs) ~ log(rprice) | tdiff, data = CigarettesSW, subset = year == "1995")
anova(fm, fm2)
