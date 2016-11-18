if(FALSE){
install.packages('igraph')
install.packages('network')
install.packages('sna')
install.packages('ndtv')
install.packages('visNetwork')
install.packages('RColorBrewer')
install.packages("poweRlaw")
}

# library("tcltk") 
# library('RColorBrewer')
library('igraph')
library("poweRlaw")

#-----------------------------------------------------------------------------------------
# Load Network
net <- read.graph(file="/home/wt/Code/ohsn/ohsn/event/ed_tag.graphml", format="graphml")
net
nodes <- V(net)
links <- E(net)
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# attribute distribution
d = links$weight

min(d)
max(d)
den = density(d)
plot(den, xlab=expression(s[ij]), ylab='PDF', main='')

# den <- density(log(d))
# den$x <- exp(den$x)
# plot(den, log="x", col=2)
d = round(d)
dmin = min(d)-1
d = d-dmin
min(d)

xl = 'Link Weight'
m1 = displ$new(d)
m1$setXmin(estimate_xmin(m1))

m2 = dislnorm$new(d)
m2$setXmin(m1$getXmin())
m2$setPars(estimate_pars(m2))

plot(m2, ylab="CDF", xlab=xl)
lines(m1, lty=2)
# lines(m2, col=2, lty=2)
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
#Plot network
V(net)$size <- log(V(net)$weight)
V(net)$frame.color <- "white"
V(net)$color <- "tomato"
V(net)$label <- ''
V(net)$label[V(net)$weight>2500] <- V(net)$name[V(net)$weight>2500] 
V(net)$label.color <- 'black'
E(net)$width <- log(E(net)$weight)
E(net)$arrow.mode <- 0
plot(net, layout=layout_with_fr) #layout_with_fr NEVER use layout_with_kk, too slow


# Giant component
net.components <- clusters(net, mode='weak')
den = density(net.components$csize)
plot(den, xlab=expression('|c[i]|'), ylab='PDF', main='')

ix <- which.max(net.components$csize)
net.giant <- induced.subgraph(net, which(net.components$membership == ix))
V(net.giant)$size <- log(V(net.giant)$weight)
V(net.giant)$frame.color <- "white"
V(net.giant)$color <- "tomato"
V(net.giant)$label <- ''
# V(net.giant)$label[V(net.giant)$weight>2500] <- V(net.giant)$name[V(net.giant)$weight>2500]
# V(net.giant)$label.color <- 'black'
E(net.giant)$width <- log(E(net.giant)$weight)
E(net.giant)$arrow.mode <- 0
plot(net.giant, layout=layout_with_fr) #layout_with_fr layout_with_kk

#-----------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------
#Cut-off edges whose weights less than threshold
cut.off <- mean(links$weight) 
net.sp <- delete_edges(net, E(net)[weight<cut.off])
V(net.sp)$size <- log(V(net)$weight)
V(net.sp)$frame.color <- "white"
V(net.sp)$color <- "tomato"
V(net.sp)$label <- ''
E(net.sp)$width <- log(E(net)$weight)
E(net.sp)$arrow.mode <- 0
plot(net.sp, layout=layout_with_fr) #layout_with_fr layout_with_kk
#-----------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------
# K-core
kc <- coreness(net, mode="all")
colrs <- adjustcolor( c("gray50", "tomato", "gold", "yellowgreen"), alpha=.6)
plot(net, vertex.size=kc*6, vertex.label=kc, vertex.color=colrs[kc], layout=layout_with_fr)
#-----------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------
#Community detection
#http://stackoverflow.com/questions/33005510/algorithm-of-community-edge-betweenness-in-python-igraph-implementation for communtiy detection in directed graph 
net = net.giant
ceb <- cluster_infomap(net, e.weights=E(net)$weight, v.weights=V(net)$weight) # setting v.weights=NULL has no difference
# ceb = cluster_louvain(net, weights = E(net)$weight)
# dendPlot(ceb, mode="hclust")
# plot(ceb, net, mark.groups = NULL)

layout.modular <- function(G,c){
  G$layout <- layout_with_fr(G)
  nm <- length(levels(as.factor(c$membership)))
  gr <- 2
  while(gr^2<nm){
    gr <- gr+1
  }
  i <- j <- 0
  for(cc in levels(as.factor(c$membership))){
    F <- delete.vertices(G,c$membership!=cc)
    F$layout <- layout_with_fr(F)
    F$layout <- layout.norm(F$layout, i,i+2,j,j+2)
    G$layout[c$membership==cc,] <- F$layout
    if(i==gr){
      i <- 0
      if(j==gr){
        j <- 0
      }else{
        j <- j+1
      }
    }else{
      i <- i+1
    }
  }
  return(G$layout)
}

G = net
c = ceb
G$layout <- layout.modular(G,c)
V(G)$color <- rainbow(length(levels(as.factor(c$membership))))[c$membership]
V(G)$label[V(G)$weight>1000] <- V(G)$name[V(G)$weight>1000]
V(G)$label.color <- 'black'
plot(G)

sizes(c)
plot(sizes(c), xlab='c', ylab='size(c)')
plot(density(sizes(c)))
hist(sizes(c))
which.max(sizes(c))
for(cc in levels(as.factor(c$membership))){
  F <- delete.vertices(G,c$membership!=4)
  V(F)$label[V(F)$weight>100] <- V(F)$name[V(F)$weight>100]
  V(F)$size <- log(V(F)$weight)*2
  # V(F)$label.color <- 'red'
  plot(F, layout=layout_with_fr)
``}


#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
#Test Community detection methods
wc = cluster_edge_betweenness(net)
modularity(wc)
# wc = cluster_fast_greedy(net)
# modularity(wc)
wc = cluster_label_prop(net)
modularity(wc)
wc = cluster_leading_eigen(net)
modularity(wc)
wc = cluster_louvain(net)
modularity(wc)
# wc = cluster_spinglass(net)
# modularity(wc)
wc = cluster_walktrap(net)
modularity(wc)
#-----------------------------------------------------------------------------------------
