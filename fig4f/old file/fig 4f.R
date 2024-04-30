suppressPackageStartupMessages(library(ComplexHeatmap))
library(cluster)
suppressPackageStartupMessages(library(dendextend))
suppressPackageStartupMessages(library(circlize))


col_fun = colorRamp2(c(0,2000), c("white","red"))
# col_fun = colorRamp2(c(0,1000, 2000), c( "white","yellow", "red"))
col_fun(seq(-2, 2))

dfdata = read.table("To_ZI_neurons_0304_top100.csv",row.names = "X",header = TRUE,sep = ",")
dfcol = read.table("To_ZI_neurons_plots_0304.csv",row.names = "X",header = TRUE,sep = ",")

dfdist = read.table("new_score_matrix.csv",row.names = "X",header = TRUE,sep = ",")
d = as.dist(dfdist)
dend_rows = as.dendrogram(hclust(d,"ward.D2"))

pdf("heatmap53.pdf", width = 27, height = 16)
ht = Heatmap(t(dfdata),col = col_fun,cluster_columns = dend_rows,
             column_split = 5,show_column_names = FALSE,
             row_split = t(dfcol),row_gap = unit(0.8, "mm"),
             column_gap = unit(0.8, "mm"),border = TRUE,
             cluster_rows = FALSE)
draw(ht)
dev.off()

