if(FALSE){
  install.packages('igraph')
  install.packages('network')
  install.packages('sna')
  install.packages('ndtv')
  install.packages('visNetwork')
  install.packages('RColorBrewer')
  install.packages("poweRlaw")
  install.packages("linkcomm")
}

# library("tcltk") 
# library('RColorBrewer')
library('igraph')
library("poweRlaw")
library("linkcomm")
library("visNetwork")

#-----------------------------------------------------------------------
net_stat <- function(g){
  summary(g)
  cat(sprintf('#Nodes: %s\n', length(V(g))))
  cat(sprintf('#Edges: %s\n', length(E(g))))
  cat(sprintf('Density: %.3f\n', edge_density(g)))
  # cat(sprintf('Path: %.3f\n', mean_distance(g)))
  components <- clusters(g, mode='weak')
  gc <- induced.subgraph(g, which(components$membership == which.max(components$csize)))
  cat(sprintf('#Components: %s\n', clusters(g)$no))
  cat(sprintf('Giant Components Ratio: %.3f\n', length(V(gc))/length(V(g))))
  cat(sprintf('Global cluster coefficient: %.3f\n', transitivity(g, type="global")))
  cat(sprintf('Reciprocity: %.3f\n', reciprocity(g)))
  cat(sprintf('Assortativity: %.3f\n', assortativity_degree(g)))
}

plot_net <- function(net){
  V(net)$size <- log(V(net)$weight)
  V(net)$frame.color <- "white"
  V(net)$color <- "tomato"
  V(net)$label <- ''
  V(net)$label[V(net)$weight>2500] <- V(net)$name[V(net)$weight>2500] 
  V(net)$label.color <- 'black'
  E(net)$width <- log(E(net)$weight)
  E(net)$arrow.mode <- 0
  plot(net, layout=layout_with_kk) #layout_with_fr NEVER use layout_with_kk, too slow
  
  # deg <- degree(net, mode="all")
  # V(net)$size <- log(1+deg)
  # V(net)$frame.color <- "white"
  # V(net)$color[V(net)$cluster>0] <- "lightsteelblue2"
  # V(net)$color[V(net)$cluster<=0] <- "tomato"
  # V(net)$label <- ''
  # V(net)$label.color <- 'black'
  # E(net)$width <- E(net)$weight
  # E(net)$arrow.mode <- 0
  # plot(net, layout=layout_with_fr) #layout_with_fr NEVER use layout_with_kk, too slow
}

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
    G$layout[c$membership==cc] <- F$layout
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

plot.community <- function(net, c){
  V(net)$c <- c$membership
  net <- subgraph.edges(net, E(net)[weight>0.3], delete.vertices = TRUE)
  net_stat(net)
  V(net)$size <- log(V(net)$weight)
  V(net)$frame.color <- "white"
  V(net)$label.color <- 'black'
  E(net)$width <- log(E(net)$weight)
  E(net)$arrow.mode <- 0
  
  net$layout <- layout_with_kk(net)
  # nm <- length(levels(as.factor(V(net)$c)))
  # nm
  # gr <- 2
  # while(gr^2<nm){
  #   gr <- gr+1
  # }
  # i <- j <- 0
  # for(cc in unique(V(net)$c)){
  #   F <- delete.vertices(net, V(net)[c=cc])
  #   F$layout <- layout_with_fr(F)
  #   F$layout <- layout.norm(F$layout, i,i+2,j,j+2)
  #   net$layout[V(net)[c=cc]] <- F$layout
  #   if(i==gr){
  #     i <- 0
  #     if(j==gr){
  #       j <- 0
  #     }else{
  #       j <- j+1
  #     }
  #   }else{
  #     i <- i+1
  #   }
  # }
  V(net)$label <- ''
  V(net)$color <- rainbow(length(levels(as.factor(V(net)$c))))[V(net)$c]
  plot(net)
}

giant_comp <- function(net){
  components <- clusters(net, mode='weak')
  den = density(components$csize)
  # hist(net.components$csize, xlab=expression('|c[i]|'), ylab='PDF', main='')
  plot(den, xlab=expression('|c[i]|'), ylab='PDF', main='')
  ix <- which.max(components$csize)
  giant <- induced.subgraph(net, which(components$membership == ix))
  return(giant)
}

pdf <- function(d){
  min(d)
  max(d)
  den = density(d)
  plot(den, xlab=expression(s[ij]), ylab='PDF', main='')
}

powerlaw <- function(d, xlab){
  # min(d)
  # max(d)
  # # den <- density(log(d))
  # # den$x <- exp(den$x)
  # # plot(den, log="x", col=2)
  # d = round(d)
  # dmin = min(d)-1
  # d = d-dmin
  # min(d)
  
  # xl = 'Node Weight'
  m1 = displ$new(d)
  m1$setXmin(estimate_xmin(m1))
  
  m2 = dislnorm$new(d)
  m2$setXmin(m1$getXmin())
  m2$setPars(estimate_pars(m2))
  
  plot(m2, ylab="CDF", xlab=xlab)
  lines(m1, lty=2)
  # lines(m2, col=2, lty=2)
}

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Load Network
g <- read.graph(file="/home/wt/Code/ohsn/ohsn/event/ed_tag_undir.graphml", format="graphml")
# net <- read.graph(file="/home/wt/Code/ohsn/ohsn/event/ed_weighted_follow.graphml", format="graphml")
# net <- read.graph(file="/home/wt/Code/ohsn/ohsn/edrelated/pro-ed-rec-mention.graphml", format="graphml")
# g <- read.graph(file="/Users/tw/Dropbox/share/ed_tag.graphml", format="graphml")
# net <- read.graph(file="/home/wt/Code/ohsn/ohsn/event/ed_follow_cluster.graphml", format="graphml")
# write_graph(g, file="/home/wt/Code/ohsn/ohsn/event/ed_tag.pajek", format = "pajek")
g

snet <- subgraph.edges(g, E(g)[weight>50], delete.vertices = TRUE)
nodes <- V(snet)
links <- E(snet)

nodes <- data.frame(id = 1:3)
edges <- data.frame(from = c(1,2), to = c(1,3))

visNetwork(nodes, edges)

#-----------------------------------------------------------------------------------------
# attribute distribution
pdf(V(g)$weight)
powerlaw(V(g)$weight, 'Node Weight')



#-----------------------------------------------------------------------------------------
# Trim network
snet <- delete.vertices(g, V(g)[V(g)[weight<0]])
snet <- subgraph.edges(g, E(g)[weight>0.3], delete.vertices = TRUE)
net_stat(snet)

#-----------------------------------------------------------------------------------------
#Plot network
plot_net(snet)



#-----------------------------------------------------------------------------------------
# Giant component
net.giant = giant_comp(snet)
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
net = g
ceb <- cluster_infomap(net, e.weights=E(net)$weight, v.weights=V(net)$weight) # setting v.weights=NULL has no difference
ceb = cluster_louvain(net, weights = E(net)$weight)
# dendPlot(ceb, mode="hclust")
# plot(ceb, net, mark.groups = NULL)

nodes <-  cbind(V(g)$name, as.numeric(V(g)$weight))
edges <- cbind( get.edgelist(g) , round( E(g)$weight, 3 ))

lc <- getLinkCommunities(edges, hcmethod = "single")
print(lc)

G = net
c = ceb
G$layout <- layout.modular(G,c)
V(G)$color <- rainbow(length(levels(as.factor(c$membership))))[c$membership]
V(G)$label[V(G)$weight>1000] <- V(G)$name[V(G)$weight>1000]
V(G)$label.color <- 'black'
plot(G)

length(sizes(c)[sizes(c)>5])
plot(sizes(c), xlab='c', ylab='size(c)')
plot(density(sizes(c)[sizes(c)<30]))
hist(sizes(c))
which.max(sizes(c))
for(cc in levels(as.factor(c$membership))){
  # F <- delete.vertices(G,c$membership!= 200)
  F <- delete.vertices(G,V(G)[ V(G)[cluster != 0] ])
  V(F)$label <- V(F)$name
  V(F)$label[V(F)$weight>100] <- V(F)$name[V(F)$weight>100]
  # V(F)$size <- log(V(F)$weight)*2
  # V(F)$label.color <- 'red'
  plot(F, layout=layout_with_fr)
  
}


#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
#Test Community detection methods
net = g
wc = cluster_edge_betweenness(net, weights=E(net)$weight)
modularity(wc)
# wc = cluster_fast_greedy(net)
# modularity(wc)
wc = cluster_label_prop(net, weights=E(net)$weight)
modularity(wc)
wc = cluster_leading_eigen(net, weights=E(net)$weight)
modularity(wc)
wc = cluster_louvain(net, weights=E(net)$weight)
modularity(wc)
# wc = cluster_spinglass(net)
# modularity(wc)
wc = cluster_walktrap(net, weights=E(net)$weight)
modularity(wc)

wc <- cluster_infomap(net, e.weights=E(net)$weight, v.weights=V(net)$weight) # setting v.weights=NULL has no difference
modularity(wc)
#-----------------------------------------------------------------------------------------
